"""
Главный файл для запуска бота для матеров
"""

from telebot import TeleBot
from telebot.types import Message

from config.settings import MASTER_BOT_TOKEN
from master_bot.services import MasterVerifySrv, MasterCustomerSrv, MasterNextSessionSrv

bot = TeleBot(MASTER_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_bot(message: Message) -> None:
    """ Логика при запуске бота """
    MasterVerifySrv(
        bot=bot,
        message=message
    )

@bot.message_handler(content_types=['text'])
def menu_button_handler(message: Message):
    text = message.text
    if message.text == 'Список мох клиентов':
        MasterCustomerSrv(
            bot=bot,
            message=message
        ).execute()
    elif message.text == 'Следующая бронь':
        MasterNextSessionSrv(
            bot=bot,
            message=message
        ).execute()

if __name__ == "__main__":
    bot.polling(none_stop=True)
