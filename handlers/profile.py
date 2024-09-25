import logging
import json  # Используем json для безопасного преобразования списков в строки
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.profile import get_profile_menu
from keyboards.main import get_main_menu
from data.usersdb import update_user, get_user_info, get_order_history_from_db

router = Router()

# Состояния для изменения данных профиля
class Profile(StatesGroup):
    change_phone = State()
    add_additional_phone = State()
    change_address = State()
    change_name = State()

# Изменение номера телефона
@router.message(F.text == "📞 Изменить номер")
async def change_phone(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал 'Изменить номер'")
    await message.answer("Введите новый номер телефона:")
    await state.set_state(Profile.change_phone)

# Добавление дополнительного номера телефона
@router.message(F.text == "➕ Добавить доп номер")
async def add_additional_phone(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал 'Добавить доп номер'")
    await message.answer("Введите дополнительный номер телефона:")
    await state.set_state(Profile.add_additional_phone)

# Изменение адреса
@router.message(F.text == "📍 Изменить адрес")
async def change_address_start(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал 'Изменить адрес'")
    await message.answer("Введите новый адрес доставки:")
    await state.set_state(Profile.change_address)

# История покупок
@router.message(F.text == "🛍 История покупок")
async def purchase_history(message: types.Message):
    logging.info("Пользователь выбрал 'История покупок'")
    user_id = message.from_user.id

    # Получаем историю заказов из базы данных
    order_history = get_order_history_from_db(user_id)

    if order_history:
        # Переворачиваем список, чтобы новые записи были сверху
        order_history = order_history[::-1]
        history_info = "\n".join(
            f"Время: {entry['time']}\n\n{entry['details']}\n\n" for entry in order_history
        )
    else:
        history_info = "Ваша история покупок пуста."

    await message.answer(history_info, reply_markup=get_profile_menu())

# Возврат в главное меню
@router.message(F.text == "⬅ Назад")
async def go_back(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал 'Назад'")
    await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
    await state.clear()

# Просмотр профиля
@router.message(F.text == "👤 Мой профиль")
async def view_profile(message: types.Message):
    logging.info("Пользователь выбрал 'Мой профиль'")
    user_info = get_user_info(message.from_user.id)

    if user_info:
        profile_info = (
            f"Имя: {user_info.get('name', 'Не указано')}\n"
            f"Телефон: {user_info.get('phone', 'Не указан')}\n"
            f"Адрес: {user_info.get('address', 'Не указан')}\n"
            f"Дополнительные номера: {', '.join(user_info.get('additional_phones', [])) or 'Нет дополнительных номеров'}"
        )
        await message.answer(profile_info, reply_markup=get_profile_menu())
    else:
        await message.answer("Профиль не найден. Попробуйте снова.")

# Обновление номера телефона
@router.message(Profile.change_phone)
async def update_phone(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный номер телефона:")
        return
    logging.info(f"Пользователь изменил номер телефона: {message.text}")

    # Обновление номера телефона в базе данных
    update_user(message.from_user.id, phone=message.text)

    await message.answer("Номер телефона изменен.", reply_markup=get_profile_menu())
    await state.clear()

# Добавление дополнительного номера телефона
@router.message(Profile.add_additional_phone)
async def add_additional_phone(message: types.Message, state: FSMContext):
    user_info = get_user_info(message.from_user.id)

    if user_info:
        additional_phones = user_info.get('additional_phones', [])
        additional_phones.append(message.text)

        logging.info(f"Пользователь добавил дополнительный номер телефона: {message.text}")

        # Обновление дополнительного номера телефона в базе данных
        update_user(message.from_user.id, additional_phones=additional_phones)

        await message.answer("Дополнительный номер добавлен.", reply_markup=get_profile_menu())
    else:
        await message.answer("Пользователь не найден. Попробуйте снова.")

    await state.clear()

# Обновление адреса
@router.message(Profile.change_address)
async def update_address(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь изменил адрес доставки: {message.text}")

    # Обновление адреса в базе данных
    update_user(message.from_user.id, address=message.text)

    await message.answer("Адрес изменен.", reply_markup=get_profile_menu())
    await state.clear()

# Изменение имени
@router.message(F.text == "✏️ Изменить имя")
async def change_name(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал 'Изменить имя'")
    await message.answer("Введите новое имя:")
    await state.set_state(Profile.change_name)

# Обновление имени
@router.message(Profile.change_name)
async def update_name(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь изменил имя: {message.text}")

    # Обновление имени в базе данных
    update_user(message.from_user.id, name=message.text)

    await message.answer("Имя изменено.", reply_markup=get_profile_menu())
    await state.clear()
