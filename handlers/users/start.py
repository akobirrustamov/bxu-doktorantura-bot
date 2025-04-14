import asyncpg
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, db, bot
from data.config import ADMINS


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    try:

        user = await db.add_user(telegram_id=message.from_user.id,
                                 full_name=message.from_user.full_name,
                                 username=message.from_user.username)
    except asyncpg.exceptions.UniqueViolationError:
        user = await db.select_user(telegram_id=message.from_user.id)

    await message.answer("Xush kelibsiz!")

    # ADMINGA xabar beramiz
    count = await db.count_users()
    msg = f"{user[1]} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
    await send_welcome_message(message)
    await bot.send_message(chat_id=ADMINS[0], text=msg)

async def send_welcome_message(message: Message):
    text = (
        "🤝 *XUSH KELIBSIZ!*\n\n"
        "🏛 *BUXORO XALQARO UNIVERSITETI RIVOJIGA O'Z HISSAMNI QO'SHAMAN*"
    )
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅ Qabul", url="https://qabul.bxu.uz"),
        InlineKeyboardButton("🔲 Mening QR kodim", callback_data="my_qr"),
        InlineKeyboardButton("Ta'lim yo'nalishlari", callback_data="directions"),
        InlineKeyboardButton("📸 Universitet haqida (Instagram)", url="https://www.instagram.com/bxu.uz/"),
        InlineKeyboardButton("👥 Men tavsiya qilganlar", callback_data="recommendations"),
        InlineKeyboardButton("💰 Grantlar", callback_data="grant"),
        InlineKeyboardButton("🤖 Yoriqnoma", callback_data="guide"),
        InlineKeyboardButton("☎️ Biz bilan bog'lanish", callback_data="contact_us"),

    )
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
