import base64
import dataclasses
import re
from io import BytesIO

from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from fixmaster_backend import FixMasterClient
from config.settings import s3, bucket_name

fix_master_client = FixMasterClient(
    api_key='test'
)

organization_menu_markup = ReplyKeyboardMarkup()

master_list = KeyboardButton("📃 Список мастеров")
client_list = KeyboardButton('👥 Список клиентов')
add_master = KeyboardButton('➕ Добавить мастера')
add_service = KeyboardButton('➕ Добавить услугу')

organization_menu_markup.add(master_list)
organization_menu_markup.add(client_list)
organization_menu_markup.add(add_master)
organization_menu_markup.add(add_service)


@dataclasses.dataclass(slots=True, frozen=True)
class OrganizationData:
    phone_number: str
    main_image: bytes
    organization_type: int
    begin_time: str
    end_time: str
    work_schedule: str
    address: str


def get_organization(telegram_id: str):
    response = fix_master_client.get_organization_by_telegram_id(
        telegram_id
    )
    print(response.status_code)
    if response.status_code == 200:
        return False
    else:
        return True


def is_phone_number(text: str):
    phone_pattern = re.compile(r'^\+?\d{1,4}?[-.\s]?(\(?\d{1,4}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
    return bool(phone_pattern.match(text))


def get_organization_type_id(title: str) -> int:
    organization_type_id = list(filter(
        lambda x: x['title'] == title,
        fix_master_client.get_organization_types()['data']
    ))[0]
    return organization_type_id['id']


def generate_organization_types_buttons() -> ReplyKeyboardMarkup:
    """
    Получение кнопок для выбора типа организации
    """
    markup = ReplyKeyboardMarkup()
    organization_types = fix_master_client.get_organization_types()
    print(organization_types)
    for t in organization_types['data']:
        markup.add(KeyboardButton(text=f"{t['title']}"))
    return markup


def generate_all_times_buttons() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2)
    [markup.add(KeyboardButton(f"{i}:00")) for i in range(4, 20)]
    return markup


class GetProfileTelebot:
    def __init__(self, bot: TeleBot, message: Message):
        self.bot = bot
        self.bot.register_next_step_handler(message, self.get_number)

    def get_number(self, message: Message):
        """ Получение данных телефона """

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


class OrganizationCreate:
    """ Логика создания организаций """

    def __init__(self, bot: TeleBot, message: Message):
        self.bot = bot
        self.message = message
        self.organization = dict()
        if get_organization(self.message.chat.id):
            self._send(
                text="Вы уже зарегистрированы в системе",
                reply_markup=organization_menu_markup
            )

            return
        self.start(message)

    def _send(self, text, **kwargs):
        message = self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )
        return message

    def _step(self, message, func):
        self.bot.register_next_step_handler(message, func)

    def start(self, message):
        self._send(
            text="Введите название \n",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_title)

    def get_title(self, message: Message):
        self.organization['title'] = message.text
        self._send(
            text="Введите номер телефона горячей линии организации\nПример: 82930703023",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_number)

    def get_number(self, message: Message):
        while True:
            try:
                self.organization['contact_phone'] = message.text
                if not is_phone_number(self.organization['contact_phone']):
                    self._send(text="Введите корректный номер телефона")
                    self._step(message, self.get_number)
                    return

                # next msg
                self._send(
                    text="Введите главное изображене"
                )
                self._step(message, self.get_main_image)
                break
            except TypeError:
                self._send(
                    text="Введите корректный номер телефона"
                )
                self._step(message, self.get_number)
                return

    def get_main_image(self, message: Message):
        while True:
            try:
                download_message = self._send(
                    'Загружаем...'
                )
                file_id = message.photo[-1].file_id
                file_info = self.bot.get_file(file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                with open(file_info.file_path, 'wb') as file:
                    file.write(downloaded_file)

                s3.upload_file(
                    Filename=file_info.file_path,
                    Bucket=bucket_name,
                    Key=file_info.file_path
                )

                self.organization[
                    'main_image_url'] = f"https://s3.timeweb.cloud/dea7d49e-ba387d71-db58-4c7f-8b19-e217f5775615/{file_info.file_path}"
                break

            except Exception as _:
                print(_.args)
                self._send(
                    text="Введите корректное изображение",
                )
                self._step(message, self.get_main_image)
                return
        # msg
        self.bot.edit_message_text(
            chat_id=download_message.chat.id,
            message_id=download_message.id,
            text="Отлично!\n",
        )
        self._send(
            text='Теперь выберите тип вашей организации!',
            reply_markup=generate_organization_types_buttons()
        )
        self._step(message, self.get_organization_type)

    def get_organization_type(self, message: Message):
        self.organization['organization_type_id'] = get_organization_type_id(message.text)

        # msg
        self._send(
            text="Выберите начало рабочего дня",
            reply_markup=generate_all_times_buttons()
        )
        self._step(message, self.get_begin_time)

    def get_begin_time(self, message: Message):
        self.organization['time_begin'] = message.text

        # msg
        self._send(
            text="А теперь выберите конец рабочего дня",
            reply_markup=generate_all_times_buttons()
        )
        self._step(message, self.get_end_time)

    def get_end_time(self, message: Message):
        self.organization['time_end'] = message.text

        # msg
        self._send(
            text="Введите график работы\nПример: 5/2, ПН-ПТ и тд.",
            reply_markup=ReplyKeyboardRemove()
        )
        self._step(message, self.get_work_schedule)

    def get_work_schedule(self, message: Message):
        self.organization['work_schedule'] = message.text

        # msg
        self._send(
            text="Введите адрес организации",
            reply_markup=ReplyKeyboardRemove()
        )
        self._step(message, self.get_address)

    def get_address(self, message: Message):
        self.organization['address'] = message.text

        self._send(
            text="Отлично! Заявка на верификацию отправлена!\nЖдите ответа",
            reply_markup=ReplyKeyboardRemove()
        )
        print(self.organization)
        self.organization['telegram_id'] = self.message.chat.id
        fix_master_client.create_organization(self.organization)
