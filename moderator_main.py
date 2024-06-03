"""
Main file
"""
from telebot import TeleBot, types

from config import settings
from moderator_bot.src.services import ModeratorCreate, VerifiedOrganization


bot = TeleBot(settings.MODERATOR_BOT_TOKEN)  # type: ignore


@bot.message_handler(commands=['start'])
def main(message: types.Message):
    """
    Сообщение при запуске бота
    """
    bot.send_message(chat_id=message.chat.id,
                     text="Добро пожаловать а FixMaster для модераторов")
    ModeratorCreate(bot, message)

@bot.message_handler(commands=['test-call'])
def send_callback(message: types.Message):
    bot.send_message(
        chat_id=message.chat.id,
        text="text",
        reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Test', callback_data=f'organization_verify_{message.id}_false_43'))
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: types.CallbackQuery):
    data: str = call.data
    

    if 'organization_verify_true' in data:
        organization_id = int(data.split('_')[-1])
        VerifiedOrganization(organization_id).verify_organization(True)
        verify_text = '\nВерифицирован ✅'
    elif 'organization_verify_false' in data:
        organization_id = int(data.split('_')[-1])
        VerifiedOrganization(organization_id).verify_organization(False)
        verify_text = '\nНе верифицирован ❌'
    else:
        verify_text = 'Не верифицирован ❌'

    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.id,
        text=call.message.text + verify_text,
        )


if __name__ == '__main__':
    bot.polling(none_stop=True)