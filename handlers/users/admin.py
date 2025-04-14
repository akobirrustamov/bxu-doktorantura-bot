import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup

from data.config import ADMINS
from loader import dp, db, bot


class AdCreation(StatesGroup):
    WaitingForText = State()  # State to wait for the text of the ad
    WaitingForPhoto = State()  # State to wait for the photo of the ad


@dp.message_handler(Command("reklama"), user_id=ADMINS)
async def start_ad_creation(message: types.Message):
    await message.answer("Please enter the text for the advertisement.")
    await AdCreation.WaitingForText.set()


@dp.message_handler(state=AdCreation.WaitingForText)
async def receive_ad_text(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['text'] = message.text
        await message.answer("Please send the image for the advertisement.")
        await AdCreation.WaitingForPhoto.set()
    except Exception as e:
        print(e)
        await message.answer("Something went wrong. Please try again.")


@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=AdCreation.WaitingForPhoto)
async def receive_ad_photo(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['photo'] = message.photo[-1].file_id
        users = await db.select_all_users()

        # Send the ad to all users
        for user in users:
            try:
                user_id = user[3]
                await bot.send_photo(chat_id=user_id, photo=data['photo'], caption=data['text'])
                await asyncio.sleep(0.05)

            except Exception as e:
                print(e)


        await message.answer("Advertisement sent to all users.")
    except Exception as e:
        print(e)
        await message.answer("Something went wrong. Please try again.")
    await state.finish()


# Handle the cancel command in case the admin wants to cancel the ad creation
@dp.message_handler(text="cancel", state="*")
async def cancel_ad_creation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Advertisement creation canceled.")






