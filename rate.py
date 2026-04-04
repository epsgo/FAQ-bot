import os
from datetime import datetime
import gspread
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db import get_user
from keyboards import auth_required
from const import TEXTS, MENU_BUTTONS

router = Router()

SPREADSHEET_ID = "1-wanGN5Q-tEutapXrOzqvg5EEzNUqlwLstyKcc1PiCk"

class FeedbackState(StatesGroup):
    waiting_for_rate = State()
    waiting_for_text = State()

def append_feedback_to_sheet(row):
    try:
        gc = gspread.service_account_from_dict({
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        })
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.get_worksheet(0) # Берем первый лист
        worksheet.append_row(row)
    except Exception as e:
        print(f"Excel Error: {e}")

def get_stars_kb():
    buttons = [
        [InlineKeyboardButton(text="⭐", callback_data="rate_1"),
         InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
         InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
         InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(lambda m: any(m.text == btns.get("btn_rate") for btns in MENU_BUTTONS.values()))
@auth_required
async def start_feedback(message: Message, state: FSMContext, user: dict):
    lang = user['language']
    await message.answer("How would you rate our onboarding bot? ⭐", reply_markup=get_stars_kb())
    await state.set_state(FeedbackState.waiting_for_rate)

@router.callback_query(FeedbackState.waiting_for_rate, F.data.startswith("rate_"))
async def process_rate(callback: CallbackQuery, state: FSMContext):
    rating = callback.data.split("_")[1]
    await state.update_data(stars=rating)
    
    await callback.message.edit_text("What exactly should we add, change, or remove to make your experience better?")
    await state.set_state(FeedbackState.waiting_for_text)
    await callback.answer()

@router.message(FeedbackState.waiting_for_text)
@auth_required
async def process_feedback_text(message: Message, state: FSMContext, user: dict):
    data = await state.get_data()
    stars = data.get("stars")
    comment = message.text
    
    row = [
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        str(message.from_user.id),
        user.get("full_name", "Unknown"),
        stars,
        comment
    ]
    
    append_feedback_to_sheet(row)
    
    await state.clear()
    await message.answer("Thank you! Your feedback has been sent to our team. 🚀")