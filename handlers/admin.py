import sqlite3
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from keyboards.admin import get_admin_menu
from aiogram.fsm.state import StatesGroup, State

router = Router()

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

# Обработчик для просмотра всех товаров
@router.message(lambda message: message.text == "📦 Просмотреть товары")
async def view_all_products(message: types.Message):
    products = get_all_products()
    if products:
        response = "Список всех товаров:\n"
        for product in products:
            response += f"ID: {product[0]}, Название: {product[1]}, Цена: {product[2]} руб.\n"
        await message.answer(response)
    else:
        await message.answer("Товары не найдены.")

# Обработчик для просмотра всех производителей
@router.message(lambda message: message.text == "👤 Просмотреть производителей")
async def view_all_manufacturers(message: types.Message):
    manufacturers = get_all_manufacturers()
    if manufacturers:
        response = "Список всех производителей:\n"
        for manufacturer in manufacturers:
            response += f"ID: {manufacturer[0]}, Название: {manufacturer[1]}\n"
        await message.answer(response)
    else:
        await message.answer("Производители не найдены.")

# Обработчик для начала редактирования товара
@router.message(lambda message: message.text == "✏️ Изменить товар")
async def select_product_to_edit(message: types.Message, state: FSMContext):
    await message.answer("Введите ID товара, который хотите изменить:")
    await state.set_state(AdminStates.selecting_product)

# Обработчик выбора товара для редактирования
@router.message(AdminStates.selecting_product)
async def enter_product_id(message: types.Message, state: FSMContext):
    product_id = message.text

    # Проверим, существует ли товар с таким ID
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
    else:
        await message.answer("Товар с таким ID не найден. Попробуйте снова.")

# Обработчик изменения названия товара
@router.message(AdminStates.editing_product_name)
async def enter_new_product_name(message: types.Message, state: FSMContext):
    new_name = message.text
    await state.update_data(new_name=new_name)
    await message.answer(f"Новое название товара: {new_name}")
    await message.answer("Теперь введите новую цену товара:")
    await state.set_state(AdminStates.editing_product_price)

# Обработчик изменения цены товара
@router.message(AdminStates.editing_product_price)
async def enter_new_product_price(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text)
    except ValueError:
        await message.answer("Введите корректное числовое значение для цены.")
        return

    # Получаем данные из FSM
    user_data = await state.get_data()
    product_id = user_data['product_id']
    new_name = user_data['new_name']

    # Обновляем товар в базе данных
    update_product(product_id, new_name, new_price)
    await message.answer(f"Товар успешно обновлен:\nНовое название: {new_name}\nНовая цена: {new_price} руб.")

    await state.clear()
    await message.answer("Вы вернулись в админ панель.", reply_markup=get_admin_menu())

# Обработчик для начала редактирования производителя
@router.message(lambda message: message.text == "✏️ Изменить производителя")
async def select_manufacturer_to_edit(message: types.Message, state: FSMContext):
    await message.answer("Введите ID производителя, который хотите изменить:")
    await state.set_state(AdminStates.selecting_manufacturer)

# Обработчик выбора производителя для редактирования
@router.message(AdminStates.selecting_manufacturer)
async def enter_manufacturer_id(message: types.Message, state: FSMContext):
    manufacturer_id = message.text

    # Проверим, существует ли производитель с таким ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM manufacturers WHERE id = ?", (manufacturer_id,))
    manufacturer = cursor.fetchone()
    conn.close()

    if manufacturer:
        await state.update_data(manufacturer_id=manufacturer_id, manufacturer_name=manufacturer[0])
        await message.answer(f"Вы выбрали производителя:\nНазвание: {manufacturer[0]}")
        await message.answer("Введите новое название производителя:")
        await state.set_state(AdminStates.editing_manufacturer_name)
    else:
        await message.answer("Производитель с таким ID не найден. Попробуйте снова.")

# Обработчик изменения названия производителя
@router.message(AdminStates.editing_manufacturer_name)
async def enter_new_manufacturer_name(message: types.Message, state: FSMContext):
    new_name = message.text
    user_data = await state.get_data()
    manufacturer_id = user_data['manufacturer_id']

    # Обновляем производителя в базе данных
    update_manufacturer(manufacturer_id, new_name)
    await message.answer(f"Производитель успешно обновлен:\nНовое название: {new_name}")

    await state.clear()
    await message.answer("Вы вернулись в админ панель.", reply_markup=get_admin_menu())
