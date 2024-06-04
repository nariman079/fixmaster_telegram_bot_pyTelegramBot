"""
Main file
"""
import logging
from telebot import TeleBot, types

from config import settings
from organization_bot.src.services import GetProfileTelebot

bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)  # type: ignore

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('bot.log')
handler.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
def main(message: types.Message):
    """
    Сообщение при запуске бота
    """
    bot.send_message(chat_id=message.chat.id,
                     text="Введите номер телефона, на которую оформили бронь")
    GetProfileTelebot(bot, message)


@bot.message_handler(commands=['my_chat_id'])
def my_chat_id(message: types.Message):
    print(message.chat.id)
    bot.send_message(chat_id=message.chat.id,
                     text=f"{message.chat.id}")


if __name__ == '__main__':
    bot.polling(none_stop=True)
