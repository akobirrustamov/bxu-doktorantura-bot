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









class ChannelManagement(StatesGroup):
    WaitingForChannelName = State()  # State to wait for the channel name for adding
    WaitingForChannelID = State()  # State to wait for the channel ID for deleting/editing
    WaitingForChannelDeleteID = State()


class ChannelAddition(StatesGroup):
    WaitingForName = State()
    WaitingForID = State()
    WaitingForURL = State()


@dp.message_handler(Command("add_channel"), user_id=ADMINS)
async def start_adding_channel(message: types.Message):
    await message.answer("Please enter the name of the channel.")
    await ChannelAddition.WaitingForName.set()


@dp.message_handler(state=ChannelAddition.WaitingForName)
async def receive_channel_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['channel_name'] = message.text
    await message.answer("Please enter the ID of the channel.")
    await ChannelAddition.WaitingForID.set()


@dp.message_handler(state=ChannelAddition.WaitingForID)
async def receive_channel_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['channel_id'] = message.text
    await message.answer("Please enter the URL of the channel.")
    await ChannelAddition.WaitingForURL.set()


@dp.message_handler(state=ChannelAddition.WaitingForURL)
async def receive_channel_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['channel_url'] = message.text

        try:
            await db.add_channel(data['channel_name'], int(data['channel_id']), data['channel_url'])
            await message.answer("Channel added successfully.")
        except Exception as e:
            print(e)
            await message.answer("Failed to add channel. Please try again later.")

    await state.finish()


@dp.message_handler(Command("delete_channel"), user_id=ADMINS)
async def start_deleting_channel(message: types.Message):
    try:
        await message.answer("Please enter the ID of the channel you want to delete.")
        await ChannelManagement.WaitingForChannelDeleteID.set()
    except Exception as e:
        print(e)
        await message.answer("Something went wrong. Please try again.")


@dp.message_handler(state=ChannelManagement.WaitingForChannelDeleteID)
async def delete_channel(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            channel_id = message.text
            await db.delete_channel(int(channel_id))

        await message.answer("Channel deleted.")
    except Exception as e:
        print(e)
        await message.answer("Something went wrong. Please try again.")
    await state.finish()


@dp.message_handler(Command("show_channels"), user_id=ADMINS)
async def receive_ad_photo(message: types.Message):

    channels = await db.select_all_channels()

    channel_info = ""
    for channel in channels:
        try:
            channel_info += f"{channel[0]}-  name: {channel[1]},  id: {channel[2]}, url: {channel[3]}\n"
        except Exception as e:
            print(e)

    await message.answer(channel_info)

