from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ReplyKeyboardRemove

from functools import wraps
from db import get_user
from const import MENU_BUTTONS

def get_start_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Start Registration")]],
        resize_keyboard=True
    )


def get_main_menu(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    lang_btns = MENU_BUTTONS.get(lang, MENU_BUTTONS["en"])

    menu_layout = [
        "btn_profile", 
        "btn_faq", 
        "btn_test", 
        "btn_meeting", 
        "btn_rate"
    ]

    for key in menu_layout:
        builder.button(text=lang_btns[key])

    if is_admin:
        builder.button(text=lang_btns["btn_admin"])

    builder.adjust(2) 
    
    return builder.as_markup(resize_keyboard=True)

def auth_required(handler):
    @wraps(handler)
    async def wrapper(event, *args, **kwargs):
        user_id = event.from_user.id
        user = get_user(user_id)
        
        if not user:
            msg = "Please complete registration first using /start 😊"
            if isinstance(event, Message):
                await event.answer(msg, reply_markup=get_start_kb())
            elif isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            return

        if not user.get("is_approved", False):
            msg = "⏳ Thanks for registering! An administrator is reviewing your request. Please hang tight, you’ll be notified soon."
            if isinstance(event, Message):
                await event.answer(msg, reply_markup=get_start_kb())
            elif isinstance(event, CallbackQuery):
                await event.answer(msg, show_alert=True)
            return
        
        return await handler(event, user=user, *args, **kwargs)
        
    return wrapper