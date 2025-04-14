from aiogram import types
from aiogram.dispatcher import filters
from loader import dp
from handlers.users.start import send_welcome_message


@dp.callback_query_handler(filters.Text(equals="contact_us"))
async def handle_contact_us(callback: types.CallbackQuery):
    text = (
        "<b>📞 Bog‘lanish uchun ma’lumotlar:</b>\n\n"
        "👤 <b>Mas’ul shaxs:</b> Shuxrat Ostonov\n"
        "💬 <b>Telegram:</b> <a href='https://t.me/OstanovSH'>@OstanovSH</a>\n"
        "📱 <b>Telefon:</b> +998 90 512 42 44\n\n"
        "Agar sizda qabul jarayoni yoki hujjatlar bo‘yicha savollar bo‘lsa, bemalol bog‘lanishingiz mumkin. "
        "Yordam berishdan mamnunmiz! 😊"
    )

    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)

