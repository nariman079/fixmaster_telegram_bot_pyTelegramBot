"""
Main file
"""
from telebot import TeleBot, types

from config import settings
from organization_bot.src.services import OrganizationCreate


bot = TeleBot(settings.ORGANIZATION_BOT_TOKEN)  # type: ignore


@bot.message_handler(commands=['start'])
def main(message: types.Message):
    """
    Сообщение при запуске бота
    """
    bot.send_message(chat_id=message.chat.id,
                     text="Добро пожаловать а FixMaster для организаций",
                     )
    OrganizationCreate(bot, message)





if __name__ == '__main__':
    bot.polling(none_stop=True)