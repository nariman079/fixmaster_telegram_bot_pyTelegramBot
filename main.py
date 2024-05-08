from telebot import TeleBot, types

from config import settings

bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message: types.Message):
    """ Сообщение при запуске бота """
    ...

