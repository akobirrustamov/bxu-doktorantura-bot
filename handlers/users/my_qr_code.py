import aiohttp
import qrcode
import io
from aiogram import types
from aiogram.dispatcher import filters
from loader import dp, db
from handlers.users.start import send_welcome_message

API_URL = "http://localhost:8080/api/v1/agent"
# API_URL = "https://qabul.bxu.uz/api/v1/agent"

@dp.callback_query_handler(filters.Text(equals="my_qr"))
async def handle_my_qr(callback: types.CallbackQuery):
    user = callback.from_user
    payload = {
        "name": user.full_name,
        "login": str(user.id),
        "password": str(user.id)
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, json=payload) as response:
                data = await response.json()
                agent_number = data.get("agentNumber")
                agent_name = data.get("agent", {}).get("name", "Noma'lum")
                agent_link = f"https://qabul.bxu.uz/{agent_number}"

                if response.status == 200:
                    await callback.message.answer(
                        f"✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
                        f"👤 Agent ismi: *{agent_name}*\n"
                        f"🔢 Agent havolasi: *{agent_link}*",
                        parse_mode="Markdown"
                    )

                elif response.status in [409, 500]:
                    await callback.message.answer(
                        f"⚠ Siz allaqachon ro'yxatdan o'tgansiz.\n\n"
                        f"👤 Agent ismi: *{agent_name}*\n"
                        f"🔢 Agent havolasi: *{agent_link}*",
                        parse_mode="Markdown"
                    )

                # Generate QR Code
                qr_img = qrcode.make(agent_link)
                buffer = io.BytesIO()
                qr_img.save(buffer, format="PNG")
                buffer.seek(0)

                # Send QR Code as photo
                await callback.message.answer_photo(types.InputFile(buffer, filename="qr.png"), caption="📲 Agent havolangiz uchun QR kod")

        except Exception as e:
            await callback.message.answer(f"🚫 Server bilan bog'lanishda xatolik: {e}")

    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)