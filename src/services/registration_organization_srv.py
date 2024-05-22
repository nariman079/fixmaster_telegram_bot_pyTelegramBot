from telebot import TeleBot
from telebot.types import Message, BotCommand
from src.services.fixmaster_backend import FixMasterClient


fix_master_client = FixMasterClient(
    api_key='test'
)

class GetProfileTelebot:
    def __init__(self, bot: TeleBot, message: Message):
        self.bot = bot
        self.bot.register_next_step_handler(message, self.get_number)

    def get_number(self, message: Message):
        """ Получение номера телефона """

        try:
            self.phone_number, self.user_keyword = message.text.split(' ')

        except:
            self.bot.send_message(
                chat_id=message.chat.id,
                text="Вы ввели неправильный формат\nПопробуйте еще раз.\nПример: 8999 word"
            )
            self.bot.register_next_step_handler(message, self.get_number)
            return

        response_data = fix_master_client.get_profile(
            phone_number=self.phone_number,
            user_keyword=self.user_keyword,
            telegram_id=message.chat.id,
            username=message.from_user.username
        )
        self.bot.send_message(
            chat_id=message.chat.id,
            text=response_data.get('message')
        )

