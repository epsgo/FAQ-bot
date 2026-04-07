from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import aiohttp
import os
from datetime import datetime
from db import get_user, update_language, update_full_name, update_birthdate
from const import PROFILE_BTNS, TEXTS, ADMIN_IDS, DISCORD_WEBHOOK
from keyboards import auth_required, get_main_menu

NDA_FILE_PATH = "nda_contract.pdf"
router = Router()


class ProfileEditState(StatesGroup):
    editing_name = State()
    editing_birthdate = State()


def get_profile_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["edit_info"], callback_data="edit_profile")],
        [InlineKeyboardButton(text=TEXTS[lang]["signNDA"], callback_data="signNDA")]
    ])


def get_profile_text(user, lang):
    birthdate = datetime.fromisoformat(user['birthdate']).strftime("%d.%m.%Y") if user.get('birthdate') else "—"
    created_at = datetime.fromisoformat(user['created_at']).strftime("%d.%m.%Y")

    LANG_DISPLAY = {"ru": "Русский", "ua": "Українська", "en": "English"}
    LANG_FLAGS = {"ru": "🌐", "ua": "🇺🇦", "en": "🇺🇸"}

    current_flag = LANG_FLAGS.get(user['language'], "🌐")

    return (
        f"👤 <b>{TEXTS[lang]['change_name']}:</b> {user['full_name']}\n"
        f"{current_flag} <b>{TEXTS[lang]['lang']}:</b> {LANG_DISPLAY.get(user['language'], '—')}\n"
        f"🎂 <b>{TEXTS[lang]['birthdate']}:</b> {birthdate}\n"
        f"🗓 <b>{TEXTS[lang]['registrationdate']}:</b> {created_at}\n"
    )


@router.message(F.text.in_(PROFILE_BTNS))
@auth_required
async def show_profile(message: Message, user: dict):
    lang = user['language']
    await message.answer(get_profile_text(user, lang), reply_markup=get_profile_kb(lang), parse_mode="HTML")


@router.callback_query(F.data == "edit_profile")
async def edit_profile_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["change_lang"], callback_data="edit_lang")],
        [InlineKeyboardButton(text=TEXTS[lang]["change_name"], callback_data="edit_name")],
        [InlineKeyboardButton(text=TEXTS[lang]["change_birthdate"], callback_data="edit_birthdate")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_profile")]
    ])

    await callback.message.edit_text(TEXTS[lang]["choose_info"], reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']
    await callback.message.edit_text(get_profile_text(user, lang), reply_markup=get_profile_kb(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "edit_lang")
async def profile_edit_lang(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text="Українська", callback_data="set_lang_ua")],
        [InlineKeyboardButton(text="English", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="edit_profile")]
    ])
    await callback.message.edit_text(TEXTS[lang]["choose_lang"], reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    new_lang = callback.data.split("_")[-1]
    update_language(user_id, new_lang)

    is_admin = user_id in ADMIN_IDS
    await callback.message.answer(
        TEXTS[new_lang]["lang_changed"],
        reply_markup=get_main_menu(new_lang, is_admin=is_admin)
    )
    updated_user = get_user(user_id)
    await callback.message.answer(
        get_profile_text(updated_user, new_lang),
        reply_markup=get_profile_kb(new_lang),
        parse_mode="HTML"
    )
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "signNDA")
async def send_nda_instruction(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']

    if not os.path.exists(NDA_FILE_PATH):
        await callback.answer("File not found", show_alert=True)
        return

    await callback.message.answer_document(
        FSInputFile(NDA_FILE_PATH),
        caption=TEXTS[lang].get("nda", "signNDA")
    )
    await callback.answer()


@router.message(F.document)
@auth_required
async def handle_any_document(message: Message, user: dict):
    if not DISCORD_WEBHOOK:
        await message.answer("Error: webhook not configured")
        return

    document = message.document
    lang = user['language']
    file_info = await message.bot.get_file(document.file_id)
    file_content = await message.bot.download_file(file_info.file_path)

    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("content", f"NDA от: {user['full_name']}")
            form.add_field(
                "file",
                file_content.getvalue(),
                filename=document.file_name,
                content_type="application/octet-stream"
            )
            async with session.post(DISCORD_WEBHOOK, data=form) as response:
                if response.status in [200, 204]:
                    await message.answer(TEXTS[lang].get("filesent", "File sent successfully 🚀"))
                else:
                    await message.answer("Error")
    except Exception:
        await message.answer("Error")


@router.callback_query(F.data == "edit_name")
async def edit_name(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']
    await state.set_state(ProfileEditState.editing_name)
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await callback.answer()


@router.callback_query(F.data == "edit_birthdate")
async def edit_birthdate(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    if not user or not user.get("is_approved"):
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    lang = user['language']
    await state.set_state(ProfileEditState.editing_birthdate)
    await callback.message.answer(TEXTS[lang]["ask_birth"])
    await callback.answer()


@router.message(ProfileEditState.editing_name)
@auth_required
async def handle_edit_name(message: Message, state: FSMContext, user: dict):
    lang = user['language']
    if not message.text:
        await message.answer(TEXTS[lang]["ask_name"])
        return

    update_full_name(message.from_user.id, message.text)
    await state.clear()
    await message.answer(TEXTS[lang]["name_changed"])
    await message.answer(
        get_profile_text(get_user(message.from_user.id), lang),
        reply_markup=get_profile_kb(lang),
        parse_mode="HTML"
    )


@router.message(ProfileEditState.editing_birthdate)
@auth_required
async def handle_edit_birthdate(message: Message, state: FSMContext, user: dict):
    lang = user['language']
    if not message.text:
        await message.answer(TEXTS[lang]["ask_birth"])
        return

    try:
        birth = datetime.strptime(message.text, "%d.%m.%Y").date()
        update_birthdate(message.from_user.id, birth.isoformat())
        await state.clear()
        await message.answer(TEXTS[lang]["birth_changed"])
        await message.answer(
            get_profile_text(get_user(message.from_user.id), lang),
            reply_markup=get_profile_kb(lang),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(TEXTS[lang]["ask_birth"])
