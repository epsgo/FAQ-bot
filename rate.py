import os
from datetime import datetime
import gspread
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db import get_user
from keyboards import auth_required
from const import MENU_BUTTONS, TEXTS

router = Router()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


class FeedbackState(StatesGroup):
    waiting_for_type = State()
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

        try:
            worksheet = sh.worksheet("Feedback")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title="Feedback", rows=1000, cols=6)

        values = worksheet.get_all_values()
        if not values or all(cell == "" for cell in values[0]):
            headers = ["Time", "User ID", "Name", "Type", "Stars", "Message"]
            worksheet.append_row(headers)

            col_widths = [150, 130, 250, 100, 100, 450]
            sheet_id = worksheet.id
            batch_requests = []

            for i, width in enumerate(col_widths):
                batch_requests.append({
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": i,
                            "endIndex": i + 1
                        },
                        "properties": {"pixelSize": width},
                        "fields": "pixelSize"
                    }
                })

            batch_requests.append({
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            })

            worksheet.spreadsheet.batch_update({"requests": batch_requests})

            worksheet.format("A1:F1", {
                "textFormat": {
                    "bold": True,
                },
                "horizontalAlignment": "CENTER"
            })
            worksheet.format("F2:F1000", {"wrapStrategy": "WRAP"})

        worksheet.append_row(row)

    except Exception as e:
        print(f"Excel Error: {e}")


def get_feedback_type_kb(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["rate_btn_rate"], callback_data="fb_rate")],
        [InlineKeyboardButton(text=t["rate_btn_bug"], callback_data="fb_bug")],
        [InlineKeyboardButton(text=t["rate_btn_idea"], callback_data="fb_idea")]
    ])


def get_stars_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⭐", callback_data="rate_1"),
            InlineKeyboardButton(text="⭐⭐", callback_data="rate_2"),
            InlineKeyboardButton(text="⭐⭐⭐", callback_data="rate_3"),
        ],
        [
            InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rate_4"),
            InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rate_5"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="fb_back")],
    ])


def get_text_input_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="fb_back")],
    ])


@router.message(lambda m: any(m.text == btns.get("btn_rate") for btns in MENU_BUTTONS.values()))
@auth_required
async def start_feedback(message: Message, state: FSMContext, user: dict):
    lang = user["language"]
    await message.answer(TEXTS[lang]["rate_choose_type"], reply_markup=get_feedback_type_kb(lang))
    await state.set_state(FeedbackState.waiting_for_type)


@router.callback_query(FeedbackState.waiting_for_type, F.data.in_({"fb_rate", "fb_bug", "fb_idea"}))
async def process_type(callback: CallbackQuery, state: FSMContext):
    lang = get_user(callback.from_user.id)["language"]
    fb_type = callback.data.split("_")[1]
    await state.update_data(type=fb_type)

    if fb_type == "rate":
        await callback.message.edit_text(TEXTS[lang]["rate_ask_stars"], reply_markup=get_stars_kb(lang))
        await state.set_state(FeedbackState.waiting_for_rate)
    elif fb_type == "bug":
        await callback.message.edit_text(TEXTS[lang]["rate_ask_text_bug"], reply_markup=get_text_input_kb(lang))
        await state.set_state(FeedbackState.waiting_for_text)
    elif fb_type == "idea":
        await callback.message.edit_text(TEXTS[lang]["rate_ask_text_idea"], reply_markup=get_text_input_kb(lang))
        await state.set_state(FeedbackState.waiting_for_text)

    await callback.answer()


@router.callback_query(FeedbackState.waiting_for_rate, F.data.startswith("rate_"))
async def process_rate(callback: CallbackQuery, state: FSMContext):
    lang = get_user(callback.from_user.id)["language"]
    rating = callback.data.split("_")[1]
    await state.update_data(stars=rating)

    text = TEXTS[lang]["rate_ask_good"] if int(rating) >= 4 else TEXTS[lang]["rate_ask_bad"]
    await callback.message.edit_text(text, reply_markup=get_text_input_kb(lang))
    await state.set_state(FeedbackState.waiting_for_text)
    await callback.answer()


@router.callback_query(F.data == "fb_back")
async def go_back_to_type(callback: CallbackQuery, state: FSMContext):
    lang = get_user(callback.from_user.id)["language"]
    await state.update_data(type=None, stars=None)
    await state.set_state(FeedbackState.waiting_for_type)
    await callback.message.edit_text(TEXTS[lang]["rate_choose_type"], reply_markup=get_feedback_type_kb(lang))
    await callback.answer()


@router.message(FeedbackState.waiting_for_text)
@auth_required
async def process_feedback_text(message: Message, state: FSMContext, user: dict):
    lang = user["language"]
    if not message.text:
        await message.answer(TEXTS[lang]["rate_text_only"])
        return

    type_map = {
        "rate": "Rating",
        "bug": "Bug",
        "idea": "Idea"
    }

    data = await state.get_data()
    stars = data.get("stars")
    stars_display = "⭐" * int(stars) if stars else ""

    row = [
        datetime.now().strftime("%d.%m.%Y %H:%M"),
        str(message.from_user.id),
        user.get("full_name", "Unknown"),
        type_map.get(data.get("type"), "Unknown"),
        stars_display,
        message.text
    ]

    append_feedback_to_sheet(row)

    await state.clear()
    await message.answer(TEXTS[lang]["rate_thanks"])