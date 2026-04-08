import os
from datetime import datetime
import gspread
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import auth_required, get_main_menu
from const import TEST_BTNS, TEXTS, TEST_QUESTIONS, ADMIN_IDS

router = Router()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
TOTAL_QUESTIONS = len(TEST_QUESTIONS)
CANCEL_TEST_BTNS = {TEXTS[lang]["test_cancel_btn"] for lang in TEXTS}


class TestState(StatesGroup):
    answering = State()


def get_test_cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]["test_cancel_btn"])]],
        resize_keyboard=True
    )




def build_time_cell(start_time: datetime, end_time: datetime, partial: bool = False, answered: int = 0) -> str:
    duration = end_time - start_time
    total_minutes, total_seconds = divmod(int(duration.total_seconds()), 60)
    status = f"⚠️ partial ({answered}/{TOTAL_QUESTIONS})\n" if partial else ""
    return (
        f"{status}"
        f"Start: {start_time.strftime('%d.%m.%Y %H:%M')}\n"
        f"End:   {end_time.strftime('%d.%m.%Y %H:%M')}\n"
        f"Time:  {total_minutes}m {total_seconds}s"
    )


def append_test_to_sheet(row: list, headers: list):
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
            worksheet = sh.worksheet("Test Results")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sh.add_worksheet(title="Test Results", rows=1000, cols=TOTAL_QUESTIONS + 3)

        values = worksheet.get_all_values()
        if not values or all(cell == "" for cell in values[0]):
            worksheet.append_row(headers)

            sheet_id = worksheet.id

            note_cells = [{"note": ""}, {"note": ""}, {"note": ""}]
            for q in TEST_QUESTIONS:
                note_cells.append({"note": q["ru"]})

            batch_requests = [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 1
                        },
                        "properties": {"pixelSize": 150},
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 2,
                            "endIndex": 3
                        },
                        "properties": {"pixelSize": 220},
                        "fields": "pixelSize"
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"frozenRowCount": 1}
                        },
                        "fields": "gridProperties.frozenRowCount"
                    }
                },
                {
                    "updateCells": {
                        "rows": [{"values": note_cells}],
                        "fields": "note",
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": TOTAL_QUESTIONS + 3,
                        }
                    }
                }
            ]
            worksheet.spreadsheet.batch_update({"requests": batch_requests})
            worksheet.format("A1:Z1", {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})

        worksheet.append_row(row)
        worksheet.format("A2:Z1000", {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"})

    except Exception as e:
        print(f"Test Excel Error: {e}")


@router.message(F.text.in_(TEST_BTNS))
@auth_required
async def start_test(message: Message, state: FSMContext, user: dict):
    lang = user["language"]
    await state.set_state(TestState.answering)
    await state.update_data(current_q=0, answers=[], start_time=datetime.now().isoformat())

    await message.answer(TEXTS[lang]["test_start"], reply_markup=ReplyKeyboardRemove())
    q_text = TEST_QUESTIONS[0][lang]
    await message.answer(
        f"<b>1/{TOTAL_QUESTIONS}</b>\n\n{q_text}",
        reply_markup=get_test_cancel_kb(lang),
        parse_mode="HTML"
    )


@router.message(TestState.answering, F.text.in_(CANCEL_TEST_BTNS))
@auth_required
async def cancel_test(message: Message, state: FSMContext, user: dict):
    lang = user["language"]
    is_admin = message.from_user.id in ADMIN_IDS
    await state.clear()
    await message.answer(
        TEXTS[lang]["test_cancelled_discarded"],
        reply_markup=get_main_menu(lang, is_admin=is_admin)
    )


@router.message(TestState.answering)
@auth_required
async def handle_test_answer(message: Message, state: FSMContext, user: dict):
    lang = user["language"]

    if not message.text:
        await message.answer(TEXTS[lang]["test_text_only"])
        return

    data = await state.get_data()
    current_q = data.get("current_q", 0)
    answers = data.get("answers", [])

    answers.append(message.text)
    current_q += 1

    if current_q < TOTAL_QUESTIONS:
        await state.update_data(current_q=current_q, answers=answers)
        q_text = TEST_QUESTIONS[current_q][lang]
        await message.answer(
            f"<b>{current_q + 1}/{TOTAL_QUESTIONS}</b>\n\n{q_text}",
            reply_markup=get_test_cancel_kb(lang),
            parse_mode="HTML"
        )
    else:
        is_admin = message.from_user.id in ADMIN_IDS
        end_time = datetime.now()
        start_time = datetime.fromisoformat(data.get("start_time"))

        headers = ["Time", "User ID", "Name"] + [f"Q{i + 1}" for i in range(TOTAL_QUESTIONS)]
        row = [
            build_time_cell(start_time, end_time),
            str(message.from_user.id),
            user.get("full_name", "Unknown"),
        ] + answers

        append_test_to_sheet(row, headers)

        await state.clear()
        await message.answer(
            TEXTS[lang]["test_thanks"],
            reply_markup=get_main_menu(lang, is_admin=is_admin)
        )


