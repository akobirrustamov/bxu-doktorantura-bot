# middlewares/check.py
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from keyboards.inline.subscription import check_button
from utils.misc import subscription
from aiogram.types import ReplyKeyboardRemove
from loader import bot, db


async def initialize_channels():
    channels = await db.select_all_channels()
    CHANNELSw = []
    for channel in channels:
        try:
            CHANNELSw.append(channel[2])
        except Exception as e:
            print(e)
    print(CHANNELSw)
    return CHANNELSw


class BigBrother(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        return
        # if update.message:
        #     user = update.message.from_user.id
        #     result = "ASSALOMU ALAYKUM! XUSH KELIBSIZ! BOTDAN FOYDALANISH UCHUN AVVAL KANALIMIZGA A'ZO BO'LISHINGIZ KERAK:\n"
        #     final_status = True
        #
        #     # Await the asynchronous function
        #     CHANNELSw = await initialize_channels()
        #
        #     for channel in CHANNELSw:
        #         status = await subscription.check(user_id=user, channel=channel)
        #         final_status *= status
        #         channel_info = await bot.get_chat(channel)
        #         if not status:
        #             invite_link = await channel_info.export_invite_link()
        #
        #     if not final_status:
        #         await update.message.reply(result, disable_web_page_preview=True, reply_markup=check_button)
        #         raise CancelHandler()
        #
        # elif update.callback_query:
        #     user = update.callback_query.from_user.id
        #     result = "ASSALOMU ALAYKUM! XUSH KELIBSIZ! BOTDAN FOYDALANISH UCHUN AVVAL KANALIMIZGA A'ZO BO'LISHINGIZ KERAK:\n"
        #     final_status = True
        #
        #     # Await the asynchronous function
        #     CHANNELSw = await initialize_channels()
        #
        #     for channel in CHANNELSw:
        #         status = await subscription.check(user_id=user, channel=channel)
        #         final_status *= status
        #         channel_info = await bot.get_chat(channel)
        #         if not status:
        #             invite_link = await channel_info.export_invite_link()
        #
        #     if not final_status:
        #         await update.callback_query.message.delete()
        #         await update.callback_query.message.answer(result, disable_web_page_preview=True,
        #                                                    reply_markup=check_button)
        #         raise CancelHandler()
        #
        # else:
        #     return
