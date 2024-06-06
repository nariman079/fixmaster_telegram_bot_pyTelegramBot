from telebot import types


def get_menu_buttons() -> types.ReplyKeyboardMarkup:
    menu_buttons = types.ReplyKeyboardMarkup()
    next_session = types.KeyboardButton('Следующая бронь')
    all_clients = types.KeyboardButton('Список мох клиентов')

    menu_buttons.row(next_session, all_clients)
    return menu_buttons
