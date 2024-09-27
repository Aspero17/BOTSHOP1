from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.goods import Goods  # Импортируйте ваши состояния
from utils.db import get_categories, get_manufacturers_by_category, get_products_by_category

router = Router()

# Используем лямбда-функцию для команды /adminpanelspb
@router.message(lambda message: message.text == "/adminpanelspb")
async def admin_panel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == 730393028:  # Замените на ваш настоящий ID администратора
        await state.clear()  # Сброс состояния перед входом в админ панель
        await message.answer("Добро пожаловать в админ панель!")
    else:
        await message.answer("У вас нет доступа к админ панели.")

@router.message(Goods.product_selection)  # Используйте состояние
async def show_categories(message: types.Message):
    categories = get_categories()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    for category in categories:
        keyboard.add(KeyboardButton(category))

    keyboard.add(KeyboardButton("🔙 Назад"))
    await message.answer("Выберите категорию товаров:", reply_markup=keyboard)

@router.message(Goods.category)  # Используйте состояние
async def handle_category_selection(message: types.Message, state: FSMContext):
    category = message.text
    manufacturers = get_manufacturers_by_category(category)

    if manufacturers:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for manufacturer in manufacturers:
            keyboard.add(KeyboardButton(manufacturer))
        keyboard.add(KeyboardButton("🔙 Назад"))
        await message.answer(f"Выберите производителя для категории '{category}':", reply_markup=keyboard)
        await state.update_data(selected_category=category)
    else:
        products = get_products_by_category(category)
        if products:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for product in products:
                keyboard.add(KeyboardButton(product['name']))
            keyboard.add(KeyboardButton("🔙 Назад"))
            await message.answer("Выберите продукт для изменения:", reply_markup=keyboard)
        else:
            await message.answer("Продукты не найдены.")
