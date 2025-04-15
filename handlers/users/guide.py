import os
from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InputFile
from loader import dp
from handlers.users.start import send_welcome_message

BASE_DIR = "./files/example"

@dp.callback_query_handler(filters.Text(equals="guide"))
async def handle_contact_us(callback: types.CallbackQuery):
    text = (
        "<b>📞 BUXORO XALQARO UNIVERSITETI</b>\n"
        "<b>📚 Doktorantura uchun ariza topshirish bo‘yicha ma’lumotlar:</b>\n\n"
        "Hurmatli nomzod, qabul jarayonini muvaffaqiyatli yakunlash uchun quyidagi hujjatlarni tayyorlab, topshirishingiz kerak:\n\n"
        "✅ <b>To‘liq F.I.Sh</b> — Familiya, Ism, Sharifingiz\n"
        "📱 <b>Telefon raqam</b> — (+998901234567) ko‘rinishida\n"
        "📄 <b>Jadval fayli</b> — Word hujjati formatida (.doc, .docx yoki .rtf)\n"
        "🎓 <b>Magistrlik diplomi</b> — PDF formatda (.pdf)\n"
        "🆔 <b>Shaxsiy pasport nusxasi</b> — PDF formatda\n"
        "🏢 <b>Ish joyidan tavsiyanoma (PDF)</b> — .pdf formatda\n\n"
        "📝 Hujjatlar to‘liq va to‘g‘ri bo‘lishi kerak. Har qanday savollar bo‘yicha biz bilan bog‘lanishingiz mumkin.\n\n"
        "📧 E-mail: info@bxu.uz\n"
        "🌐 Veb-sayt: https://bxu.uz\n"
        "☎️ Telefon: +998 90 512 42 44\n"
        "💬 <b>Telegram:</b> <a href='https://t.me/OstanovSH'>@OstanovSH</a>\n\n"
        "📂 Quyida namunaviy fayllar bilan tanishing:"
    )

    await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

    # 1. Send example files
    if os.path.exists(BASE_DIR):
        for filename in os.listdir(BASE_DIR):
            file_path = os.path.join(BASE_DIR, filename)
            if os.path.isfile(file_path):
                await callback.message.answer_document(InputFile(file_path), caption=f"📎 <b>Namuna:</b> {filename}", parse_mode="HTML")

    # 2. Continue to main menu
    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)
