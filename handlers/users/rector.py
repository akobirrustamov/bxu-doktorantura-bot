from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import CallbackQuery

from loader import dp, db
from handlers.users.start import send_welcome_message
from datetime import datetime
from handlers.users.start import send_welcome_message


@dp.callback_query_handler(filters.Text(equals="grant"))
async def handle_rector_grant(callback: types.CallbackQuery):

    print(callback.data)

    text1 = (
        "<b>🎓 Rektor Granti haqida</b>\n\n"
        "Rektor granti — bu <b>Buxoro Xalqaro Universiteti</b>da o‘qishni xohlovchi "
        "iqtidorli abituriyentlar uchun ajratiladigan maxsus imtiyozdir.\n\n"
        "📌 Ushbu grantga quyidagi shartlarni bajargan nomzodlar da’vogarlik qilishi mumkin:\n"
        "• Universitetga o‘qishga <b>qabul qilinishdan oldin</b> yoki <b>qabul qilinganidan so‘ng</b>\n"
        "• IELTS imtihonidan <b>kamida 7.5 yoki undan yuqori</b> natijaga ega bo‘lish\n\n"
        "🎯 Bu grant iqtidorli yoshlarni rag‘batlantirish, ularning xalqaro darajadagi "
        "bilimlarini qadrlash maqsadida ajratiladi.\n\n"
        "📢 Agar sizda yuqori til bilimi va katta maqsadlar bo‘lsa — <b>Rektor granti aynan siz uchun!</b>"
        "📢 Rasmiy yangiliklar uchun kuzatib boring: <a href='https://t.me/bxu_uz'>@bxu_uz</a>"
    )
    text2 = (
        "<b>💰 Rektor Stipendiyasi haqida</b>\n\n"
        "Rektor stipendiyasi — bu <b>IELTS natijasi 6.0 yoki undan yuqori</b> bo‘lgan "
        "talabalar uchun mo‘ljallangan <b>moliya yengilligi</b>dir.\n\n"
        "📌 Shartlar:\n"
        "• IELTS darajangiz <b>6.0 yoki undan yuqori</b> bo‘lishi kerak\n"
        "• Ushbu holatda siz <b>shartnoma to‘lovidan 5 million so‘m</b> chegirmaga ega bo‘lasiz\n\n"
        "🎯 Bu stipendiya talabalarni til o‘rganishga rag‘batlantirish va ularning akademik salohiyatini "
        "qo‘llab-quvvatlash uchun ajratiladi.\n\n"
        "📢 IELTS natijangiz bor va universitetda o‘qishni rejalashtirgan bo‘lsangiz — "
        "<b>Rektor stipendiyasi siz uchun ajoyib imkoniyat!</b>"
        "📢 Rasmiy yangiliklar uchun kuzatib boring: <a href='https://t.me/bxu_uz'>@bxu_uz</a>"

    )
    text3 = (
        "<b>🎓 Davlat Granti (nodavlat OTMlar uchun)</b>\n\n"
        "⚡️ <b>Rasman:</b> Xorijiy va nodavlat oliy ta’lim muassasalariga <b>1200 ta davlat granti</b> ajratildi.\n\n"
        "📌 Ushbu grantlar quyidagi ta’lim muassasalariga tegishli:\n"
        "• O‘zbekistonda faoliyat yuritayotgan <b>xorijiy universitetlar</b> va ularning filiallari\n"
        "• <b>Nodavlat oliy ta’lim tashkilotlari</b>\n\n"
        "🎯 Bu tashabbus O‘zbekistonda sifatli ta’limni qo‘llab-quvvatlash va iqtidorli talabalarni moliyaviy rag‘batlantirish maqsadida amalga oshirilmoqda.\n\n"
    )

    await callback.message.answer(text1, parse_mode="HTML")
    await callback.message.answer(text2, parse_mode="HTML")
    await callback.message.answer(text3, parse_mode="HTML")
    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)



@dp.callback_query_handler(filters.Text(equals="guide"))
async def send_guide(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "<b>📌 Botdan foydalanish yo‘riqnomasi</b>\n\n"
        "Abuturientlarni sizga maxsus taqdim etilgan QR kod orqali ro'yxatdan o'tib unversitetimiz talabasi bo'lgan har bir ta'lim oluvchi uchun aloxida rag'batlantirish beriladi."
    )
    await  callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)