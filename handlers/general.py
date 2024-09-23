import logging
from aiogram import types, Router, F
from keyboards.main import get_main_menu
from keyboards.profile import get_profile_menu
from keyboards.cart import get_cart_keyboard
from data.usersdb import get_user_info

router = Router()


@router.message(lambda message: message.text == "/start")
async def start_command(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_menu())


@router.message(F.text == "🛒 Товары")
async def show_goods(message: types.Message):
    logging.info("Пользователь выбрал раздел 'Товары'")
    await message.answer("Вот список товаров:", reply_markup=get_main_menu())


@router.message(F.text == "🛍 Корзина")
async def show_cart(message: types.Message):
    logging.info("Пользователь выбрал раздел 'Корзина'")
    await message.answer("Ваша корзина:", reply_markup=get_cart_keyboard())


@router.message(F.text == "👤 Мой профиль")
async def show_profile(message: types.Message):
    logging.info("Пользователь выбрал раздел 'Мой профиль'")
    user_id = message.from_user.id

    # Получаем данные пользователя из базы данных
    user_info = get_user_info(user_id)

    if user_info:
        name, phone, address, additional_phones_str = user_info
        additional_phones = "\n".join(eval(additional_phones_str))  # Преобразуем строку в список

        profile_info = (f"Имя: {name}\n"
                        f"Телефон: {phone}\n"
                        f"Адрес: {address}\n"
                        f"Дополнительные номера:\n{additional_phones}")
        await message.answer(f"Ваш профиль:\n{profile_info}", reply_markup=get_profile_menu())
    else:
        await message.answer("Информация о профиле не найдена.", reply_markup=get_profile_menu())
