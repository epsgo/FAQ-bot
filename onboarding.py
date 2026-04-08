import asyncio
import logging
import os
from datetime import datetime, time, timedelta

import gspread

logger = logging.getLogger(__name__)
from aiogram import Router, F, Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey

from db import get_user, get_all_approved_users, update_onboarding_stage
from const import (
    ADMIN_IDS, ONBOARDING_STAGES, ONBOARDING_QUESTIONS,
    ONBOARDING_TEXTS, ONBOARDING_NEGATIVE_KEYWORDS,
)

router = Router()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
NOTIFY_IDS = {int(i.strip()) for i in os.getenv("NOTIFY_IDS", "").split(",") if i.strip()} or ADMIN_IDS
ALL_Q_KEYS = ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q11_detail", "q12"]
_Q_COL_OFFSET = 3  


class OnboardingState(StatesGroup):
    answering = State()


def get_score_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=str(i), callback_data=f"ob_score_{i}")
        for i in range(1, 6)
    ]])


def get_yn_kb(lang: str) -> InlineKeyboardMarkup:
    t = ONBOARDING_TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t["yn_yes"], callback_data="ob_yn_yes"),
        InlineKeyboardButton(text=t["yn_no"],  callback_data="ob_yn_no"),
    ]])


def has_negative_sentiment(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in ONBOARDING_NEGATIVE_KEYWORDS)


async def alert_managers(bot: Bot, user: dict, lang: str, template_key: str, question: str, answer: str):
    t = ONBOARDING_TEXTS[lang]
    text = t[template_key].format(
        name=user.get("full_name", "Unknown"),
        user_id=user["user_id"],
        question=question,
        answer=answer,
    )
    for admin_id in NOTIFY_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


async def send_question(bot: Bot, user_id: int, lang: str, stage: int, q_idx: int):
    questions = ONBOARDING_STAGES[stage]["questions"]
    q = questions[q_idx]
    q_text = ONBOARDING_QUESTIONS[q["key"]][lang]
    total = len(questions)
    text = f"<b>{q_idx + 1}/{total}</b>\n\n{q_text}"

    if q["type"] == "score":
        await bot.send_message(user_id, text, reply_markup=get_score_kb(), parse_mode="HTML")
    elif q["type"] == "yn":
        await bot.send_message(user_id, text, reply_markup=get_yn_kb(lang), parse_mode="HTML")
    else:
        await bot.send_message(user_id, text, parse_mode="HTML")


def _col_letter(q_idx: int) -> str:
    return chr(ord('A') + _Q_COL_OFFSET + q_idx)


def _init_onboarding_sheet(ws):
    total_cols = _Q_COL_OFFSET + len(ALL_Q_KEYS)

    def q_header(k):
        if k == "q11_detail":
            return "Q11 Detail"
        return f"Q{k[1:]}"  

    headers = ["Timestamp", "User ID", "Name"] + [q_header(k) for k in ALL_Q_KEYS]
    ws.append_row(headers)

    note_cells = [{"note": ""}, {"note": ""}, {"note": ""}]
    for k in ALL_Q_KEYS:
        if k == "q11_detail":
            note_cells.append({"note": "Детали ответа на вопрос Q11 (если ответил «Да»)"})
        else:
            note_cells.append({"note": ONBOARDING_QUESTIONS[k]["ru"]})

    sheet_id = ws.id
    last_col_letter = _col_letter(len(ALL_Q_KEYS) - 1)

    ws.spreadsheet.batch_update({"requests": [
        {
            "updateSheetProperties": {
                "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }
        },
        {
            "updateCells": {
                "rows": [{"values": note_cells}],
                "fields": "note",
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0, "endRowIndex": 1,
                    "startColumnIndex": 0, "endColumnIndex": total_cols,
                }
            }
        },
        {"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 130}, "fields": "pixelSize"
        }},
        {"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},
            "properties": {"pixelSize": 110}, "fields": "pixelSize"
        }},
        {"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3},
            "properties": {"pixelSize": 220}, "fields": "pixelSize"
        }},
    ]})

    ws.format(f"A1:{last_col_letter}1", {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER"})


def save_to_sheet(user: dict, answers: dict):
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
            ws = sh.worksheet("Onboarding")
        except gspread.exceptions.WorksheetNotFound:
            total_cols = _Q_COL_OFFSET + len(ALL_Q_KEYS)
            ws = sh.add_worksheet(title="Onboarding", rows=1000, cols=total_cols)
            _init_onboarding_sheet(ws)

        all_values = ws.get_all_values()
        user_id_str = str(user["user_id"])

        row_idx = None
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) > 1 and row[1] == user_id_str:
                row_idx = i
                break

        if row_idx is None:
            new_row = [
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                user_id_str,
                user.get("full_name", "Unknown"),
            ] + [answers.get(k, "") for k in ALL_Q_KEYS]
            next_row = next(
                (i for i, r in enumerate(all_values, start=1) if all(c == "" for c in r)),
                len(all_values) + 1
            )
            ws.update(f"A{next_row}", [new_row])
        else:
            updates = []
            for i, k in enumerate(ALL_Q_KEYS):
                if k in answers:
                    updates.append({
                        "range": f"{_col_letter(i)}{row_idx}",
                        "values": [[answers[k]]]
                    })
            if updates:
                ws.batch_update(updates)

        last_col = _col_letter(len(ALL_Q_KEYS) - 1)
        ws.format(f"A2:{last_col}1000", {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"})

    except Exception as e:
        logger.error("Ошибка записи в Sheets (Onboarding): %s", e, exc_info=True)



async def finish_stage(bot: Bot, state: FSMContext, user: dict, answers: dict, stage: int):
    lang = user["language"]
    await asyncio.to_thread(save_to_sheet, user, answers)
    update_onboarding_stage(user["user_id"], stage)
    await state.clear()
    await bot.send_message(user["user_id"], ONBOARDING_TEXTS[lang]["thanks"])



async def advance(bot: Bot, state: FSMContext, user: dict, data: dict):
    stage = data["stage"]
    q_idx = data["q_idx"] + 1
    questions = ONBOARDING_STAGES[stage]["questions"]

    if q_idx < len(questions):
        await state.update_data(q_idx=q_idx)
        await send_question(bot, user["user_id"], user["language"], stage, q_idx)
    else:
        await finish_stage(bot, state, user, data["answers"], stage)



@router.callback_query(OnboardingState.answering, F.data.startswith("ob_score_"))
async def handle_score(callback: CallbackQuery, state: FSMContext):
    score = int(callback.data.split("_")[-1])
    user = get_user(callback.from_user.id)
    lang = user["language"]
    data = await state.get_data()

    stage = data["stage"]
    q_idx = data["q_idx"]
    q_key = ONBOARDING_STAGES[stage]["questions"][q_idx]["key"]
    q_text = ONBOARDING_QUESTIONS[q_key][lang]

    answers = data.get("answers", {})
    answers[q_key] = str(score)
    await state.update_data(answers=answers)

    await callback.message.edit_reply_markup()
    await callback.answer()

    if score <= 2:
        await alert_managers(callback.bot, user, lang, "alert_score", q_text, str(score))

    await advance(callback.bot, state, user, {**data, "answers": answers})


@router.callback_query(OnboardingState.answering, F.data.in_({"ob_yn_yes", "ob_yn_no"}))
async def handle_yn(callback: CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    lang = user["language"]
    data = await state.get_data()

    stage = data["stage"]
    q_idx = data["q_idx"]
    q_key = ONBOARDING_STAGES[stage]["questions"][q_idx]["key"]

    answered_yes = callback.data == "ob_yn_yes"

    await callback.message.edit_reply_markup()
    await callback.answer()

    if answered_yes:
        answers = data.get("answers", {})
        answers[q_key] = "yes"
        await state.update_data(answers=answers, awaiting_yn_text=True)
        await callback.bot.send_message(
            user["user_id"],
            ONBOARDING_TEXTS[lang]["yn_followup"]
        )
    else:
        answers = data.get("answers", {})
        answers[q_key] = "no"
        await state.update_data(answers=answers, awaiting_yn_text=False)
        await advance(callback.bot, state, user, {**data, "answers": answers})


@router.message(OnboardingState.answering)
async def handle_text_answer(message: Message, state: FSMContext):
    if not message.text:
        return

    user = get_user(message.from_user.id)
    lang = user["language"]
    data = await state.get_data()

    stage = data["stage"]
    q_idx = data["q_idx"]
    q_key = ONBOARDING_STAGES[stage]["questions"][q_idx]["key"]
    q_text = ONBOARDING_QUESTIONS[q_key][lang]
    answers = data.get("answers", {})

    if data.get("awaiting_yn_text"):
        answers[f"{q_key}_detail"] = message.text
        await state.update_data(answers=answers, awaiting_yn_text=False)
        await alert_managers(message.bot, user, lang, "alert_yn", q_text, message.text)
        await advance(message.bot, state, user, {**data, "answers": answers})
        return

    current_type = ONBOARDING_STAGES[stage]["questions"][q_idx]["type"]
    if current_type != "text":
        return

    answers[q_key] = message.text
    await state.update_data(answers=answers)

    if has_negative_sentiment(message.text):
        await alert_managers(message.bot, user, lang, "alert_text", q_text, message.text)

    await advance(message.bot, state, user, {**data, "answers": answers})



@router.message(Command("ob_test"))
async def ob_test(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit() or int(args[1]) not in (1, 2, 3, 4):
        await message.answer("Usage: /ob_test <stage>\nStage: 1 (day 3), 2 (day 7), 3 (day 14), 4 (day 30)")
        return

    stage = int(args[1])
    user = get_user(message.from_user.id)
    if not user:
        await message.answer("You are not registered.")
        return

    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await state.set_state(OnboardingState.answering)
    await state.update_data(stage=stage, q_idx=0, answers={}, awaiting_yn_text=False)

    lang = user["language"]
    day = ONBOARDING_STAGES[stage]["day"]
    await message.answer(ONBOARDING_TEXTS[lang][f"intro_day{day}"])
    await send_question(message.bot, message.from_user.id, lang, stage, 0)



async def send_stage(bot: Bot, dp: Dispatcher, user: dict, stage: int):
    user_id = user["user_id"]
    lang = user["language"]

    storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
    fsm = FSMContext(storage=dp.storage, key=storage_key)

    current_state = await fsm.get_state()
    if current_state is not None:
        return  

    await fsm.set_state(OnboardingState.answering)
    await fsm.update_data(stage=stage, q_idx=0, answers={}, awaiting_yn_text=False)

    day = ONBOARDING_STAGES[stage]["day"]
    intro_key = f"intro_day{day}"
    await bot.send_message(user_id, ONBOARDING_TEXTS[lang][intro_key])
    await send_question(bot, user_id, lang, stage, 0)


async def check_user_onboarding(bot: Bot, dp: Dispatcher, user: dict):
    created_at = datetime.fromisoformat(user["created_at"])
    days_since = (datetime.now() - created_at).days
    current_stage = user.get("onboarding_stage", 0)

    if current_stage >= 4:
        return

    stage_days = {1: 3, 2: 7, 3: 14, 4: 30}

    for stage in range(current_stage + 1, 5):
        if days_since >= stage_days[stage]:
            try:
                await send_stage(bot, dp, user, stage)
                update_onboarding_stage(user["user_id"], stage)
            except Exception as e:
                logger.error("Ошибка отправки стадии %s пользователю %s: %s", stage, user["user_id"], e, exc_info=True)
            break  


async def onboarding_scheduler(bot: Bot, dp: Dispatcher):
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), time(12, 0))
        if target <= now:
            target += timedelta(days=1)

        await asyncio.sleep((target - datetime.now()).total_seconds())

        try:
            users = get_all_approved_users()
        except Exception as e:
            logger.error("Ошибка получения пользователей в планировщике: %s", e, exc_info=True)
            continue

        for user in users:
            await check_user_onboarding(bot, dp, user)
