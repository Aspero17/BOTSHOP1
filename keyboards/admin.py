from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_menu() -> ReplyKeyboardMarkup:
    # Создайте кнопки
    button_view_products = KeyboardButton("📦 Просмотреть товары")
    button_edit_products = KeyboardButton("✏️ Изменить товары")
    button_back = KeyboardButton("🔙 Назад")

    # Создайте клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(
        button_view_products,
        button_edit_products,
    ).add(button_back)

    return keyboard
