from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from const import MEETING_BTNS, TEXTS
from keyboards import auth_required
from db import get_user, get_users_by_role

router = Router()


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


# ─── Main menu ────────────────────────────────────────────────────────────────

@router.message(F.text.in_(MEETING_BTNS))
@auth_required
async def show_meeting_menu(message: Message, user: dict):
    lang = user["language"]
    await message.answer(t(lang, "meet_menu_title"), reply_markup=_meeting_main_kb(lang))


@router.callback_query(F.data == "meet_back")
async def meet_back(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    lang = user["language"] if user else "en"
    await callback.message.edit_text(t(lang, "meet_menu_title"), reply_markup=_meeting_main_kb(lang))
    await callback.answer()


# ─── 1:1 — select person ─────────────────────────────────────────────────────

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


# ─── 1:1 — send request ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("meet_user_"))
async def request_meeting(callback: CallbackQuery):
    parts = callback.data.split("_")
    target_id    = int(parts[2])
    requester_id = int(parts[3])

    requester = get_user(requester_id)
    target    = get_user(target_id)
    req_lang  = requester["language"] if requester else "en"
    tgt_lang  = target["language"]    if target    else "en"

    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(tgt_lang, "meet_btn_confirm"), callback_data=f"meet_confirm_{requester_id}"),
            InlineKeyboardButton(text=t(tgt_lang, "meet_btn_decline"), callback_data=f"meet_decline_{requester_id}"),
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
        return

    await callback.message.edit_text(t(req_lang, "meet_sent"))
    await callback.answer()


# ─── 1:1 — confirm / decline ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("meet_confirm_"))
async def confirm_meeting(callback: CallbackQuery):
    requester_id = int(callback.data.split("_")[2])
    confirmer    = get_user(callback.from_user.id)
    requester    = get_user(requester_id)
    cfm_lang     = confirmer["language"]  if confirmer  else "en"
    req_lang     = requester["language"]  if requester  else "en"

    try:
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
    requester_id = int(callback.data.split("_")[2])
    decliner     = get_user(callback.from_user.id)
    requester    = get_user(requester_id)
    dcl_lang     = decliner["language"]  if decliner  else "en"
    req_lang     = requester["language"] if requester else "en"

    try:
        await callback.bot.send_message(
            requester_id,
            t(req_lang, "meet_declined_by", name=decliner["full_name"]),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.message.edit_text(t(dcl_lang, "meet_you_declined"))
    await callback.answer()


# ─── Mentor request ───────────────────────────────────────────────────────────

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
