from aiogram import types
from aiogram.dispatcher import filters
from loader import dp
from handlers.users.start import send_welcome_message


@dp.callback_query_handler(filters.Text(equals="contact_us"))
async def handle_contact_us(callback: types.CallbackQuery):
    text = (
        "<b>📞 Bog‘lanish uchun ma’lumotlar:</b>\n\n"
        "📱 <a href='https://t.me/bxu_uz'> <b>Telegram:</b> @bxu_uz</a>\n"
        "📸 <a href='https://www.instagram.com/bxu.uz/'> <b>Instagram:</b> @bxu.uz</a>\n"
        "📘 <a href='https://www.facebook.com/BXU.UZ'> <b>Facebook:</b> BXU.UZ</a>\n"
        "▶️ <a href='https://www.youtube.com/@bxu_uz'> <b>YouTube:</b> @bxu_uz</a>\n"
        "🌐 <a href='https://bxu.uz'> <b>Veb-sayt:</b> bxu.uz</a>\n"
        "📞 <b>Telefon:</b> +998 55 309-99-99"
    )

    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)
