from telebot.types import Message
from telebot import TeleBot

from config.settings import CLIENT_BOT_TOKEN
from customer_bot.services import CustomerLastBookingSrv, CustomerAuthorizationSrv

bot = TeleBot(CLIENT_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_bot(message: Message) -> None:
    CustomerAuthorizationSrv(
        bot=bot,
        message=message
    )


@bot.message_handler(content_types=['text'])
def menu_buttons_bot(message: Message) -> None:
    if message.text == 'Следующая бронь':
        CustomerLastBookingSrv(
            bot=bot,
            message=message
        ).execute()


if __name__ == '__main__':
    bot.polling(none_stop=True)
