from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from const import MEETING_BTNS, TEXTS
from keyboards import auth_required
from db import get_user, get_users_by_role, create_meeting, update_meeting_status, get_meeting
from datetime import datetime

router = Router()


class MeetingStates(StatesGroup):
    waiting_for_datetime = State()


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text


def _meeting_main_kb(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "meet_btn_manager"),  callback_data="meet_role_manager"),
            InlineKeyboardButton(text=t(lang, "meet_btn_teamlead"), callback_data="meet_role_teamlead"),
        ],
        [InlineKeyboardButton(text=t(lang, "meet_btn_mentor"), callback_data="meet_mentor")],
    ])


def _back_kb(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "meet_back"), callback_data="meet_back")]
    ])


def _skip_datetime_kb(lang: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "meet_skip_datetime"), callback_data="meet_skip_datetime")],
        [InlineKeyboardButton(text=t(lang, "meet_back"), callback_data="meet_back")]
    ])


@router.message(F.text.in_(MEETING_BTNS))
@auth_required
async def show_meeting_menu(message: Message, user: dict):
    lang = user["language"]
    await message.answer(t(lang, "meet_menu_title"), reply_markup=_meeting_main_kb(lang))


@router.callback_query(F.data == "meet_back")
async def meet_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = get_user(callback.from_user.id)
    lang = user["language"] if user else "en"
    await callback.message.edit_text(t(lang, "meet_menu_title"), reply_markup=_meeting_main_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("meet_role_"))
async def show_role_users(callback: CallbackQuery):
    role = callback.data.split("meet_role_")[1]
    user = get_user(callback.from_user.id)
    lang = user["language"] if user else "en"

    users = get_users_by_role(role)
    candidates = [u for u in users if u["user_id"] != callback.from_user.id]

    select_key = "meet_select_manager" if role == "manager" else "meet_select_teamlead"

    if not candidates:
        await callback.message.edit_text(t(lang, "meet_no_available"), reply_markup=_back_kb(lang))
        await callback.answer()
        return

    buttons = []
    for u in candidates:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {u['full_name']}",
            callback_data=f"meet_user_{u['user_id']}_{callback.from_user.id}"
        )])
    buttons.append([InlineKeyboardButton(text=t(lang, "meet_back"), callback_data="meet_back")])

    await callback.message.edit_text(
        t(lang, select_key),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("meet_user_"))
async def request_meeting_ask_datetime(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    target_id    = int(parts[2])
    requester_id = int(parts[3])

    requester = get_user(requester_id)
    req_lang  = requester["language"] if requester else "en"

    await state.update_data(target_id=target_id, requester_id=requester_id)
    await state.set_state(MeetingStates.waiting_for_datetime)

    await callback.message.edit_text(
        t(req_lang, "meet_ask_datetime"),
        reply_markup=_skip_datetime_kb(req_lang)
    )
    await callback.answer()


@router.message(MeetingStates.waiting_for_datetime)
async def handle_datetime_input(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    lang = user["language"] if user else "en"
    
    datetime_text = message.text.strip()
    
    try:
        meeting_dt = datetime.strptime(datetime_text, "%d.%m.%Y %H:%M")
        if meeting_dt < datetime.now():
            await message.answer(
                t(lang, "meet_invalid_datetime") + "\n\n⚠️ Дата не может быть в прошлом.",
                reply_markup=_skip_datetime_kb(lang)
            )
            return
        
        data = await state.get_data()
        target_id = data.get("target_id")
        requester_id = data.get("requester_id")
        
        requester = get_user(requester_id)
        target    = get_user(target_id)
        req_lang  = requester["language"] if requester else "en"
        tgt_lang  = target["language"]    if target    else "en"

        meeting_id = create_meeting(requester_id, target_id, datetime_text)

        confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=t(tgt_lang, "meet_btn_confirm"), callback_data=f"meet_confirm_{meeting_id}"),
                InlineKeyboardButton(text=t(tgt_lang, "meet_btn_decline"), callback_data=f"meet_decline_{meeting_id}"),
            ]
        ])

        try:
            await message.bot.send_message(
                target_id,
                t(tgt_lang, "meet_with_datetime", name=requester["full_name"], datetime=datetime_text),
                reply_markup=confirm_kb,
                parse_mode="HTML"
            )
        except Exception:
            await message.answer(t(req_lang, "meet_error"))
            await state.clear()
            return

        await message.answer(t(req_lang, "meet_datetime_set", datetime=datetime_text))
        await state.clear()
        
    except ValueError:
        await message.answer(
            t(lang, "meet_invalid_datetime"),
            reply_markup=_skip_datetime_kb(lang)
        )


@router.callback_query(F.data == "meet_skip_datetime")
async def skip_datetime(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target_id = data.get("target_id")
    requester_id = data.get("requester_id")

    requester = get_user(requester_id)
    target    = get_user(target_id)
    req_lang  = requester["language"] if requester else "en"
    tgt_lang  = target["language"]    if target    else "en"

    meeting_id = create_meeting(requester_id, target_id, meeting_datetime=None)

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(tgt_lang, "meet_btn_confirm"), callback_data=f"meet_confirm_{meeting_id}"),
            InlineKeyboardButton(text=t(tgt_lang, "meet_btn_decline"), callback_data=f"meet_decline_{meeting_id}"),
        ]
    ])

    try:
        await callback.bot.send_message(
            target_id,
            t(tgt_lang, "meet_incoming_11", name=requester["full_name"]),
            reply_markup=confirm_kb,
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.edit_text(t(req_lang, "meet_error"), reply_markup=_back_kb(req_lang))
        await callback.answer()
        await state.clear()
        return

    await callback.message.edit_text(t(req_lang, "meet_sent"))
    await callback.answer()
    await state.clear()


@router.callback_query(F.data.startswith("meet_confirm_"))
async def confirm_meeting(callback: CallbackQuery):
    meeting_id = callback.data.split("_")[2]
    meeting = get_meeting(meeting_id)
    
    if not meeting:
        await callback.answer("Встреча не найдена", show_alert=True)
        return
    
    requester_id = meeting["requester_id"]
    confirmer    = get_user(callback.from_user.id)
    requester    = get_user(requester_id)
    cfm_lang     = confirmer["language"]  if confirmer  else "en"
    req_lang     = requester["language"]  if requester  else "en"

    update_meeting_status(meeting_id, "confirmed")

    try:
        if meeting.get("meeting_datetime"):
            await callback.bot.send_message(
                requester_id,
                t(req_lang, "meet_confirmed_with_datetime", name=confirmer["full_name"], datetime=meeting["meeting_datetime"]),
                parse_mode="HTML"
            )
        else:
            await callback.bot.send_message(
                requester_id,
                t(req_lang, "meet_confirmed_by", name=confirmer["full_name"]),
                parse_mode="HTML"
            )
    except Exception:
        pass

    await callback.message.edit_text(t(cfm_lang, "meet_you_confirmed"))
    await callback.answer()


@router.callback_query(F.data.startswith("meet_decline_"))
async def decline_meeting(callback: CallbackQuery):
    meeting_id = callback.data.split("_")[2]
    meeting = get_meeting(meeting_id)
    
    if not meeting:
        await callback.answer("Встреча не найдена", show_alert=True)
        return
    
    requester_id = meeting["requester_id"]
    decliner     = get_user(callback.from_user.id)
    requester    = get_user(requester_id)
    dcl_lang     = decliner["language"]  if decliner  else "en"
    req_lang     = requester["language"] if requester else "en"

    update_meeting_status(meeting_id, "declined")

    try:
        if meeting.get("meeting_datetime"):
            await callback.bot.send_message(
                requester_id,
                t(req_lang, "meet_declined_with_datetime", name=decliner["full_name"], datetime=meeting["meeting_datetime"]),
                parse_mode="HTML"
            )
        else:
            await callback.bot.send_message(
                requester_id,
                t(req_lang, "meet_declined_by", name=decliner["full_name"]),
                parse_mode="HTML"
            )
    except Exception:
        pass

    await callback.message.edit_text(t(dcl_lang, "meet_you_declined"))
    await callback.answer()


@router.callback_query(F.data == "meet_mentor")
async def request_mentor(callback: CallbackQuery):
    user     = get_user(callback.from_user.id)
    lang     = user["language"] if user else "en"
    managers = get_users_by_role("manager")
    candidates = [m for m in managers if m["user_id"] != callback.from_user.id]

    if not candidates:
        await callback.message.edit_text(t(lang, "meet_no_available"), reply_markup=_back_kb(lang))
        await callback.answer()
        return

    buttons = []
    for m in candidates:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {m['full_name']}",
            callback_data=f"meet_mentor_{m['user_id']}_{callback.from_user.id}"
        )])
    buttons.append([InlineKeyboardButton(text=t(lang, "meet_back"), callback_data="meet_back")])

    await callback.message.edit_text(
        t(lang, "meet_select_mentor"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("meet_mentor_"))
async def send_mentor_request(callback: CallbackQuery):
    parts        = callback.data.split("_")
    manager_id   = int(parts[2])
    requester_id = int(parts[3])

    requester = get_user(requester_id)
    manager   = get_user(manager_id)
    req_lang  = requester["language"] if requester else "en"
    mgr_lang  = manager["language"]   if manager   else "en"

    try:
        await callback.bot.send_message(
            manager_id,
            t(mgr_lang, "meet_incoming_mentor", name=requester["full_name"]),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.edit_text(t(req_lang, "meet_error"), reply_markup=_back_kb(req_lang))
        await callback.answer()
        return

    await callback.message.edit_text(t(req_lang, "meet_mentor_sent"))
    await callback.answer()
