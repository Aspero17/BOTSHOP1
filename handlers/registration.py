from keyboards.main import get_main_menu
from data.usersdb import is_user_registered, add_user, update_user
import logging
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command

router = Router()

class Registration(StatesGroup):
    name = State()
    phone = State()
    address = State()

@router.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if is_user_registered(user_id):
        # Пользователь уже зарегистрирован
        await message.answer("Вы уже зарегистрированы!", reply_markup=get_main_menu())
        logging.info(f"Пользователь {user_id} уже зарегистрирован.")
    else:
        # Пользователь не зарегистрирован, начинаем процесс регистрации
        logging.info("Обработка команды /start")
        await message.answer("Привет! Добро пожаловать в наш магазин. Введите ваше имя!")
        await state.set_state(Registration.name)

@router.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    logging.info("Получено имя пользователя: %s", message.text)
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь введите ваш номер телефона:")
    await state.set_state(Registration.phone)

@router.message(Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный номер телефона:")
        return
    logging.info("Получен номер телефона пользователя: %s", message.text)
    await state.update_data(phone=message.text)
    await message.answer("Спасибо! Теперь введите адрес доставки:")
    await state.set_state(Registration.address)

@router.message(Registration.address)
async def process_address(message: types.Message, state: FSMContext):
    logging.info("Получен адрес пользователя: %s", message.text)
    user_data = await state.get_data()
    name = user_data['name']
    phone = user_data['phone']
    address = message.text

    # Сохранение данных пользователя в базе данных
    add_user(message.from_user.id, name, phone, address)

    try:
        keyboard = get_main_menu()
        logging.info("Клавиатура успешно создана")
        await message.answer("Регистрация завершена!", reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатуры: {e}")

    await state.clear()