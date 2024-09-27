from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_admin_menu() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    # Создайте кнопки
    kb_builder.row(
        KeyboardButton(text="📦 Просмотреть товары"),
        KeyboardButton(text="✏️ Изменить товары"),
    )

    kb_builder.add(KeyboardButton(text="🔙 Назад"))

    return kb_builder.as_markup(resize_keyboard=True)
