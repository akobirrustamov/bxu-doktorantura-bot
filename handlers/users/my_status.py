from aiogram import types
from aiogram.dispatcher.filters import Text
from loader import dp, db
from handlers.users.start import send_welcome_message

status_labels = {
    0: "🟡 Boshlanmagan",
    1: "✍️ F.I.Sh kiritildi",
    2: "📱 Telefon raqam kiritildi",
    3: "📄 Jadval yuklandi",
    4: "🎓 Diplom yuklandi",
    5: "🆔 Pasport yuklandi",
    6: "🏢 Tavsiyanoma (Word) yuklandi",
    7: "🏢 Tavsiyanoma (PDF) yuklandi",
    8: "✅ To‘liq topshirildi (Qabulda)",
    -1: "❌ Rad etilgan"
}

@dp.callback_query_handler(Text(equals="my_status"))
async def check_my_status(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    application = await db.get_application(telegram_id)

    if not application:
        await callback.message.answer("📭 Siz hali ariza topshirmagansiz.")
        await callback.answer()
        return

    # Status info
    current_status = application['status']
    status_text = status_labels.get(current_status, "❓ Noma'lum holat")

    text = (
        f"📄 <b>Ariza holati:</b>\n\n"
        f"<b>F.I.Sh:</b> {application['full_name'] or '❌ Kiritilmagan'}\n"
        f"<b>Telefon:</b> {application['phone'] or '❌ Kiritilmagan'}\n"
        f"<b>Hozirgi bosqich:</b> {status_text}\n"
        f"<b>Qabul holati:</b> {'✅ Qabul qilingan' if application['is_accepted'] else '⏳ Ko‘rib chiqilmoqda'}"
    )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
    await send_welcome_message(callback.message)
