from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Управление категориями"),
        KeyboardButton("Управление производителями"),
        KeyboardButton("Управление товарами"),
        KeyboardButton("Изменение цен"),
        KeyboardButton("Выход из админпанели"),
    )
    return markup
