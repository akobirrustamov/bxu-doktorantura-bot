from aiogram import types
from aiogram.types import ContentType
from loader import dp
import requests


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text+"\n nima gap!")

