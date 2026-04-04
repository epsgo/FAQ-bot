from aiogram import Router, F
from db import *
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from const import PROFILE_BTNS, TEXTS, ADMIN_IDS, DISCORD_WEBHOOK
from datetime import datetime
import os
import requests
from keyboards import auth_required, get_main_menu
NDA_FILE_PATH = "nda_contract.pdf" 
router = Router()
edit_state = {}

def get_profile_kb(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["edit_info"], callback_data="edit_profile")],
        [InlineKeyboardButton(text=TEXTS[lang]["signNDA"], callback_data="signNDA")]
    ])
    return kb

def get_profile_text(user, lang):
    birthdate = datetime.fromisoformat(user['birthdate']).strftime("%d.%m.%Y") if user.get('birthdate') else "—"
    created_at = datetime.fromisoformat(user['created_at']).strftime("%d.%m.%Y")
    
    LANG_DISPLAY = {"ru": "Русский", "ua": "Українська", "en": "English"}
    LANG_FLAGS = {"ru": "🇷🇺", "ua": "🇺🇦", "en": "🇺🇸"} 
    
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
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["edit_info"], callback_data="edit_profile")],
        [InlineKeyboardButton(text=TEXTS[lang]["signNDA"], callback_data="signNDA")]
    ])
    await message.answer(get_profile_text(user, lang), reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "edit_profile")
async def edit_profile_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
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
    lang = user['language']
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["edit_info"], callback_data="edit_profile")]
    ])
    await callback.message.edit_text(get_profile_text(user, lang), reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "edit_lang")
async def profile_edit_lang(callback: CallbackQuery):
    lang = get_user(callback.from_user.id)['language']
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
    new_lang = callback.data.split("_")[-1]
    update_language(user_id, new_lang)
    
    is_admin = user_id in ADMIN_IDS
    await callback.message.answer(
        TEXTS[new_lang]["lang_changed"],
        reply_markup=get_main_menu(new_lang, is_admin=is_admin)
    )
    user = get_user(user_id)
    await callback.message.answer(
        get_profile_text(user, new_lang),
        reply_markup=get_profile_kb(new_lang),
        parse_mode="HTML"
    )
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "signNDA")
async def send_nda_instruction(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user(user_id)['language']

    if not os.path.exists(NDA_FILE_PATH):
        return

    await callback.message.answer_document(
        FSInputFile(NDA_FILE_PATH),
        caption=TEXTS[lang].get("nda", "signNDA")
    )
    await callback.answer()

@router.message(F.document)
@auth_required
async def handle_any_document(message: Message, user: dict):
    document = message.document
    lang = user['language']
    file_info = await message.bot.get_file(document.file_id)
    file_content = await message.bot.download_file(file_info.file_path)

    try:
        files = {"file": (document.file_name, file_content.getvalue())}
        payload = {"content": f"NDA от: {user['full_name']}"}
        
        response = requests.post(DISCORD_WEBHOOK, data=payload, files=files)
        if response.status_code in [200, 204]:
            success_text = TEXTS[lang].get("filesent", "File sent successfully 🚀")
            await message.answer(success_text)
        else:
            await message.answer("Error")
        
    except Exception as e:
        await message.answer("Error")


@router.callback_query(F.data == "edit_name")
async def edit_name(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    lang = user['language']

    edit_state[callback.from_user.id] = "name"
    
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await callback.answer()


@router.callback_query(F.data == "edit_birthdate")
async def edit_birthdate(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    lang = user['language']

    edit_state[callback.from_user.id] = "birthdate"
    
    await callback.message.answer(TEXTS[lang]["ask_birth"])
    await callback.answer()


@router.message(lambda message: message.from_user.id in edit_state)
@auth_required
async def handle_edit(message: Message):
    user_id = message.from_user.id
    state = edit_state[user_id]
    user = get_user(user_id)
    lang = user['language']

    if state == "name":
        update_full_name(user_id, message.text)
        await message.answer(TEXTS[lang]["name_changed"])
    elif state == "birthdate":
        try:
            birth = datetime.strptime(message.text, "%d.%m.%Y").date()
            update_birthdate(user_id, birth.isoformat())
            await message.answer(TEXTS[lang]["birth_changed"])
        except ValueError:
            await message.answer(TEXTS[lang]["ask_birth"])
            return

    edit_state.pop(user_id)

    await message.answer(
        get_profile_text(get_user(user_id), lang),
        reply_markup=get_profile_kb(lang), 
        parse_mode="HTML"
    )