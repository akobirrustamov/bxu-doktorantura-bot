import os
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from handlers.users.reseption import notify_admin_about_application
from loader import dp, db
from aiogram.dispatcher.filters import Text
import re
from handlers.users.start import send_welcome_message

BASE_DIR = "./files"


class ApplicationStates(StatesGroup):
    full_name = State()
    phone = State()
    schedule_file = State()
    diploma_file = State()
    passport_file = State()
    reference_word = State()
    reference_pdf = State()


def generate_file_path(telegram_id: int, filename: str) -> str:
    user_folder = os.path.join(BASE_DIR, str(telegram_id))
    os.makedirs(user_folder, exist_ok=True)
    return os.path.join(user_folder, filename)


@dp.callback_query_handler(Text(equals="qabul"))
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id

    # Check if the user already has an accepted application
    application = await db.get_application(telegram_id)
    if application and application.get("is_accepted"):
        await callback.message.answer(
            "✅ <b>Sizning arizangiz allaqachon qabul qilingan.</b>\n\n"
            "Agar hujjatlar bilan bog‘liq biror xatolik yoki qo‘shimcha savolingiz bo‘lsa,\n"
            "iltimos quyidagi raqam orqali bog‘laning:\n\n"
           "<b>📞 Bog‘lanish uchun ma’lumotlar:</b>\n\n"
            "👤 <b>Mas’ul shaxs:</b> Shuxrat Ostonov\n"
            "💬 <b>Telegram:</b> <a href='https://t.me/OstanovSH'>@OstanovSH</a>\n"
            "📱 <b>Telefon:</b> +998 90 512 42 44\n\n"
            "🙏 Yana murojaat qilganingiz uchun tashakkur!",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Start a new application process
    await db.create_application(telegram_id)
    await callback.message.answer("1️⃣ To‘liq F.I.Sh (Familiya, Ism, Sharifingiz) kiriting:")
    await ApplicationStates.full_name.set()
    await callback.answer()
    await callback.message.delete()



@dp.message_handler(state=ApplicationStates.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    await db.update_application_step(message.from_user.id, "full_name", message.text, 1)
    await message.answer("2️⃣ Telefon raqamingizni (+998901234567) ko‘rinishida yuboring:")
    await ApplicationStates.phone.set()



@dp.message_handler(content_types=types.ContentType.TEXT, state=ApplicationStates.phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()

    # Validate phone format: +998 followed by 9 digits
    if not re.match(r"^\+998\d{9}$", phone):
        await message.answer("❌ Telefon raqami noto‘g‘ri formatda. Iltimos, quyidagicha kiriting:\n\n📱 Masalan: +998901234567")
        return

    await db.update_application_step(
        telegram_id=message.from_user.id,
        field_name="phone",
        field_value=phone,
        status=2
    )
    await message.answer("3️⃣ Jadval faylini (Word: .doc/.docx/ .rtf) yuboring:")
    await ApplicationStates.schedule_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.schedule_file)
async def get_schedule_file(message: types.Message, state: FSMContext):
    file = message.document
    filename = file.file_name.lower()

    if not filename.endswith((".doc", ".docx", ".rtf")):
        await message.answer("❌ Faqat .doc, .docx yoki .rtf formatdagi fayllar qabul qilinadi.\n\nIltimos, mos faylni yuboring.")
        return

    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)  # ✅ Fixed here
    await db.update_application_step(message.from_user.id, "schedule_file", f"/{path}", 3)
    await message.answer("4️⃣ Magistrlik diplomini PDF formatda yuboring:")
    await ApplicationStates.diploma_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.diploma_file)
async def get_diploma_file(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)  # ✅ fixed here
    await db.update_application_step(message.from_user.id, "diploma_file", f"/{path}", 4)
    await message.answer("5️⃣ Shaxsiy pasport PDF formatda yuboring:")
    await ApplicationStates.passport_file.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.passport_file)
async def get_passport_file(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "passport_file", f"/{path}", 5)
    await message.answer("6️⃣ Ish joyidan tavsiyanoma Word (.doc/.docx) yuboring:")
    await ApplicationStates.reference_word.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.reference_word)
async def get_reference_word(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "reference_word", f"/{path}", 6)
    await message.answer("7️⃣ Ish joyidan tavsiyanoma PDF formatda yuboring:")
    await ApplicationStates.reference_pdf.set()


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=ApplicationStates.reference_pdf)
async def get_reference_pdf(message: types.Message, state: FSMContext):
    file = message.document
    path = generate_file_path(message.from_user.id, file.file_name)
    await file.download(destination=path)
    await db.update_application_step(message.from_user.id, "reference_pdf", f"/{path}", 7)
    await message.answer("✅ Arizangiz qabul qilindi. Yaqinda ko‘rib chiqiladi. Rahmat!")
    await notify_admin_about_application(message.from_user.id)
    await state.finish()
    await send_welcome_message(message)


