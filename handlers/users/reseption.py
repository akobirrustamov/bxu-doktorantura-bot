import shutil

from aiogram.dispatcher.filters import Text
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from loader import bot, db
import os
from loader import dp

REVIEWER_ID = 855893763  # The admin who reviews the application



async def notify_admin_about_application(telegram_id: int):
    # 1. Fetch application data
    application = await db.get_application(telegram_id)
    if not application:
        return

    # 2. Zip user's folder
    user_folder = os.path.join("./files", str(telegram_id))
    zip_filename = f"{telegram_id}_application.zip"
    zip_path = os.path.join("./files", zip_filename)

    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', user_folder)

    # 3. Compose admin message
    text = (
        f"✉️ <b>Yangi ariza!</b>\n\n"
        f"<b>F.I.Sh:</b> {application['full_name']}\n"
        f"<b>Telefon:</b> {application['phone']}\n"
        f"<b>Telegram ID:</b> {telegram_id}\n"
        f"<b>Username:</b> @{application['username'] if application['username'] else 'yo‘q'}\n"
        f"<b>Status:</b> {application['status']}\n"
    )

    # 4. Inline buttons
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{telegram_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{telegram_id}")
    )

    # 5. Send ZIP file and message to admin
    await bot.send_document(
        chat_id=REVIEWER_ID,
        document=InputFile(zip_path),
        caption=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.callback_query_handler(Text(startswith="accept_"))
async def accept_application(callback: types.CallbackQuery):
    telegram_id = int(callback.data.split("_")[1])
    await db.update_application_step(telegram_id, 8)
    await db.update_application_step(telegram_id, field_name="status", field_value=-1, status=-1)
    await bot.send_message(telegram_id, "✅ Arizangiz muvofaqqiyatli qabul qilindi. Tabriklaymiz!")
    await callback.message.edit_reply_markup()
    await callback.answer("Qabul qilindi")



@dp.callback_query_handler(Text(startswith="reject_"))
async def reject_application(callback: types.CallbackQuery):
    telegram_id = int(callback.data.split("_")[1])

    # 1. Update status in DB
    await db.update_application_status(telegram_id, -1)

    # 2. Send message to user
    await bot.send_message(telegram_id, "❌ Afsuski, arizangiz rad etildi. Iltimos, hujjatlarni tekshirib qayta topshiring.")

    # 3. Clean up files
    user_folder = os.path.join("./files", str(telegram_id))
    zip_path = os.path.join("./files", f"{telegram_id}_application.zip")

    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # 4. Clean up message in admin chat
    await callback.message.edit_reply_markup()
    await callback.answer("Rad etildi")
    await callback.message.delete()

