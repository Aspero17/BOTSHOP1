import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from utils.storage import user_data, add_to_cart, remove_from_cart
import hashlib

router = Router()

def generate_short_id(item_id: str) -> str:
    """Генерация короткого идентификатора на основе хэша."""
    return hashlib.md5(item_id.encode()).hexdigest()[:8]  # Используем первые 8 символов хэша

def format_cart(user_id: int) -> str:
    cart = user_data.get(user_id, {}).get('cart', {})
    if not cart:
        return "Ваша корзина пуста."

    total_cost = 0
    cart_items = []

    for item_id, item in cart.items():
        item_total = item['price'] * item['quantity']
        total_cost += item_total
        cart_items.append(
            f"🛒 *{item['name']}*\n"
            f"   Количество: {item['quantity']} шт.\n"
            f"   Цена за единицу: {item['price']} руб.\n"
            f"   Итоговая стоимость: {item_total} руб.\n"
            "----------------------------------------"
        )

    result = "\n".join(cart_items) + f"\n\n*Общая стоимость:* {total_cost} руб."
    return result

def get_cart_keyboard(user_id: int) -> InlineKeyboardMarkup:
    cart = user_data.get(user_id, {}).get('cart', {})
    keyboard = []

    for item_id, item in cart.items():
        item_name = item['name']
        short_item_id = generate_short_id(item_id)  # Генерируем короткий идентификатор

        keyboard.append([
            InlineKeyboardButton(text=f"🔽 Уменьшить {item_name}", callback_data=f"decrease_{short_item_id}"),
            InlineKeyboardButton(text=f"🔼 Увеличить {item_name}", callback_data=f"increase_{short_item_id}"),
            InlineKeyboardButton(text=f"🗑 Удалить {item_name}", callback_data=f"delete_{short_item_id}")
        ])

    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def find_item_id(short_id: str, user_id: int) -> str:
    """Поиск оригинального идентификатора товара по короткому ID."""
    for item_id in user_data.get(user_id, {}).get('cart', {}):
        if generate_short_id(item_id) == short_id:
            return item_id
    return None

@router.message(F.text == "🛒 Управление корзиной")
async def manage_cart(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cart_text = format_cart(user_id)
    await message.answer(
        f"Ваша корзина:\n\n{cart_text}",
        reply_markup=get_cart_keyboard(user_id)
    )
    await state.set_state("MANAGING_CART")

@router.callback_query(lambda c: c.data and c.data.startswith('decrease_'))
async def callback_decrease(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    short_item_id = callback_query.data.split('_')[1]

    item_id = find_item_id(short_item_id, user_id)
    if item_id:
        item = user_data[user_id]['cart'][item_id]
        add_to_cart(user_id, item_id, quantity=-1, price=item['price'], name=item['name'])
        await update_cart_message(callback_query.message, user_id)
        await callback_query.answer("Количество товара уменьшено.")
    else:
        logging.warning(f"Item '{short_item_id}' not found in cart.")
        await callback_query.answer("Товар не найден в корзине.")

@router.callback_query(lambda c: c.data and c.data.startswith('increase_'))
async def callback_increase(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    short_item_id = callback_query.data.split('_')[1]

    item_id = find_item_id(short_item_id, user_id)
    if item_id:
        item = user_data[user_id]['cart'][item_id]
        add_to_cart(user_id, item_id, quantity=1, price=item['price'], name=item['name'])
        await update_cart_message(callback_query.message, user_id)
        await callback_query.answer("Количество товара увеличено.")
    else:
        logging.warning(f"Item '{short_item_id}' not found in cart.")
        await callback_query.answer("Товар не найден в корзине.")

@router.callback_query(lambda c: c.data and c.data.startswith('delete_'))
async def callback_delete(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    short_item_id = callback_query.data.split('_')[1]

    item_id = find_item_id(short_item_id, user_id)
    if item_id:
        remove_from_cart(user_id, item_id)
        await update_cart_message(callback_query.message, user_id)
        await callback_query.answer("Товар удален из корзины.")
    else:
        logging.warning(f"Item '{short_item_id}' not found in cart.")
        await callback_query.answer("Товар не найден в корзине.")

@router.callback_query(lambda c: c.data == 'back')
async def callback_back(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.answer("Возвращаемся в главное меню.")
    await state.clear()

async def update_cart_message(message: types.Message, user_id: int):
    if message.text:
        cart_text = format_cart(user_id)
        new_markup = get_cart_keyboard(user_id)

        logging.info(f"Current message text: {message.text}")
        logging.info(f"New cart text: {cart_text}")

        try:
            await message.edit_text(
                f"Ваша корзина:\n\n{cart_text}",
                reply_markup=new_markup
            )
        except TelegramBadRequest as e:
            logging.error(f"Failed to update cart message: {e}")
            if "message is not modified" not in str(e):
                raise
    else:
        logging.warning("Message text is empty, cannot update.")
