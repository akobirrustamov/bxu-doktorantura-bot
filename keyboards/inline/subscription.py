from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import db


async def generate_channel_buttons():
    channels = await db.select_all_channels()

    button_data = []
    for channel in channels:
        try:
            button_data.append(
                InlineKeyboardButton(text=channel[1], url=channel[3])
            )
        except Exception as e:
            print(e)
    return button_data


async def create_inline_keyboard():
    buttons = await generate_channel_buttons()
    buttons.append(
        InlineKeyboardButton(text="✅Obunani tekshirish", callback_data="check_subs")
    )

    check_button = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return check_button

# Now you can use create_inline_keyboard() to get the dynamically generated inline keyboard
check_button = create_inline_keyboard()
