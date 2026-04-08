from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from db import get_user, add_user, approve_user
from const import TEXTS, ADMIN_IDS
from keyboards import get_main_menu

router = Router()


class RegistrationState(StatesGroup):
    waiting_name = State()
    waiting_birthdate = State()


@router.message(CommandStart())
@router.message(F.text == "Start Registration")
async def start(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)

    if user:
        user_id = message.from_user.id
        is_admin = user_id in ADMIN_IDS
        if is_admin and not user.get("is_approved"):
            approve_user(user_id)
            user["is_approved"] = True
        await message.answer(
            TEXTS[user['language']]['welcome_back'],
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
async def set_language(callback: CallbackQuery, state: FSMContext):
    if get_user(callback.from_user.id):
        await callback.answer()
        return

    lang = callback.data.split("_")[1]
    await state.set_state(RegistrationState.waiting_name)
    await state.update_data(language=lang)
    await callback.message.answer(TEXTS[lang]["ask_name"])
    await callback.answer()


@router.message(RegistrationState.waiting_name)
async def handle_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]

    if not message.text:
        await message.answer(TEXTS[lang]["ask_name"])
        return

    await state.update_data(full_name=message.text)
    await state.set_state(RegistrationState.waiting_birthdate)
    await message.answer(TEXTS[lang]["ask_birth"])


@router.message(RegistrationState.waiting_birthdate)
async def handle_birthdate(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]

    if not message.text:
        await message.answer(TEXTS[lang]["ask_birth"])
        return

    try:
        birth = datetime.strptime(message.text, "%d.%m.%Y").date()
        user_id = message.from_user.id
        add_user(user_id, data["full_name"], birth.isoformat(), lang)
        await state.clear()

        if user_id in ADMIN_IDS:
            approve_user(user_id)
            await message.answer(
                TEXTS[lang]["registered"],
                reply_markup=get_main_menu(lang, is_admin=True)
            )
        else:
            await message.answer(TEXTS[lang]["wait_approval"])

            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        admin_id,
                        f"🔔 New registration request!\nFull name: {data['full_name']}\nID: {user_id}"
                    )
                except Exception:
                    continue
    except ValueError:
        await message.answer(TEXTS[lang]["ask_birth"])
