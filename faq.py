import asyncio
import json
import os
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from const import FAQ_BTNS, TEXTS, NDA_INSTRUCTION
from keyboards import auth_required

router = Router()

FAQ_DELETE_DELAY = 12 * 60 * 60
# (chat_id, text_msg_id) -> [photo_msg_id, ...]  — для удаления фото при нажатии Back
_pending_photo_deletions: dict[tuple, list[int]] = {}

with open("faq_data.json", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)["categories"]


async def delete_after(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass

def schedule_delete(message: Message):
    asyncio.create_task(delete_after(message, FAQ_DELETE_DELAY))


def get_categories_kb(lang: str) -> InlineKeyboardMarkup:
    buttons = []
    for i, cat in enumerate(FAQ_DATA):
        buttons.append([InlineKeyboardButton(
            text=f"{cat['icon']} {cat['titles'][lang]}",
            callback_data=f"faq_c_{i}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_questions_kb(cat_idx: int, lang: str) -> InlineKeyboardMarkup:
    cat = FAQ_DATA[cat_idx]
    buttons = []
    for q_idx, q in enumerate(cat["questions"]):
        buttons.append([InlineKeyboardButton(
            text=q["q"][lang],
            callback_data=f"faq_q_{cat_idx}_{q_idx}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="faq_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text.in_(FAQ_BTNS))
@auth_required
async def show_faq_menu(message: Message, user: dict):
    lang = user["language"]
    sent = await message.answer(TEXTS[lang]["faq_title"], reply_markup=get_categories_kb(lang))
    schedule_delete(sent)


@router.callback_query(F.data == "faq_menu")
async def faq_menu_callback(callback: CallbackQuery):
    from db import get_user
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user["language"]
    await callback.message.edit_text(TEXTS[lang]["faq_title"], reply_markup=get_categories_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("faq_c_"))
async def show_category(callback: CallbackQuery):
    from db import get_user
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    cat_idx = int(callback.data.split("_")[-1])
    lang = user["language"]
    cat = FAQ_DATA[cat_idx]
    title = f"{cat['icon']} {cat['titles'][lang]}"

    # Удалить фото-сообщения, если они были отправлены отдельно от текста
    key = (callback.message.chat.id, callback.message.message_id)
    for photo_id in _pending_photo_deletions.pop(key, []):
        try:
            await callback.bot.delete_message(callback.message.chat.id, photo_id)
        except Exception:
            pass

    if callback.message.photo:
        await callback.message.delete()
        sent = await callback.message.answer(title, reply_markup=get_questions_kb(cat_idx, lang))
        schedule_delete(sent)
    else:
        await callback.message.edit_text(title, reply_markup=get_questions_kb(cat_idx, lang))

    await callback.answer()


@router.callback_query(F.data.startswith("faq_q_"))
async def show_answer(callback: CallbackQuery):
    from db import get_user
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    _, _, cat_idx, q_idx = callback.data.split("_")
    cat_idx, q_idx = int(cat_idx), int(q_idx)
    lang = user["language"]
    q = FAQ_DATA[cat_idx]["questions"][q_idx]

    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"faq_c_{cat_idx}")]
    ])

    answer_text = q['a'][lang]

    if answer_text == "::NDA_INSTRUCTION::":
        answer_text = NDA_INSTRUCTION[lang]

    if "![" in answer_text and "](" in answer_text:
        image_pattern = r'!\[.*?\]\((.*?)\)'
        image_paths = re.findall(image_pattern, answer_text)
        text_without_images = re.sub(image_pattern, '', answer_text).strip()
        existing_images = [path for path in image_paths if os.path.exists(path)]

        if existing_images:
            await callback.message.delete()

            full_text = f"<b>{q['q'][lang]}</b>\n\n{text_without_images}"

            if len(existing_images) == 1:
                if len(full_text) <= 1024:
                    # Одно сообщение: фото + подпись + кнопка
                    sent = await callback.message.answer_photo(
                        photo=FSInputFile(existing_images[0]),
                        caption=full_text,
                        parse_mode="HTML",
                        reply_markup=back_kb
                    )
                    schedule_delete(sent)
                else:
                    # Фото отдельно, длинный текст отдельно
                    sent_photo = await callback.message.answer_photo(photo=FSInputFile(existing_images[0]))
                    schedule_delete(sent_photo)
                    sent_text = await callback.message.answer(full_text[:4096], reply_markup=back_kb, parse_mode="HTML")
                    schedule_delete(sent_text)
                    _pending_photo_deletions[(callback.message.chat.id, sent_text.message_id)] = [sent_photo.message_id]
            else:
                # Несколько фото — отправить как медиагруппу
                media = [InputMediaPhoto(media=FSInputFile(p)) for p in existing_images]
                sent_messages = await callback.message.answer_media_group(media=media)
                for sent in sent_messages:
                    schedule_delete(sent)
                photo_ids = [s.message_id for s in sent_messages]

                # Текст + кнопка отдельным сообщением
                if len(full_text) > 4096:
                    chunks = []
                    current_chunk = f"<b>{q['q'][lang]}</b>\n\n"
                    for para in text_without_images.split('\n\n'):
                        if len(current_chunk) + len(para) + 2 < 4096:
                            current_chunk += para + "\n\n"
                        else:
                            chunks.append(current_chunk.strip())
                            current_chunk = para + "\n\n"
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    for chunk in chunks[:-1]:
                        sent = await callback.message.answer(chunk, parse_mode="HTML")
                        schedule_delete(sent)
                    sent_text = await callback.message.answer(chunks[-1], reply_markup=back_kb, parse_mode="HTML")
                    schedule_delete(sent_text)
                else:
                    sent_text = await callback.message.answer(full_text, reply_markup=back_kb, parse_mode="HTML")
                    schedule_delete(sent_text)
                _pending_photo_deletions[(callback.message.chat.id, sent_text.message_id)] = photo_ids
        else:
            await callback.message.edit_text(
                f"<b>{q['q'][lang]}</b>\n\n{text_without_images}",
                reply_markup=back_kb,
                parse_mode="HTML"
            )
    else:
        await callback.message.edit_text(
            f"<b>{q['q'][lang]}</b>\n\n{answer_text}",
            reply_markup=back_kb,
            parse_mode="HTML"
        )

    await callback.answer()
