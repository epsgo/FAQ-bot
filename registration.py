from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from db import *
from const import TEXTS, ADMIN_IDS
from keyboards import get_main_menu

router = Router()
registration_state = {}

@router.message(CommandStart())
async def start(message: Message):
    user = get_user(message.from_user.id)
    
    if user:
        is_admin = message.from_user.id in ADMIN_IDS
        await message.answer(TEXTS[user['language']]['welcome_back'],
            reply_markup=get_main_menu(user['language'], is_admin=is_admin)
        )
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="Русский", callback_data="lang_ru")
    kb.button(text="Українська", callback_data="lang_ua")
    kb.button(text="English", callback_data="lang_en")
    kb.adjust(1)

    await message.answer("Choose your language:", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id

    registration_state[user_id] = {"language": lang}
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await callback.answer()

@router.message()
async def handle_messages(message: Message):
    user_id = message.from_user.id

    if user_id not in registration_state:
        return

    state = registration_state[user_id]
    lang = state["language"]

    if "full_name" not in state:
        state["full_name"] = message.text
        await message.answer(TEXTS[lang]["ask_birth"])
        return

    if "birthdate" not in state:
        try:
            birth = datetime.strptime(message.text, "%d.%m.%Y").date()
            add_user(user_id, state["full_name"], birth.isoformat(), lang)
            
            await message.answer(TEXTS[lang]["wait_approval"]) 
            
            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        admin_id, 
                        f"🔔 New registration request!\nFull name: {state['full_name']}\nID: {user_id}"
                    )
                except Exception:
                    continue
                
            registration_state.pop(user_id)
        except ValueError:
            await message.answer(TEXTS[lang]["ask_birth"])

