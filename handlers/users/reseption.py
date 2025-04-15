import shutil
import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot, db, dp
from handlers.users.start import send_welcome_message

REVIEWER_ID = [855893763, 367877704]  # Admin Telegram IDs


# --- FSM state for rejection reason ---
class RejectReasonState(StatesGroup):
    waiting_for_reason = State()


# --- Notify admin with ZIP and inline buttons ---
async def notify_admin_about_application(telegram_id: int):
    application = await db.get_application(telegram_id)
    if not application:
        return

    user_folder = os.path.join("./files", str(telegram_id))
    zip_filename = f"{telegram_id}_application.zip"
    zip_path = os.path.join("./files", zip_filename)

    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', user_folder)

    text = (
        f"✉️ <b>Yangi ariza!</b>\n\n"
        f"<b>F.I.Sh:</b> {application['full_name']}\n"
        f"<b>Telefon:</b> {application['phone']}\n"
        f"<b>Telegram ID:</b> {telegram_id}\n"
        f"<b>Username:</b> @{application['username'] if application['username'] else 'yo‘q'}\n"
        f"<b>Status:</b> {application['status']}\n"
    )

    keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{telegram_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{telegram_id}")
    )

    for admin_id in REVIEWER_ID:
        await bot.send_document(
            chat_id=admin_id,
            document=InputFile(zip_path),
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


# --- Accept handler ---
@dp.callback_query_handler(Text(startswith="accept_"))
async def accept_application(callback: types.CallbackQuery):
    telegram_id = int(callback.data.split("_")[1])
    await db.update_application_status(telegram_id, 8)
    await db.accept_application(telegram_id)

    await bot.send_message(
        telegram_id,
        "✅ <b>Arizangiz muvofaqqiyatli qabul qilindi!</b>\n\n"
        "Rasmiylar tomonidan ko‘rib chiqildi va tasdiqlandi.\n"
        "Tez orada siz bilan bog‘lanamiz.",
        parse_mode="HTML"
    )

    await callback.message.edit_reply_markup()
    await callback.answer("Qabul qilindi")


# --- Reject handler: Ask reason ---
@dp.callback_query_handler(Text(startswith="reject_"))
async def reject_application(callback: types.CallbackQuery, state: FSMContext):
    telegram_id = int(callback.data.split("_")[1])

    # Save necessary data in state
    await state.update_data(
        rejecting_user_id=telegram_id,
        admin_chat_id=callback.message.chat.id,
        admin_message_id=callback.message.message_id
    )

    await callback.message.edit_reply_markup()
    await callback.message.answer("❗️ Rad etish sababini kiriting:")
    await RejectReasonState.waiting_for_reason.set()
    await callback.answer()


# --- Handle admin's reason message ---
@dp.message_handler(state=RejectReasonState.waiting_for_reason)
async def process_reject_reason(message: types.Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data.get("rejecting_user_id")
    admin_chat_id = data.get("admin_chat_id")
    admin_message_id = data.get("admin_message_id")
    reason = message.text.strip()

    # 1. Update status
    await db.update_application_status(telegram_id, -1)

    # 2. Notify applicant
    await bot.send_message(
        telegram_id,
        f"❌ <b>Afsuski, arizangiz rad etildi.</b>\n\n"
        f"🔎 <b>Sabab:</b> {reason}\n\n"
        f"Iltimos, hujjatlaringizni tekshirib qayta topshiring.",
        parse_mode="HTML"
    )

    # 3. Clean up files
    user_folder = os.path.join("./files", str(telegram_id))
    zip_path = os.path.join("./files", f"{telegram_id}_application.zip")
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 4. Confirm to admin
    try:
        await bot.edit_message_text(
            "❌ Ariza rad etildi va foydalanuvchiga xabar yuborildi.",
            chat_id=admin_chat_id,
            message_id=admin_message_id
        )
    except Exception:
        await bot.send_message(
            chat_id=admin_chat_id,
            text="✅ Rad etish sababi yuborildi va foydalanuvchi xabardor qilindi."
        )

    # 5. Return to start menu if needed (optional)
    fake_msg = types.Message(
        message_id=message.message_id,
        from_user=message.from_user,
        chat=message.chat,
        date=message.date
    )
    await send_welcome_message(fake_msg)

    await state.finish()
