from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    # Первая строка: одна кнопка
    kb_builder.row(
        KeyboardButton(text="🛒 Товары")
    )

    # Вторая строка: одна кнопка
    kb_builder.row(
        KeyboardButton(text="🛍 Корзина")
    )

    # Третья строка: две кнопки
    kb_builder.row(
        KeyboardButton(text="👤 Мой профиль"),
        KeyboardButton(text="✉ Обратная связь")
    )

    return kb_builder.as_markup(resize_keyboard=True)