from aiogram import Router, F
from db import *
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from const import ADMIN_BTNS, ADMIN_IDS, TEXTS
from keyboards import get_main_menu, get_start_kb

router = Router()


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

@router.message(F.text.in_(ADMIN_BTNS))
async def show_admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("⚙️ Admin Panel", reply_markup=get_admin_main_kb())


@router.callback_query(F.data == "admin_pending")
async def show_pending(callback: CallbackQuery):
    users = get_pending_users()
    if not users:
        await callback.message.edit_text("No pending requests found.", reply_markup=get_admin_main_kb())
        return

    buttons = []
    for u in users:
        buttons.append([InlineKeyboardButton(text=f"👤 {u['full_name']}", callback_data=f"view_pending_{u['user_id']}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_admin")])
    await callback.message.edit_text("Select user to review:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("view_pending_"))
async def view_pending_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    user = get_user(user_id)
    
    text = (f"<b>Approve this user?</b>\n\n"
            f"Name: {user['full_name']}\n"
            f"Birthdate: {user['birthdate']}\n"
            f"ID: {user_id}\n\n")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
         InlineKeyboardButton(text="❌ Reject", callback_data=f"confirm_delete_{user_id}_pending")],
        [InlineKeyboardButton(text="⬅️ Back to list", callback_data="admin_pending")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "admin_all_users")
async def show_all_users(callback: types.CallbackQuery):
    users = all_users()
    if not users:
        await callback.message.edit_text("No users found.", reply_markup=get_admin_main_kb())
        return

    buttons = []
    for user in users:
        buttons.append([InlineKeyboardButton(text=f"👤 {user['full_name']} ({user['user_id']})", 
                                             callback_data=f"confirm_delete_{user['user_id']}_all")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Back to Admin Panel", callback_data="back_to_admin")])
    await callback.message.edit_text("Registered Users (Click to delete):", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    data = callback.data.split("_")
    user_id = int(data[2])
    source = data[3] 
    
    user = get_user(user_id)
    text = f"⚠️ <b>Delete this user?</b>\n{user['full_name']} ({user_id})"
    
    back_target = "admin_pending" if source == "pending" else "admin_all_users"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"delete_user_{user_id}_{source}")],
        [InlineKeyboardButton(text="❌ No, Cancel", callback_data=back_target)]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("approve_"))
async def process_approve(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    approve_user(user_id)
    
    user = get_user(user_id)

    try:
        await callback.bot.send_message(
            user_id, 
            TEXTS[user['language']]["registered"], 
            reply_markup=get_main_menu(user['language'], is_admin=(user_id in ADMIN_IDS))
        )
    except Exception:
        pass

    await callback.answer(f"✅ {user['full_name']} approved")

    await show_pending(callback)


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ Admin Panel", reply_markup=get_admin_main_kb())
    await callback.answer()

@router.callback_query(F.data.startswith("delete_user_"))
async def process_delete_user(callback: CallbackQuery):
    data = callback.data.split("_")
    user_id = int(data[2])
    source = data[3]
    user = get_user(user_id)

    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text="...",
            reply_markup=get_start_kb()
        )
    except Exception as e:
        print(f"Could not notify user {user_id}: {e}")

    delete_user(user_id)

    if source == "pending":
        await show_pending(callback)
    else:
        await show_all_users(callback)

    await callback.answer(f"Agent {user['full_name']} deleted")
