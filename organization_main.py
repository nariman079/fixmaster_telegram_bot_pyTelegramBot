"""
Main file
"""
import os
import uuid

from telebot import TeleBot, types

from config import settings, cache
from config.settings import bucket_name, s3
from organization_bot.src.services import OrganizationCreate, MasterListSrv, MasterDetailSrv, \
    MasterDeleteSrv, MasterCreateSrv, MasterEditSrv, MasterServiceListSrv, MasterServiceListSrv, \
    MasterServiceDetailSrv, MasterServiceEditSrv, MasterServiceCreateSrv, MasterServiceDeleteSrv

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


@bot.message_handler(content_types=['text'])
def get_organization_data_content(message: types.Message):
    if message.text == '📃 Список мастеров':
        MasterListSrv(bot=bot, message=message).execute()
    elif message.text == '👥 Список клиентов':
        pass
    elif message.text == "➕ Добавить мастера":
        MasterCreateSrv(bot=bot,
                        message=message)
    else:
        pass
        # ClientListSrv(bot=bot, message=message).execute()
    # elif message.text == :
    #     ServicesListSrv(bot=bot, message=message).execute()


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery):
    data = call.data
    print(data)
    if 'masterlist' in data:
        MasterListSrv(
            bot=bot,
            message=call.message,
            call=True
        ).execute()
    elif 'masterdetail' in data:
        master_id = data.split('_')[-1]
        MasterDetailSrv(bot=bot,
                        master_id=int(master_id),
                        call=call,
                        ).execute()
    elif 'masterdelete' in data:
        master_id = data.split('_')[-1]
        MasterDeleteSrv(bot=bot,
                        master_id=int(master_id),
                        call=call,
                        ).execute()
    elif 'mastercrete' in data:
        MasterCreateSrv(bot=bot,
                        message=call.message)
    elif 'masteredit' in data:
        master_id = data.split('_')[-1]

        MasterEditSrv(
            bot=bot,
            message=call.message,
            master_id=int(master_id)
        )
    elif 'masterservices_list' in data:
        master_id = data.split('_')[-1]
        MasterServiceListSrv(
            bot=bot,
            message=call.message,
            master_id=int(master_id)
        ).execute()
    elif 'masterservice_detail' in data:
        service_id = data.split('_')[-1]
        print(service_id)
        MasterServiceDetailSrv(
            bot=bot,
            message=call.message,
            service_id=int(service_id)
        ).execute()
    elif 'masterservice_delete' in data:
        service_id = data.split('_')[-1]
        MasterServiceDeleteSrv(
            bot=bot,
            message=call.message,
            service_id=int(service_id)
        ).execute()

    elif 'masterservice_create' in data:
        master_id = data.split('_')[-1]
        MasterServiceCreateSrv(
            bot=bot,
            message=call.message,
            master_id=int(master_id)
        )
        ...
    elif 'mastereservice_edit' in data:
        service_id = data.split('_')[-1]
        MasterServiceEditSrv(
            bot=bot,
            message=call.message,
            service_id=int(service_id)
        )


@bot.message_handler(content_types=['photo'])
def photo(message: types.Message) -> None:
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    path = f'photos/{message.from_user.username}/'
    if not os.path.isdir(path):
        os.mkdir(path)

    file_path = os.path.join(path, f"{str(uuid.uuid4())}.jpg")
    with open(file_path, 'wb') as file:
        file.write(downloaded_file)

    s3.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=file_path
    )

    url = f"https://s3.timeweb.cloud/dea7d49e-ba387d71-db58-4c7f-8b19-e217f5775615/{file_path}"
    print(url)


if __name__ == '__main__':
    bot.polling(none_stop=True)
