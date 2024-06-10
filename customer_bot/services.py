from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telebot import TeleBot

from fixmaster_backend import FixMasterClient

fix_master_client = FixMasterClient(
    api_key='test'
)



def web_app_keyboard(user_id: int): #создание клавиатуры с webapp кнопкой
    menu_buttons = ReplyKeyboardMarkup(row_width=1)
    last_booking = KeyboardButton("Следующая бронь")
    webAppTest = WebAppInfo(f"https://booking.fix-mst.ru/#/?user_id={user_id}") #создаем webappinfo - формат хранения url

    one_butt = KeyboardButton(text="Забронировать еще", web_app=webAppTest) #создаем кнопку типа webapp
    menu_buttons.row(one_butt, last_booking) #добавляем кнопки в клавиатуру

    return menu_buttons #возвращаем клавиатуру

def check_authorization(telegram_id: int | str):
    response = fix_master_client.check_customer(telegram_id)
    return response.status_code == 200


class CustomerAuthorizationSrv:
    def __init__(
            self,
            bot: TeleBot,
            message: Message

    ):
        self.telegram_id = message.chat.id
        self.bot = bot

        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Добро пожаловать в FixMaster для клиентов\n"
        )
        if not check_authorization(self.telegram_id):
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Введите код для авторизации\n"
            )
            self.bot.register_next_step_handler(message, self.start)
        else:

            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Вы уже авторизованы в системе",
                reply_markup=web_app_keyboard(self.telegram_id)
            )

    def start(self, message: Message):
        code = message.text

        response = fix_master_client.customer_verify(
            verify_data={
                'telegram_id': self.telegram_id,
                'code': code
            }
        )
        print(response.text)
        if response.status_code == 200:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text=response.json()['message'],
                reply_markup=web_app_keyboard(self.telegram_id)
            )
            return
        self.bot.send_message(
            chat_id=self.telegram_id,
            text=response.json()['message']
        )


class CustomerLastBookingSrv:
    def __init__(
            self,
            bot: TeleBot,
            message: Message

    ):
        self.telegram_id = message.chat.id
        self.bot = bot

    def get_last_booking(self) -> None:
        """ Получение последней брони клиента """
        response = fix_master_client.customer_last_booking(
            telegram_id=self.telegram_id
        )

        self.bot.send_message(
            chat_id=self.telegram_id,
            text=response.json()['message']
        )


    def execute(self) -> None:
        """ Выполнение команд """
        self.get_last_booking()


