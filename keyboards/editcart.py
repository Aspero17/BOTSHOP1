from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    cart = user_data.get(user_id, {}).get('cart', {})
    keyboard = InlineKeyboardMarkup(row_width=2)

    for item_id, item in cart.items():
        item_name = item['name']
        keyboard.add(
            InlineKeyboardButton(f"🔽 Уменьшить {item_name}", callback_data=f"decrease_{item_id}"),
            InlineKeyboardButton(f"🔼 Увеличить {item_name}", callback_data=f"increase_{item_id}"),
            InlineKeyboardButton(f"🗑 Удалить {item_name}", callback_data=f"delete_{item_id}")
        )

    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return keyboard
