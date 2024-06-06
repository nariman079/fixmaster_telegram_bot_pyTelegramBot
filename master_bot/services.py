from telebot import TeleBot
from telebot.types import Message

from fixmaster_backend.client import FixMasterClient
from master_bot.buttons import get_menu_buttons

fix_master_client = FixMasterClient(
    api_key='test'
)


class MasterVerifySrv:

    def __init__(
            self,
            bot: TeleBot,
            message: Message
    ):
        self.bot = bot
        self.message = message
        self.telegram_id = message.chat.id
        self.start()

    def start(self) -> None:
        """
        Начало работы
        """
        self.bot.send_message(
            chat_id=self.telegram_id,
            text="Введеите код для авторизации."
        )
        self.bot.register_next_step_handler(self.message, self.check_code)

    def check_code(self, message: Message) -> None:
        """
        Проверка кода авторизации
        """

        self.code = message.text

        response = fix_master_client.master_verify(
            master_data={
                'code': self.code,
                'telegram_id': self.telegram_id
            }
        )

        if response.status_code == 200:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text="Вы успешно авторизовались",
                reply_markup=get_menu_buttons()
            )
        elif response.status_code == 400:
            self.bot.send_message(
                chat_id=self.telegram_id,
                text=f"Вы неправильно ввели код.\n{response.json()['message']}",
            )
            self.bot.register_next_step_handler(message, self.check_code)
        else:
            print(response.text)
            self.bot.send_message(
                text=f"Неизвестная ошибка \n{response.status_code}\nПопробуйте еще раз или обратитесь к администратору",
                chat_id=self.telegram_id
            )
            self.bot.register_next_step_handler(message, self.check_code)


class MasterCustomerSrv:
    def __init__(
            self,
            bot: TeleBot,
            message: Message
    ):
        self.bot = bot
        self.message = message
        self.telegram_id = message.chat.id

    def get_master_customers(self) -> None:
        """ Получение списка клиентов мастера """
        response = fix_master_client.master_clients(self.telegram_id)

        if response.status_code == 200:
            self.customers = response.json()['data']
        else:
            self.customers = []

    def generate_customer_list_message(self) -> None:
        """ Генерация сообщения """
        self.message_obj = "Список клиентов:\n"

        for customer in self.customers:
            self.message_obj += f'@{customer.get("username")}\n'

    def send_customer_list_on_master(self) -> None:
        """ Отправка сообщения """
        self.bot.send_message(
            chat_id=self.telegram_id,
            text=self.message_obj
        )

    def execute(self) -> None:
        """ Выполнение всех команд """
        self.get_master_customers()
        self.generate_customer_list_message()
        self.send_customer_list_on_master()


class MasterNextSessionSrv:
    def __init__(
            self,
            bot: TeleBot,
            message: Message
    ):
        self.bot = bot
        self.message = message
        self.telegram_id = message.chat.id

    def get_last_booking(self) -> None:
        """ Получение данных о следующем броне """
        response = fix_master_client.master_last_booking(self.telegram_id)

        if response.status_code == 200:
            print(response.json())
            self.message_obj = response.json()['message']
        else:
            self.message_obj = "Неизвестная ошибка"

    def send_customer_list_on_master(self) -> None:
        """ Отправка сообщения """
        self.bot.send_message(
            chat_id=self.telegram_id,
            text=self.message_obj
        )

    def execute(self) -> None:
        """ Выполнение всех команд """
        self.get_last_booking()
        self.send_customer_list_on_master()
