import sqlite3
import logging
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from keyboards.admin import get_admin_menu
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from functools import wraps

router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Добавление обработчика для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Состояния для FSM
class AdminStates(StatesGroup):
    selecting_product = State()
    editing_product_name = State()
    editing_product_price = State()
    selecting_manufacturer = State()
    editing_manufacturer_name = State()

DB_PATH = "data/products.db"

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Получение всех товаров
def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

# Обновление товара (название и цена)
def update_product(product_id: int, new_name: str, new_price: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (new_name, new_price, product_id))
    conn.commit()
    conn.close()

# Получение всех производителей
def get_all_manufacturers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM manufacturers")
    manufacturers = cursor.fetchall()
    conn.close()
    return manufacturers

# Обновление производителя
def update_manufacturer(manufacturer_id: int, new_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE manufacturers SET name = ? WHERE id = ?", (new_name, manufacturer_id))
    conn.commit()
    conn.close()

# Проверка, находится ли пользователь в админ панели
async def check_admin_state(state: FSMContext):
    current_state = await state.get_state()
    if current_state is None or current_state not in AdminStates.all():
        logger.warning("Пользователь не в админ панели.")
        return False
    return True


# Список администраторов по user_id
ADMINS = [730393028, 987654321]  # Здесь добавь свой user_id и других админов

# Функция для проверки, является ли пользователь администратором
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Декоратор для проверки прав администратора
def admin_only(handler):
    @wraps(handler)
    async def wrapper(message: types.Message, state: FSMContext, *args, **kwargs):
        if not is_admin(message.from_user.id):
            logging.warning(f"Пользователь {message.from_user.id} пытался получить доступ к админ функции.")
            return await message.answer("У вас нет доступа к этой функции.")
        return await handler(message, state, *args, **kwargs)
    return wrapper

# Обработчик команды /adminpanelspb
@router.message(Command(commands=["adminpanelspb"]))
@admin_only
async def admin_panel_command(message: types.Message, state: FSMContext):
    logging.info(f"Администратор {message.from_user.id} вошел в админ панель.")
    await state.set_state("admin_panel")  # Устанавливаем состояние админ панели
    await message.answer("Добро пожаловать в админ панель!", reply_markup=get_admin_menu())

# Проверка на нахождение в админ панели
async def check_admin_state(state: FSMContext) -> bool:
    current_state = await state.get_state()
    return current_state == "admin_panel"

# Обработчик для просмотра всех товаров
@router.message(lambda message: message.text == "📦 Просмотреть товары")
@admin_only
async def view_all_products(message: types.Message, state: FSMContext):
    if not await check_admin_state(state):
        return await message.answer("Пожалуйста, сначала войдите в админ панель.")

    products = get_all_products()
    if products:
        response = "Список всех товаров:\n"
        chunk_size = 4096 // 100  # приблизительно по 100 символов на товар
        for i in range(0, len(products), chunk_size):
            chunk = products[i:i + chunk_size]
            response = ""
            for product in chunk:
                response += f"ID: {product[0]}, Название: {product[1]}, Цена: {product[2]} руб.\n"
            await message.answer(response)
        logger.info(f"Админ {message.from_user.id} просмотрел все товары.")
    else:
        await message.answer("Товары не найдены.")
        logger.info(f"Админ {message.from_user.id} попытался просмотреть товары, но они не найдены.")

# Обработчик для просмотра всех производителей
@router.message(lambda message: message.text == "👤 Просмотреть производителей")
@admin_only
async def view_all_manufacturers(message: types.Message, state: FSMContext):
    manufacturers = get_all_manufacturers()
    if manufacturers:
        response = "Список всех производителей:\n"
        for manufacturer in manufacturers:
            response += f"ID: {manufacturer[0]}, Название: {manufacturer[1]}\n"
        await message.answer(response)
        logging.info(f"Админ {message.from_user.id} просмотрел всех производителей.")
    else:
        await message.answer("Производители не найдены.")
        logging.info(f"Админ {message.from_user.id} попытался просмотреть производителей, но они не найдены.")

# Обработчик для начала редактирования товара
@router.message(lambda message: message.text == "✏️ Изменить товар")
@admin_only
async def select_product_to_edit(message: types.Message, state: FSMContext):
    await message.answer("Введите ID товара, который хотите изменить:")
    await state.set_state(AdminStates.selecting_product)
    logging.info(f"Админ {message.from_user.id} начал процесс редактирования товара.")

# Обработчик выбора товара для редактирования
@router.message(AdminStates.selecting_product)
@admin_only
async def enter_product_id(message: types.Message, state: FSMContext):
    product_id = message.text
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        await state.update_data(product_id=product_id, product_name=product[0], product_price=product[1])
        await message.answer(f"Вы выбрали товар:\nНазвание: {product[0]}\nЦена: {product[1]} руб.")
        await message.answer("Введите новое название товара:")
        await state.set_state(AdminStates.editing_product_name)
        logging.info(f"Админ {message.from_user.id} выбрал товар с ID {product_id} для редактирования.")
    else:
        await message.answer("Товар с таким ID не найден. Попробуйте снова.")
        logging.warning(f"Товар с ID {product_id} не найден админом {message.from_user.id}.")

# Обработчик изменения названия товара
@router.message(AdminStates.editing_product_name)
@admin_only
async def enter_new_product_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await state.update_data(new_name=new_name)
    await message.answer(f"Новое название товара: {new_name}")
    await message.answer("Теперь введите новую цену товара:")
    await state.set_state(AdminStates.editing_product_price)
    logging.info(f"Админ {message.from_user.id} изменил название товара на {new_name}.")

# Обработчик изменения цены товара
@router.message(AdminStates.editing_product_price)
@admin_only
async def enter_new_product_price(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text)
    except ValueError:
        await message.answer("Введите корректное числовое значение для цены.")
        logging.warning(f"Админ {message.from_user.id} ввел некорректное значение цены: {message.text}.")
        return

    user_data = await state.get_data()
    product_id = user_data['product_id']
    new_name = user_data['new_name']

    update_product(product_id, new_name, new_price)
    await message.answer(f"Товар успешно обновлен:\nНовое название: {new_name}\nНовая цена: {new_price} руб.")
    logging.info(
        f"Админ {message.from_user.id} обновил товар с ID {product_id}. Новое название: {new_name}, новая цена: {new_price} руб.")

    await state.clear()
    await message.answer("Вы вернулись в админ панель.", reply_markup=get_admin_menu())