from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_cart_keyboard() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    kb_builder.row(
        KeyboardButton(text="🛍 Просмотреть корзину"),
        KeyboardButton(text="🗑 Очистить корзину")
    )

    kb_builder.row(
        KeyboardButton(text="📜 История заказов"),
        KeyboardButton(text="💳 Оформить заказ"),  # Новая кнопка
        KeyboardButton(text="🔙 Назад")
    )

    return kb_builder.as_markup(resize_keyboard=True)
