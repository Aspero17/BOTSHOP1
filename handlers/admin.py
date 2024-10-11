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
    adding_product = State()
    deleting_product = State()
    adding_manufacturer = State()

logger.info("Файл admin.py загружен.")

ADMINS = [730393028, 987654321]

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Декоратор для проверки прав администратора
def admin_only(handler):
    @wraps(handler)
    async def wrapper(message: types.Message, *args, **kwargs):
        if not is_admin(message.from_user.id):
            logging.warning(f"Пользователь {message.from_user.id} пытался получить доступ к админ функции.")
            return await message.answer("У вас нет доступа к этой функции.")
        return await handler(message, *args, **kwargs)
    return wrapper

# Оптимизация работы с БД
class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect("data/products.db")
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        self.conn.close()

def get_all_products():
    with DatabaseConnection() as db:
        db.cursor.execute("SELECT id, name, price FROM products")
        return db.cursor.fetchall()

def get_all_manufacturers():
    with DatabaseConnection() as db:
        db.cursor.execute("SELECT id, name FROM manufacturers")
        return db.cursor.fetchall()

def update_product(product_id, new_name, new_price):
    with DatabaseConnection() as db:
        db.cursor.execute("UPDATE products SET name = ?, price = ? WHERE id = ?", (new_name, new_price, product_id))

def add_product_to_db(name, price):
    with DatabaseConnection() as db:
        db.cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))

def delete_product_by_id(product_id):
    with DatabaseConnection() as db:
        db.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return db.cursor.rowcount > 0

# Обработчики

@router.message(Command("adminpanelspb"))
async def admin_panel_command(message: types.Message, state: FSMContext):
    logging.info(f"Попытка вызвать админ панель от пользователя {message.from_user.id}.")
    await state.clear()
    await state.set_state("admin_panel")
    await message.answer("Добро пожаловать в админ панель!", reply_markup=get_admin_menu())

@router.message(lambda message: message.text == "📦 Просмотреть товары")
@admin_only
async def view_all_products(message: types.Message):
    products = get_all_products()

    if not products:
        await message.answer("Нет доступных товаров.")
        return

    response = "Список всех товаров:\n"
    for product in products:
        product_id, name, price = product
        response += f"ID: {product_id}, Название: {name}, Цена: {price} руб.\n"

    max_length = 4096
    if len(response) > max_length:
        parts = [response[i:i + max_length] for i in range(0, len(response), max_length)]
        for part in parts:
            await message.answer(part)
    else:
        await message.answer(response)

@router.message(lambda message: message.text == "👤 Просмотреть производителей")
@admin_only
async def view_all_manufacturers(message: types.Message):
    manufacturers = get_all_manufacturers()
    if manufacturers:
        response = "\n".join([f"ID: {m[0]}, Название: {m[1]}" for m in manufacturers])
        await message.answer(f"Список всех производителей:\n{response}")
        logging.info(f"Админ {message.from_user.id} просмотрел всех производителей.")
    else:
        await message.answer("Производители не найдены.")
        logging.info(f"Админ {message.from_user.id} попытался просмотреть производителей, но они не найдены.")

@router.message(lambda message: message.text == "✏️ Изменить товар")
@admin_only
async def select_product_to_edit(message: types.Message, state: FSMContext):
    logging.info(f"Нажата кнопка для редактирования товара. Текст сообщения: {message.text}")
    await message.answer("Введите ID товара, который хотите изменить:")
    await state.set_state(AdminStates.selecting_product)



@router.message(AdminStates.selecting_product)
@admin_only
async def enter_product_id(message: types.Message, state: FSMContext):
    product_id = message.text
    with DatabaseConnection() as db:
        db.cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
        product = db.cursor.fetchone()

    if product:
        await state.update_data(product_id=product_id, product_name=product[0], product_price=product[1])
        await message.answer(f"Вы выбрали товар:\nНазвание: {product[0]}\nЦена: {product[1]} руб.")
        await message.answer("Введите новое название товара:")
        await state.set_state(AdminStates.editing_product_name)
        logging.info(f"Админ {message.from_user.id} выбрал товар с ID {product_id} для редактирования.")
    else:
        await message.answer("Товар с таким ID не найден. Попробуйте снова.")
        logging.warning(f"Товар с ID {product_id} не найден админом {message.from_user.id}.")

