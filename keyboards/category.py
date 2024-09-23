from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_category_menu() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(
        KeyboardButton(text="🍞 Мука"),
        KeyboardButton(text="🥯 Дрожжи"),
        KeyboardButton(text="🧈 Масло")
    )
    kb_builder.row(
        KeyboardButton(text="🥚 Яйца"),
        KeyboardButton(text="🫙 Уксус"),
        KeyboardButton(text="🧂 Соль-Сода-Сахар")
    )
    kb_builder.row(
        KeyboardButton(text="🥫 Консервация"),
        KeyboardButton(text="🍅 Томатная паста, Майонез, Соусы"),
        KeyboardButton(text="🍚 Рис"),
        KeyboardButton(text="🌿 Приправы")
    )
    kb_builder.row(
        KeyboardButton(text="🔙 Назад")
    )
    return kb_builder.as_markup(resize_keyboard=True)
