from aiogram import Router, F
from db import *
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from const import ADMIN_BTNS, ADMIN_IDS, TEXTS
from keyboards import get_main_menu, get_start_kb

router = Router()

ROLES = {
    "manager":  "👔 Managers",
    "teamlead": "👑 Teamleads",
    "support":  "🎧 Supports",
}


@router.callback_query.middleware()
async def admin_only(handler, callback: CallbackQuery, data: dict):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    return await handler(callback, data)


def get_admin_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 All Users", callback_data="admin_all_users")],
        [InlineKeyboardButton(text="⏳ Awaiting approval", callback_data="admin_pending")]
    ])


def get_role_tabs_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👔 Managers",  callback_data="admin_role_manager"),
            InlineKeyboardButton(text="👑 Teamleads", callback_data="admin_role_teamlead"),
            InlineKeyboardButton(text="🎧 Supports",  callback_data="admin_role_support"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_admin")]
    ])


def get_role_select_kb(prefix: str, back_cb: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👔 Managers",  callback_data=f"{prefix}_manager"),
            InlineKeyboardButton(text="👑 Teamleads", callback_data=f"{prefix}_teamlead"),
            InlineKeyboardButton(text="🎧 Supports",  callback_data=f"{prefix}_support"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=back_cb)]
    ])


def user_card_text(user: dict, user_id: int) -> str:
    role_label = ROLES.get(user.get("role", ""), user.get("role", "—"))
    return (
        f"<b>👤 {user['full_name']}</b>\n"
        f"Role: {role_label}\n"
        f"ID: {user_id}\n"
        f"Birthdate: {user['birthdate']}"
    )


def user_card_kb(user_id: int, back_role: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Change Role", callback_data=f"change_role_{user_id}_{back_role}"),
            InlineKeyboardButton(text="🗑️ Delete",      callback_data=f"confirm_delete_{user_id}_{back_role}"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data=f"admin_role_{back_role}")]
    ])


# ─── Admin main ────────────────────────────────────────────────────────────────

@router.message(F.text.in_(ADMIN_BTNS))
async def show_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("⚙️ Admin Panel", reply_markup=get_admin_main_kb())


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ Admin Panel", reply_markup=get_admin_main_kb())
    await callback.answer()


# ─── All Users → role tabs ─────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_all_users")
async def show_all_users(callback: types.CallbackQuery):
    await callback.message.edit_text("📋 Select role to view:", reply_markup=get_role_tabs_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_role_"))
async def show_users_by_role(callback: CallbackQuery):
    role = callback.data.split("admin_role_")[1]
    users = get_users_by_role(role)
    role_label = ROLES.get(role, role)

    if not users:
        await callback.message.edit_text(
            f"{role_label}: no users found.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_all_users")]
            ])
        )
        await callback.answer()
        return

    buttons = []
    for u in users:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {u['full_name']}",
            callback_data=f"view_user_{u['user_id']}_{role}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_all_users")])

    await callback.message.edit_text(
        f"{role_label}:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


# ─── View user ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("view_user_"))
async def view_user(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id   = int(parts[2])
    back_role = parts[3]
    user = get_user(user_id)
    await callback.message.edit_text(
        user_card_text(user, user_id),
        reply_markup=user_card_kb(user_id, back_role),
        parse_mode="HTML"
    )
    await callback.answer()


# ─── Change Role ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("change_role_"))
async def change_role(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id   = int(parts[2])
    back_role = parts[3]
    user = get_user(user_id)

    await callback.message.edit_text(
        f"Select new role for <b>{user['full_name']}</b>:",
        reply_markup=get_role_select_kb(
            prefix=f"set_role_{user_id}",
            back_cb=f"view_user_{user_id}_{back_role}"
        ),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_role_"))
async def set_role_handler(callback: CallbackQuery):
    parts    = callback.data.split("_")
    user_id  = int(parts[2])
    new_role = parts[3]
    set_role(user_id, new_role)

    user = get_user(user_id)
    await callback.answer(f"✅ Role → {ROLES.get(new_role, new_role)}", show_alert=False)
    await callback.message.edit_text(
        user_card_text(user, user_id),
        reply_markup=user_card_kb(user_id, new_role),
        parse_mode="HTML"
    )


# ─── Delete user ───────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    parts   = callback.data.split("_")
    user_id = int(parts[2])
    source  = parts[3]

    user = get_user(user_id)
    text = f"⚠️ <b>Delete this user?</b>\n{user['full_name']} ({user_id})"

    back_target = "admin_pending" if source == "pending" else f"view_user_{user_id}_{source}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"delete_user_{user_id}_{source}")],
        [InlineKeyboardButton(text="❌ No, Cancel",  callback_data=back_target)]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("delete_user_"))
async def process_delete_user(callback: CallbackQuery):
    parts   = callback.data.split("_")
    user_id = int(parts[2])
    source  = parts[3]
    user    = get_user(user_id)

    try:
        await callback.bot.send_message(chat_id=user_id, text="...", reply_markup=get_start_kb())
    except Exception:
        pass

    delete_user(user_id)
    await callback.answer(f"🗑️ {user['full_name']} deleted")

    if source == "pending":
        await show_pending(callback)
    else:
        await _refresh_role_list(callback, source)


async def _refresh_role_list(callback: CallbackQuery, role: str):
    users      = get_users_by_role(role)
    role_label = ROLES.get(role, role)

    if not users:
        await callback.message.edit_text(
            f"{role_label}: no users found.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_all_users")]
            ])
        )
        return

    buttons = []
    for u in users:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {u['full_name']}",
            callback_data=f"view_user_{u['user_id']}_{role}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_all_users")])

    await callback.message.edit_text(
        f"{role_label}:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


# ─── Pending / Approve ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_pending")
async def show_pending(callback: CallbackQuery):
    users = get_pending_users()
    if not users:
        await callback.message.edit_text("No pending requests found.", reply_markup=get_admin_main_kb())
        await callback.answer()
        return

    buttons = []
    for u in users:
        buttons.append([InlineKeyboardButton(
            text=f"👤 {u['full_name']}",
            callback_data=f"view_pending_{u['user_id']}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_admin")])
    await callback.message.edit_text(
        "Select user to review:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_pending_"))
async def view_pending_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    user    = get_user(user_id)

    text = (
        f"<b>Approve this user?</b>\n\n"
        f"Name: {user['full_name']}\n"
        f"Birthdate: {user['birthdate']}\n"
        f"ID: {user_id}\n\n"
        f"Select role:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👔 Managers",  callback_data=f"approve_with_role_{user_id}_manager"),
            InlineKeyboardButton(text="👑 Teamleads", callback_data=f"approve_with_role_{user_id}_teamlead"),
            InlineKeyboardButton(text="🎧 Supports",  callback_data=f"approve_with_role_{user_id}_support"),
        ],
        [InlineKeyboardButton(text="❌ Reject", callback_data=f"confirm_delete_{user_id}_pending")],
        [InlineKeyboardButton(text="⬅️ Back to list", callback_data="admin_pending")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("approve_with_role_"))
async def process_approve_with_role(callback: CallbackQuery):
    parts   = callback.data.split("_")
    # approve_with_role_{user_id}_{role}
    user_id = int(parts[3])
    role    = parts[4]

    approve_user_with_role(user_id, role)
    user       = get_user(user_id)
    role_label = ROLES.get(role, role)

    try:
        await callback.bot.send_message(
            user_id,
            TEXTS[user['language']]["registered"],
            reply_markup=get_main_menu(user['language'], is_admin=(user_id in ADMIN_IDS))
        )
    except Exception:
        pass

    await callback.answer(f"✅ {user['full_name']} approved as {role_label}", show_alert=False)
    await show_pending(callback)
