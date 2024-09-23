from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_profile_menu() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    # Первая строка: две кнопки
    kb_builder.row(
        KeyboardButton(text="📞 Изменить номер"),
        KeyboardButton(text="✏️ Изменить имя")  # Кнопка для изменения имени
    )

    # Вторая строка: две кнопки
    kb_builder.row(
        KeyboardButton(text="➕ Добавить доп номер"),
        KeyboardButton(text="📍 Изменить адрес")  # Кнопка для изменения адреса
    )

    # Третья строка: одна кнопка
    kb_builder.row(
        KeyboardButton(text="🛍 История покупок"),
        KeyboardButton(text="⬅ Назад")
    )

    return kb_builder.as_markup(resize_keyboard=True)
