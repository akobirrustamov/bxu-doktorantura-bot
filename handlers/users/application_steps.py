import os
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.users.reseption import notify_admin_about_application
from handlers.users.start import send_welcome_message
from loader import dp, db

BASE_DIR = "./files"

class ApplicationStates(StatesGroup):
    full_name = State()
    phone = State()
    schedule_file = State()
    diploma_file = State()
    passport_file = State()
    reference_word = State()


def generate_file_path(telegram_id: int, filename: str) -> str:
    user_folder = os.path.join(BASE_DIR, str(telegram_id))
    os.makedirs(user_folder, exist_ok=True)
    return os.path.join(user_folder, filename)


def step_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("⬅️ Orqaga", callback_data="back"),
        InlineKeyboardButton("📛 Qabulni to‘xtatish", callback_data="cancel")
    )


@dp.callback_query_handler(Text(equals="qabul"))
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    application = await db.get_application(telegram_id)
    if application and application.get("is_accepted"):
        await callback.message.answer(
            "✅ <b>Sizning arizangiz allaqachon qabul qilingan.</b>\n\n"
            "Agar hujjatlar bilan bog‘liq biror xatolik yoki qo‘shimcha savolingiz bo‘lsa,\n"
            "iltimos quyidagi raqam orqali bog‘laning:\n\n"
            "<b>📞 Bog‘lanish uchun ma’lumotlar:</b>\n\n"
            "👤 <b>Mas‘ul shaxs:</b> Shuxrat Ostonov\n"
            "💬 <b>Telegram:</b> <a href='https://t.me/OstanovSH'>@OstanovSH</a>\n"
            "📱 <b>Telefon:</b> +998 90 512 42 44\n\n"
            "🙍 Yana murojaat qilganingiz uchun tashakkur!",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await db.create_application(telegram_id)
    await callback.message.answer("1⃣ To‘liq F.I.Sh (Familiya, Ism, Sharifingiz) kiriting:", reply_markup=step_keyboard())
    await ApplicationStates.full_name.set()
    await callback.answer()
    await callback.message.delete()


@dp.callback_query_handler(Text(equals="cancel"), state='*')
async def cancel_application(callback: types.CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id
    await db.delete_application(telegram_id)
    await state.finish()

    await callback.message.answer(
        "📛 <b>Ariza topshirish jarayoni butunlay to‘xtatildi.</b>\n\n"
        "Agar savollaringiz yoki muammolaringiz bo‘lsa, quyidagi ma’lumotlar orqali biz bilan bog‘laning:\n\n"
        "👤 <b>Mas‘ul shaxs:</b> Shuxrat Ostonov\n"
        "💬 <b>Telegram:</b> <a href='https://t.me/OstanovSH'>@OstanovSH</a>\n"
        "📞 <b>Telefon:</b> +998 90 512 42 44\n\n"
        "🤝 E’tiboringiz uchun rahmat!",
        parse_mode="HTML"
    )

    await send_welcome_message(callback.message)


@dp.callback_query_handler(Text(equals="back"), state=ApplicationStates.phone)
async def back_to_fullname(callback: types.CallbackQuery):
    await callback.message.answer("1⃣ Iltimos, F.I.Sh ni qayta kiriting:", reply_markup=step_keyboard())
    await ApplicationStates.full_name.set()


@dp.callback_query_handler(Text(equals="back"), state=ApplicationStates.schedule_file)
async def back_to_phone(callback: types.CallbackQuery):
    await callback.message.answer("2⃣ Telefon raqamingizni qayta kiriting:", reply_markup=step_keyboard())
    await ApplicationStates.phone.set()


@dp.callback_query_handler(Text(equals="back"), state=ApplicationStates.diploma_file)
async def back_to_schedule(callback: types.CallbackQuery):
    await callback.message.answer("3⃣ Jadval faylini qayta yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.schedule_file.set()


@dp.callback_query_handler(Text(equals="back"), state=ApplicationStates.passport_file)
async def back_to_diploma(callback: types.CallbackQuery):
    await callback.message.answer("4⃣ Magistrlik diplomini qayta yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.diploma_file.set()


@dp.callback_query_handler(Text(equals="back"), state=ApplicationStates.reference_word)
async def back_to_passport(callback: types.CallbackQuery):
    await callback.message.answer("5⃣ Pasport faylini qayta yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.passport_file.set()


@dp.message_handler(state=ApplicationStates.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    await db.update_application_step(message.from_user.id, "full_name", message.text, 1)
    await message.answer("2⃣ Telefon raqamingizni (+998901234567) ko‘rinishida yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.phone.set()


@dp.message_handler(content_types=types.ContentType.TEXT, state=ApplicationStates.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+998\d{9}$", phone):
        await message.answer("❌ Telefon raqami noto‘g‘ri formatda. Masalan: +998901234567")
        return
    await db.update_application_step(message.from_user.id, "phone", phone, 2)
    example_path = "./files/example/jadval.rtf"
    if os.path.exists(example_path):
        await message.answer_document(
            types.InputFile(example_path),
            caption="📄 <b>Namuna:</b> Siz yuboradigan jadval <i>shu ko‘rinishda</i> bo‘lishi kerak.",
            parse_mode="HTML"
        )

    await message.answer("3⃣ Endi o‘zingizning jadval faylingizni (.doc/.docx/.rtf) yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.schedule_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.schedule_file)
async def get_schedule_file(message: types.Message, state: FSMContext):
    file = message.document
    filename = file.file_name.lower()
    if not filename.endswith((".doc", ".docx", ".rtf")):
        await message.answer("❌ Faqat .doc/.docx/.rtf fayllar qabul qilinadi.")
        return
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "schedule_file", f"/{path}", 3)
    await message.answer("4⃣ Magistrlik diplomini PDF formatda yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.diploma_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.diploma_file)
async def get_diploma_file(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "diploma_file", f"/{path}", 4)
    await message.answer("5⃣ Pasport faylini PDF formatda yuboring:", reply_markup=step_keyboard())
    await ApplicationStates.passport_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.passport_file)
async def get_passport_file(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "passport_file", f"/{path}", 5)
    await message.answer(
        "6⃣ <b>Rektor nomiga tavsiyanoma xatini yuboring</b>\n\n"
        "Iltimos, quyidagi ma’lumotlarga asoslangan holda rasmiy xatni tayyorlab, Word formatida (.doc/.docx) yuboring:\n\n"
        "📌 <b>Kimga:</b> Buxoro Xalqaro Universiteti Rektori\n"
        "📌 <b>Ismi:</b> Psixologiya fanlari doktori, professor Baratov Sharif Ramazonovich\n\n"
        "Xat rasmiy tashkilot (ish joyingiz) tomonidan yozilgan bo‘lishi va imzo/pechat bilan tasdiqlangan bo‘lishi lozim.",
        parse_mode="HTML",
        reply_markup=step_keyboard()
    )

    await ApplicationStates.reference_word.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.reference_word)
async def get_reference_word(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "reference_word", f"/{path}", 6)
    await message.answer("✅ Arizangiz qabul qilindi. Yaqinda ko‘rib chiqiladi. Rahmat!")
    await notify_admin_about_application(message.from_user.id)
    await state.finish()
    await send_welcome_message(message)
