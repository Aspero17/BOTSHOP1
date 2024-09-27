from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from keyboards.cart import get_cart_keyboard
from keyboards.main import get_main_menu
from data.usersdb import initialize_users_db, get_user_info, save_order_to_db, get_order_history_from_db
from utils.storage import user_data
from datetime import datetime

router = Router()

class OrderStates(StatesGroup):
    confirming_order = State()

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

@router.message(F.text == "🛍 Просмотреть корзину")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_users_db()  # Инициализация базы данных пользователей
    cart_info = format_cart(user_id)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Управление корзиной")],
            [KeyboardButton(text="🗑 Очистить корзину")],
            [KeyboardButton(text="💳 Оформить заказ")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer(cart_info, reply_markup=keyboard)

@router.message(F.text == "🗑 Очистить корзину")
async def clear_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_users_db()
    user_data[user_id]['cart'] = {}
    await message.answer("Ваша корзина была очищена.", reply_markup=get_main_menu())

@router.message(F.text == "💳 Оформить заказ")
async def handle_order(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    initialize_users_db()

    if not user_data.get(user_id, {}).get('cart'):
        await message.answer("Ваша корзина пуста. Добавьте товары в корзину перед оформлением заказа.")
        return

    user_info = get_user_info(user_id)

    if not user_info.get('name') or not user_info.get('phone') or not user_info.get('address'):
        await message.answer("Пожалуйста, заполните свои данные (имя, телефон, адрес) перед оформлением заказа.")
        return

    cart_info = format_cart(user_id)
    confirmation_message = (
        f"Вы собираетесь оформить заказ. Проверьте информацию:\n\n{cart_info}\n\n"
        "Подтвердите оформление заказа. Если нужно внести изменения, вернитесь в корзину."
    )

    await message.answer(confirmation_message, reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить заказ")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    ))
    await state.set_state(OrderStates.confirming_order)

@router.message(OrderStates.confirming_order)
async def handle_order_confirmation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text == "✅ Подтвердить заказ":
        user_info = get_user_info(user_id)
        cart_info = format_cart(user_id)
        order_message = (
            f"Новый заказ от {user_info.get('name')}\n"
            f"Телефон: {user_info.get('phone')}\n"
            f"Адрес: {user_info.get('address')}\n\n"
            f"Содержимое корзины:\n{cart_info}"
        )

        special_chat_id = -1002162957894  # Замените на ID специального чата
        try:
            await message.bot.send_message(special_chat_id, order_message)
            await message.answer(
                "Ваш заказ оформлен и отправлен на обработку. Спасибо за покупку!",
                reply_markup=get_main_menu()
            )

            save_order_to_db(user_id, order_message)

        except Exception as e:
            await message.answer(f"Не удалось отправить заказ: {e}")

        user_data[user_id]['cart'] = {}  # Очищаем корзину
        await state.clear()
    elif message.text == "🔙 Назад":
        await message.answer("Вы вернулись в корзину.", reply_markup=get_cart_keyboard())
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите корректный вариант.")


@router.message(F.text == "📜 История заказов")
async def show_order_history(message: types.Message):
    user_id = message.from_user.id
    initialize_users_db()
    history_info = format_order_history(user_id)

    # Ограничение на количество символов в одном сообщении Telegram
    max_message_length = 4096

    # Разбиваем сообщение на части и отправляем каждую часть отдельно
    if len(history_info) > max_message_length:
        for i in range(0, len(history_info), max_message_length):
            await message.answer(history_info[i:i + max_message_length], reply_markup=get_main_menu())
    else:
        await message.answer(history_info, reply_markup=get_main_menu())


def format_order_history(user_id: int) -> str:
    history = get_order_history_from_db(user_id)
    if not history:
        return "📦 Ваша история заказов пуста."

    # Создаем список для хранения отформатированных записей
    history_entries = []

    for entry in history:
        # Добавляем отступ и улучшаем форматирование
        details_formatted = entry['details'].replace('\n', '\n   ')
        formatted_entry = (
            f"🗓️ **Дата и время:** {entry['time']}\n"
            f"📜 **Детали заказа:**\n"
            f"   {details_formatted}\n"  # Отступ для деталей заказа
            f"{'⭐' * 13}\n"  # Разделитель между записями
        )
        # Добавляем запись в начало списка, чтобы новые заказы были внизу
        history_entries.insert(0, formatted_entry)

    # Объединяем записи в одну строку и добавляем заголовок
    formatted_history = "\n".join(history_entries)

    # Возвращаем итоговую строку с заголовком
    return (
        "📋 **История ваших заказов:**\n"
        f"{'═' * 13}\n"  # Линия заголовка
        f"{formatted_history}"
    )

@router.message(F.text)
async def handle_all_buttons(message: types.Message, state: FSMContext):
    if message.text == "🛍 Просмотреть корзину":
        await show_cart(message)
    elif message.text == "🗑 Очистить корзину":
        await clear_cart(message)
    elif message.text == "📜 История заказов":
        await show_order_history(message)
    elif message.text == "🔙 Назад":
        await message.answer("Возвращаемся в главное меню.", reply_markup=get_main_menu())
    elif message.text == "💳 Оформить заказ":
        await handle_order(message, state)
    else:
        await message.answer("Неизвестная команда.")
