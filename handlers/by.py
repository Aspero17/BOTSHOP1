from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.cart import get_cart_keyboard
from utils.storage import user_data, initialize_user
from keyboards.main import get_main_menu
from handlers.cart import format_cart

router = Router()

class OrderStates(StatesGroup):
    confirming_order = State()

@router.message(F.text == "💳 Оформить заказ")
async def start_order_confirmation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    initialize_user(user_id)

    # Проверяем, что корзина не пуста
    if not user_data[user_id].get('cart'):
        await message.answer("Ваша корзина пуста. Добавьте товары в корзину перед оформлением заказа.")
        return

    # Проверяем, есть ли сохраненные данные
    user_info = user_data[user_id]
    if not all(user_info.get(key) for key in ['name', 'phone', 'address']):
        await message.answer("Пожалуйста, заполните свои данные (имя, телефон, адрес) перед оформлением заказа.")
        # Здесь можно вызвать функцию, которая собирает данные пользователя
        return

    # Запрашиваем подтверждение
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
        user_info = user_data[user_id]
        cart_info = format_cart(user_id)
        order_message = (
            f"Новый заказ от {user_info['name']}\n"
            f"Телефон: {user_info['phone']}\n"
            f"Адрес: {user_info['address']}\n\n"
            f"Содержимое корзины:\n{cart_info}"
        )

        special_chat_id = -1002162957894  # Замените на ID специального чата
        try:
            await message.bot.send_message(special_chat_id, order_message)
            await message.answer("Ваш заказ оформлен и отправлен на обработку. Спасибо за покупку!",
                                 reply_markup=get_main_menu())
        except Exception as e:
            await message.answer(f"Не удалось отправить заказ: {e}")
            # Дополнительно можно логировать ошибку, если нужно

        user_data[user_id]['cart'] = {}  # Очищаем корзину
        await state.clear()
    elif message.text == "🔙 Назад":
        await message.answer("Вы вернулись в корзину.", reply_markup=get_cart_keyboard())
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите корректный вариант.")
