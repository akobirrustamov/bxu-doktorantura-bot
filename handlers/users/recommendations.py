from aiogram import types
from aiogram.dispatcher import filters
from loader import dp, db
from handlers.users.start import send_welcome_message
from datetime import datetime


@dp.callback_query_handler(filters.Text(equals="recommendations"))
async def handle_recommendations(callback: types.CallbackQuery):
    user = callback.from_user
    phone = str(user.id)

    # Step 1: Find agent by phone
    res = await db.get_agent(phone)

    if res:
        agent_id = res["id"]
        agent_name = res.get("name", "Noma'lum")

        abuturients = await db.get_agent_abuturients(agent_id)

        # Format current date and time as: 12.04.2025 12:00
        now = datetime.now().strftime("%d.%m.%Y %H:%M")

        if not abuturients:
            await callback.message.answer(f"📭 {agent_name} tomonidan hali abituriyent tavsiya qilinmagan.")
        else:
            msg = (
                f"📋 *{agent_name}* tomonidan tavsiya qilingan abituriyentlar "
                f"(_{now} holatiga ko‘ra_):\n\n"
            )
            for i, abu in enumerate(abuturients, 1):
                first_name = abu.get("first_name", "Ism yo'q")
                last_name = abu.get("last_name", "")
                msg += f"{i}. {first_name} {last_name}\n"

            msg += f"\n🧮 Umumiy soni: {len(abuturients)} ta"
            await callback.message.answer(msg, parse_mode="Markdown")

    else:
        await callback.message.answer("❌ Siz ro'yxatdan o'tmagansiz.")

    await callback.answer()
    await callback.message.delete()
    await send_welcome_message(callback.message)
