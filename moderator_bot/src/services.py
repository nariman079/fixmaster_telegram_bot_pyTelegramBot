from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from fixmaster_backend import FixMasterClient

fix_master_client = FixMasterClient(
    api_key='test'
)


class ModeratorCreate:
    """ Логика создания организаций """

    def __init__(self, bot: TeleBot, message: Message):
        self.bot = bot
        self.message = message
        self.moderator = dict()
        self.moderator['telegram_id'] = message.chat.id
        self._send(
            text="Введите логин \n",
            reply_markup=ReplyKeyboardRemove()
        )
        self.start(message)

    def _send(self, text, **kwargs):
        self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )

    def _step(self, message, func):
        self.bot.register_next_step_handler(message, func)

    def start(self, message):
        
        self._step(
            message,
            self.get_login
        )

    def get_login(self, message: Message):
        login = message.text
        self.moderator['login'] = login
        self._send(
            text="Введите код"
        )
        self._step(
            message, self.get_code
        )

    def get_code(self, message: Message):
        while True:
            code = message.text
            self.moderator['code'] = code
            response = fix_master_client.get_moderator(
                    self.moderator
                )
            
            print(response.status_code)
            print(response.json())
            if response.json():
                if response.json()['code'] == 201:
                    self._send(
                        text=response.json()['message']
                    )
                    break
                elif response.json()['code'] == 404:
                    self._send(
                        text=response.json()['message']
                    )
                    self._step(
                        message,
                        self.get_code
                    )
                    return
                elif response.json()['code'] == 400:
                    self._send(
                        text=response.json()['message']
                    )
                    self._send(
                        text="Введите логин еще раз"
                    )
                    self._step(
                        message,
                        self.get_login
                    )
                    return
                elif response.json()['code'] == 440:
                    self._send(
                        text=response.json()['message']
                    )
                    return
                
                else:
                    self._send(
                        text=response.json()['message']
                    )
                    self._step(
                        message,
                        self.get_code
                    )
                    return



class VerifiedOrganization:
    def __init__(self, organization_id: int):
        self.organization_id = organization_id

    def verify_organization(self, verify: bool):
        fix_master_client.verify_organization(
            organization_id=self.organization_id,
            verify=verify
        )
    
