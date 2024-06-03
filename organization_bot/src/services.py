import dataclasses
import re

from telebot import TeleBot
from telebot.types import (Message,
                           ReplyKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardRemove,
                           InlineKeyboardButton,
                           InlineKeyboardMarkup, CallbackQuery)

from config.redis import dict_get, dict_set
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


def get_organization_data(telegram_id: str | int) -> dict:
    response = fix_master_client.get_organization_data_by_telegram_id(
        telegram_id
    )
    if response.status_code == 200:
        print(response.status_code)
        return response.json()['data']

    return response.json()


def is_organization_exist(telegram_id: str) -> bool:
    response = fix_master_client.get_organization_by_telegram_id(
        telegram_id
    )
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


def generate_all_times_buttons(default_time=4) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2)
    [markup.add(KeyboardButton(f"{i}:00")) for i in range(default_time, 20)]
    return markup


def generate_service_min_time_button():
    markup = ReplyKeyboardMarkup(row_width=2)
    [
        markup.add(
            KeyboardButton(f"{i}0 мин")
        ) for i in range(1, 10)
    ]
    return markup

def generate_master_detail_data(master_data: dict) -> str:
    result_message = ""
    master_data.pop('services')
    for key, value in master_data.items():
        result_message += f"{key}: {value}\n"
    print(result_message)
    return result_message





def get_master_services(master_id: int):
    response = fix_master_client.get_master_services(
        master_id
    )
    if response.status_code == 200:
        return response.json()['data']
    return response.text


def get_service_detail(service_id: int):
    response = fix_master_client.get_service_detail(
        service_id
    )
    if response.status_code == 200:
        return response.json()['data']
    return response.text


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
        if is_organization_exist(self.message.chat.id):
            self._send(
                text="Вы уже зарегистрированы в системе",
                reply_markup=organization_menu_markup
            )
            self._send(
                text=get_organization_data(self.message.chat.id).get('title', 'Cle')
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


class MasterListSrv:

    def __init__(self, bot: TeleBot, message: Message, call: CallbackQuery = None):
        self.bot = bot
        self.message = message
        self.call = call

    def _send(self, text, **kwargs):
        message = self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )
        return message

    def generate_master_list_buttons(self):
        self.master_list = get_organization_data(self.message.chat.id)['masters']
        self.master_list_buttons = InlineKeyboardMarkup()
        [self.master_list_buttons.add(InlineKeyboardButton(text=f"{i.get('name')} {i.get('surname')}",
                                                           callback_data=f"masterdetail_{i.get('id')}"))
         for i in self.master_list]

    def execute(self):

        self.generate_master_list_buttons()
        if self.call:
            self.bot.edit_message_text(
                text=f"Список мастеров:\nУ вас {len(self.master_list)} мастеров",
                reply_markup=self.master_list_buttons,
                message_id=self.message.id,
                chat_id=self.message.chat.id
            )
        else:
            self._send(
                text=f"Список мастеров:\nУ вас {len(self.master_list)} мастеров",
                reply_markup=self.master_list_buttons,
            )
        return None


class MasterDetailSrv:

    def __init__(
            self,
            bot: TeleBot,
            call: CallbackQuery,
            master_id: int
    ):
        self.bot = bot
        self.message = call.message
        self.call_data = call.data
        self.master_id = master_id

    def _send(self, text, **kwargs):
        message = self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )
        return message

    def get_master_data(self):
        try:
            self.master_data = list(filter(
                lambda x: x['id'] == self.master_id,
                get_organization_data(self.message.chat.id)['masters']
            ))[0]
        except IndexError:
            self.master_data = None

    def generate_master_detail_buttons(self):
        self.master_detail_buttons = InlineKeyboardMarkup()
        edit_button = InlineKeyboardButton('Изменить', callback_data=f"masteredit_{self.master_data.get('id')}")
        delete_button = InlineKeyboardButton('Удалить', callback_data=f"masterdelete_{self.master_data.get('id')}")
        master_services_button = InlineKeyboardButton('Список улуг',
                                                      callback_data=f"masterservices_list_{self.master_data.get('id')}")
        back_button = InlineKeyboardButton(text='Назад', callback_data=f"backmasterlist_{self.message.chat.id}")
        self.master_detail_buttons.add(edit_button)
        self.master_detail_buttons.add(delete_button)
        self.master_detail_buttons.add(master_services_button)
        self.master_detail_buttons.add(back_button)

    def execute(self):
        self.get_master_data()
        if self.master_data:
            self.generate_master_detail_buttons()
            self.bot.edit_message_text(
                text=generate_master_detail_data(self.master_data),
                reply_markup=self.master_detail_buttons,
                message_id=self.message.id,
                chat_id=self.message.chat.id
            )

        return None


class MasterDeleteSrv:

    def __init__(
            self,
            bot: TeleBot,
            call: CallbackQuery,
            master_id: int
    ):
        self.bot = bot
        self.message = call.message
        self.call_data = call.data
        self.master_id = master_id

    def generate_master_list_buttons(self):
        self.master_list = get_organization_data(self.message.chat.id)['masters']
        self.master_list_buttons = InlineKeyboardMarkup()
        [self.master_list_buttons.add(InlineKeyboardButton(text=f"{i.get('name')} {i.get('surname')}",
                                                       callback_data=f"masterdetail_{i.get('id')}"))
         for i in self.master_list]

    def delete_master(self):
        self.bot.edit_message_text(
            text="Удаляем мастера",
            message_id=self.message.id,
            chat_id=self.message.chat.id
        )
        fix_master_client.delete_master(
            self.master_id
        )

    def execute(self):
        self.delete_master()
        self.generate_master_list_buttons()
        self.bot.edit_message_text(
            text=f"Список мастеров:\nУ вас {len(self.master_list)} мастеров",
            reply_markup=self.master_list_buttons,
            message_id=self.message.id,
            chat_id=self.message.chat.id
        )
        return None


class MasterCreateSrv:

    def __init__(self, bot: TeleBot, message: Message):
        self.bot = bot
        self.message = message
        self.master_data = dict()

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
            text="Введите имя мастера\n",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_name)

    def get_name(self, message: Message):
        self.master_data['name'] = message.text
        self._send(
            text="Введите фамилию мастера",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_surname)

    def get_surname(self, message: Message):
        if message.text == 'Пропустить':
            self._step(message, self.get_image)
            return
        self.master_data['surname'] = message.text

        # next msg
        self._send(
            text="Введите фотографию мастера"
        )
        self._step(message, self.get_image)

    def get_image(self, message: Message):
        while True:
            try:

                download_message = self._send(
                    'Загружаем...'
                )
                file_id = message.photo[-1].file_id
                print("Получаем файл", file_id)

                file_info = self.bot.get_file(file_id)
                print("Получаем файл", file_info.__dict__)

                downloaded_file = self.bot.download_file(file_info.file_path)
                print("Началась загрузка фотографии загрузилась 1")
                with open(file_info.file_path, 'wb') as file:
                    file.write(downloaded_file)
                print("Началась загрузка фотографии загрузилась 2")
                s3.upload_file(
                    Filename=file_info.file_path,
                    Bucket=bucket_name,
                    Key=file_info.file_path
                )
                print("Фотография загрузилась")

                self.master_data[
                    'image_url'] = f"https://s3.timeweb.cloud/dea7d49e-ba387d71-db58-4c7f-8b19-e217f5775615/{file_info.file_path}"
                break

            except Exception as _:
                self._send(
                    text="Введите корректное изображение",
                )
                self._step(message, self.get_image)
                return
        # msg
        self.bot.edit_message_text(
            chat_id=download_message.chat.id,
            message_id=download_message.id,
            text="Отлично!\n",

        )
        self._send(
            text="Мастер создан!",
            reply_markup=organization_menu_markup
        )
        self.master_data['organization_id'] = get_organization_data(self.message.chat.id).get('id')
        response = fix_master_client.create_master(self.master_data)
        print(response.json())
        self._send(
            text=response.text
        )


class MasterEditSrv:
    def __init__(self, bot: TeleBot, message: Message, master_id: int):
        self.bot = bot
        self.message = message
        self.master_data = dict()
        self.master_id = master_id
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
        self.skip_button_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        self.skip_button_markup.add(
            KeyboardButton(text='Не изменять')
        )
        self._send(
            text="Введите имя мастера\nИли нажмите 'Не изменять'",
            reply_markup=self.skip_button_markup
        )

        self._step(message, self.get_name)

    def get_name(self, message: Message):

        if message.text == 'Не изменять':
            self._send(
                text="Введите фамилию мастера",
                reply_markup=self.skip_button_markup
            )
            self._step(message, self.get_surname)
            return
        else:
            self.master_data['name'] = message.text
            self._send(
                text="Введите фамилию мастера",
                reply_markup=self.skip_button_markup
            )

            self._step(message, self.get_surname)

    def get_surname(self, message: Message):
        if message.text == 'Не изменять':
            self._send(
                text="Введите фотографию мастера"
            )
            self._step(message, self.get_image)
            return
        self.master_data['surname'] = message.text

        # next msg
        self._send(
            text="Введите фотографию мастера"
        )
        self._step(message, self.get_image)

    def get_image(self, message: Message):
        download_message = message
        while True:
            try:

                if message.text == 'Не изменять':
                    break

                download_message = self._send(
                    'Загружаем...'
                )
                file_id = message.photo[-1].file_id
                print("Получаем файл", file_id)

                file_info = self.bot.get_file(file_id)
                print("Получаем файл", file_info.__dict__)

                downloaded_file = self.bot.download_file(file_info.file_path)
                print("Началась загрузка фотографии загрузилась 1")
                with open(file_info.file_path, 'wb') as file:
                    file.write(downloaded_file)
                print("Началась загрузка фотографии загрузилась 2")
                s3.upload_file(
                    Filename=file_info.file_path,
                    Bucket=bucket_name,
                    Key=file_info.file_path
                )
                print("Фотография загрузилась")
                self.master_data['image_url'] = f"https://s3.timeweb.cloud/dea7d49e-ba387d71-db58-4c7f-8b19-e217f5775615/{file_info.file_path}"
                break

            except Exception as _:
                self._send(
                    text="Введите корректное изображение",
                )
                print(_.args)

                self._step(message, self.get_image)
                return

        # msg
        if download_message:
            self.bot.edit_message_text(
                chat_id=download_message.chat.id,
                message_id=download_message.id,
                text="Отлично!\n",
            )
        self._send(
            text="Мастер Изменен!",
            reply_markup=organization_menu_markup
        )
        self.master_data['organization_id'] = get_organization_data(self.message.chat.id).get('id')
        fix_master_client.edit_master(self.master_data, self.master_id)


class MasterServiceListSrv:

    def __init__(self,
                 bot: TeleBot,
                 message: Message,
                 master_id: int):
        self.bot = bot
        self.message = message
        self.master_id = master_id

    def _send(self, text, **kwargs):
        message = self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )
        return message

    def get_services_list(self):
        self.master_services = get_master_services(self.master_id)

    def generate_service_list_buttons(self):
        self.services_list_buttons = InlineKeyboardMarkup()
        self.services_list = self.master_services
        [
            self.services_list_buttons.add(
                InlineKeyboardButton(
                    f"{i.get('title')}",
                    callback_data='masterservice_detail_{}'.format(i.get('id'))
                )
            )
            for i in self.services_list
        ]
        self.services_list_buttons.add(
            InlineKeyboardButton(
                text='Добавить услугу',
                callback_data='masterservice_create_{}'.format(self.master_id)
            )
        )
        self.services_list_buttons.add(
            InlineKeyboardButton(
                'Назад',
                callback_data='masterdetail_{}'.format(self.master_id)
            )
        )

    def execute(self):
        self.get_services_list()
        self.generate_service_list_buttons()
        self.bot.edit_message_text(
            text=f"Список услуг мастера:\nУ мастера {len(self.services_list)} услуг",
            reply_markup=self.services_list_buttons,
            message_id=self.message.id,
            chat_id=self.message.chat.id
        )
        return None


class MasterServiceDetailSrv:

    def __init__(self,
                 bot: TeleBot,
                 message: Message,
                 service_id: int):
        self.bot = bot
        self.message = message
        self.service_id = service_id

    def _send(self, text, **kwargs):
        message = self.bot.send_message(
            chat_id=self.message.chat.id,
            text=text,
            **kwargs
        )
        return message

    def get_service_detail(self):
        self.service_detail = get_service_detail(self.service_id)

    def generate_master_detail_buttons(self):
        self.master_detail_buttons = InlineKeyboardMarkup()
        edit_button = InlineKeyboardButton('Изменить', callback_data=f"masteredit_{self.master_data.get('id')}")
        delete_button = InlineKeyboardButton('Удалить', callback_data=f"masterdelete_{self.master_data.get('id')}")
        back_button = InlineKeyboardButton('Назад', callback_data=f"masterservices_list_{self.message.chat.id}")
        self.master_detail_buttons.add(edit_button)
        self.master_detail_buttons.add(delete_button)
        self.master_detail_buttons.add(back_button)

    def execute(self):
        self.get_service_detail()
        self.generate_service_list_buttons()
        self._send(
            text=f"Список услуг:\nУ вас {len(self.services_list)} услуг",
            reply_markup=self.services_list_buttons
        )
        return None


class MasterServiceCreateSrv:
    def __init__(self,
                 bot: TeleBot,
                 message: Message,
                 master_id: int):
        self.bot = bot
        self.message = message
        self.service_data = dict()
        self.master_id = master_id
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
            text="Введите название услуги \n",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_title)

    def get_title(self, message: Message):
        self.service_data['title'] = message.text
        self._send(
            text="Введите короткое описание услуги",
            reply_markup=ReplyKeyboardRemove()
        )

        self._step(message, self.get_description)

    def get_description(self, message: Message):
        self.service_data['short_description'] = message.text

        # next msg
        self._send(
            text="Выберите длительность услуги",
            reply_markup=generate_service_min_time_button()
        )
        self._step(message, self.get_min_time)

    def get_min_time(self, message: Message):
        # msg
        try:
            if 'мин' in message.text:
                time = message.text.replace('мин', '')
                int(time)
                self.service_data['min_time'] = time

        except ValueError:
            self._send(
                text="Выберите число из списка"
            )
            self._step(message, self.get_min_time)
            return
        self._send(
            text="Введите стоимость услуги в рублях",
            reply_markup=ReplyKeyboardRemove()
        )
        self._step(message, self.get_price)

    def get_price(self, message: Message):
        self.service_data['price'] = message.text
        try:
            int(message.text)
        except ValueError:
            self._send(
                text="Введите корректную стоимость "
            )
            self._step(message, self.get_price)
            return

        self._send(
            text="Услуга создана",
            reply_markup=organization_menu_markup
        )
        self.service_data['master_id'] = self.master_id
        fix_master_client.create_service(self.service_data, self.master_id)



class MasterServiceEditSrv:
    ...





class MasterServiceDeleteSrv:
    ...
