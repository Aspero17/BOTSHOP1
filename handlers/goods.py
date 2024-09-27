import re
import asyncio
from PIL import Image
import tempfile
import os
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InputFile, FSInputFile
from keyboards.main import get_main_menu
from keyboards.category import get_category_menu
from utils.database import get_manufacturers_by_category, get_products_by_category, get_products_by_manufacturer, \
    get_product_by_name
from utils.storage import user_data, initialize_user
from data.descriptions import get_category_description, get_manufacturer_description, get_manufacturer_image# Импортируем функцию для получения описаний

router = Router()


class Goods(StatesGroup):
    category = State()
    manufacturer = State()
    product_selection = State()
    quantity = State()
    cart = State()


@router.message(F.text == "🛒 Товары")
async def show_goods(message: types.Message, state: FSMContext):
    await message.answer("Выберите категорию:", reply_markup=get_category_menu())
    await state.set_state(Goods.category)


@router.message(Goods.category)
async def handle_category_selection(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.clear()  # Очистка состояния при возврате в главное меню
        await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
        return

    category = re.sub(r'[^\w\s]', '', message.text).strip()

    # Получаем и отправляем описание категории
    category_description = get_category_description(category)
    await message.answer(f"*Описание категории '{category}':*\n{category_description}", parse_mode="Markdown")

    # Получаем список производителей из базы данных
    manufacturers = get_manufacturers_by_category(category)

    if manufacturers:
        # Создаем кнопки для каждого производителя
        buttons = [KeyboardButton(text=manufacturer) for manufacturer in manufacturers]
        buttons.append(KeyboardButton(text="🔙 Назад"))
        keyboard = ReplyKeyboardMarkup(
            keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
            resize_keyboard=True
        )
        await message.answer(f"Выберите производителя для категории '{category}':", reply_markup=keyboard)
        await state.update_data(selected_category=category, selected_manufacturer=None)  # Обновление состояния
        await state.set_state(Goods.manufacturer)
    else:
        # Если производителей нет, предлагаем выбрать продукт
        products = get_products_by_category(category)
        if products:
            buttons = [KeyboardButton(text=f"{product['name']} - {product['price']} руб.") for product in products]
            buttons.append(KeyboardButton(text="🔙 Назад"))
            keyboard = ReplyKeyboardMarkup(
                keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
                resize_keyboard=True
            )
            await message.answer("Выберите продукт для добавления в корзину:", reply_markup=keyboard)
            await state.update_data(selected_category=category)  # Обновление состояния
            await state.set_state(Goods.product_selection)
        else:
            await message.answer("Продукты не найдены.", reply_markup=get_category_menu())


async def compress_image(input_path, quality=80):
    """Сжать изображение и вернуть путь к сжатому изображению."""
    loop = asyncio.get_event_loop()  # Получаем текущий цикл событий
    compressed_image_path = await loop.run_in_executor(None, _compress_image, input_path, quality)
    return compressed_image_path

def _compress_image(input_path, quality):
    """Вспомогательная функция для синхронного сжатия изображения."""
    with Image.open(input_path) as img:
        # Преобразуем изображение в режим RGB, если оно в режиме RGBA
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Создаем временный файл для сжатого изображения
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            img.save(temp_file.name, "JPEG", quality=quality)
            return temp_file.name

@router.message(Goods.manufacturer)
async def handle_manufacturer_selection(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.update_data(selected_manufacturer=None)  # Очистка выбранного производителя при возврате
        await message.answer("Выберите категорию:", reply_markup=get_category_menu())
        await state.set_state(Goods.category)
        return

    manufacturer = message.text

    # Получаем описание производителя
    description = get_manufacturer_description(manufacturer)

    # Получаем изображение производителя
    image_path = get_manufacturer_image(manufacturer)

    # Сжимаем изображение асинхронно
    try:
        compressed_image_path = await compress_image(image_path)
        # Передаем изображение без использования временного файла, если размер позволяет
        if os.path.getsize(compressed_image_path) < 5 * 1024 * 1024:  # Проверяем размер файла (5 MB)
            photo = FSInputFile(compressed_image_path)  # Создаем объект FSInputFile с путем к изображению
            # Отправляем изображение вместе с описанием
            await message.answer_photo(photo, caption=description)
        else:
            await message.answer("Изображение слишком большое для отправки. Пожалуйста, попробуйте другое.")

        # Удаляем временный файл после отправки
        os.remove(compressed_image_path)

    except FileNotFoundError:
        await message.answer(f"Изображение для производителя '{manufacturer}' не найдено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

    # Получаем список продуктов по выбранному производителю
    products = get_products_by_manufacturer(manufacturer)

    if products:
        buttons = [KeyboardButton(text=f"{product['name']} - {product['price']} руб.") for product in products]
        buttons.append(KeyboardButton(text="🔙 Назад"))
        keyboard = ReplyKeyboardMarkup(
            keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
            resize_keyboard=True
        )
        await message.answer("Выберите продукт для добавления в корзину:", reply_markup=keyboard)
        await state.update_data(selected_manufacturer=manufacturer)  # Обновление состояния
        await state.set_state(Goods.product_selection)
    else:
        await message.answer("Продукты не найдены.", reply_markup=get_category_menu())


@router.message(Goods.product_selection)
async def select_product(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        data = await state.get_data()
        category = data.get("selected_category", "")
        manufacturer = data.get("selected_manufacturer", "")

        if manufacturer:
            manufacturers = get_manufacturers_by_category(category)
            if manufacturers:
                buttons = [KeyboardButton(text=manufacturer) for manufacturer in manufacturers]
                buttons.append(KeyboardButton(text="🔙 Назад"))
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
                    resize_keyboard=True
                )
                await message.answer("Выберите производителя:", reply_markup=keyboard)
                await state.set_state(Goods.manufacturer)
            else:
                products = get_products_by_category(category)
                if products:
                    buttons = [KeyboardButton(text=f"{product['name']} - {product['price']} руб.") for product in products]
                    buttons.append(KeyboardButton(text="🔙 Назад"))
                    keyboard = ReplyKeyboardMarkup(
                        keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
                        resize_keyboard=True
                    )
                    await message.answer("Выберите продукт для добавления в корзину:", reply_markup=keyboard)
                    await state.set_state(Goods.product_selection)
                else:
                    await message.answer("Продукты не найдены.", reply_markup=get_category_menu())
        else:
            await message.answer("Выберите категорию:", reply_markup=get_category_menu())
            await state.set_state(Goods.category)
        return

    product_info = message.text.split(" - ")
    if len(product_info) == 2:
        product_name = product_info[0]
        product = get_product_by_name(product_name)

        if product:
            await message.answer(
                f"Вы выбрали продукт: {product['name']}. Цена: {product['price']} руб.\nВведите количество:"
            )
            await state.update_data(selected_product=product)
            await state.set_state(Goods.quantity)
            # Показать кнопки для ввода количества
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔙 Назад")]
                ],
                resize_keyboard=True
            )
            await message.answer("Введите количество товара или нажмите '🔙 Назад':", reply_markup=keyboard)
        else:
            await message.answer("Ошибка при получении данных о продукте.")
    else:
        await message.answer("Некорректный формат выбора продукта. Пожалуйста, выберите продукт из списка.")



@router.message(Goods.quantity)
async def handle_quantity(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        data = await state.get_data()
        manufacturer = data.get("selected_manufacturer", "")

        if manufacturer:
            products = get_products_by_manufacturer(manufacturer)
            buttons = [KeyboardButton(text=f"{product['name']} - {product['price']} руб.") for product in products]
            buttons.append(KeyboardButton(text="🔙 Назад"))
            keyboard = ReplyKeyboardMarkup(keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
                                           resize_keyboard=True)
            await message.answer(f"Вы вернулись к выбору продуктов от производителя '{manufacturer}'.",
                                 reply_markup=keyboard)
            await state.set_state(Goods.product_selection)
        else:
            await message.answer("Выберите категорию:", reply_markup=get_category_menu())
            await state.set_state(Goods.category)
        return

    if message.text.isdigit():
        quantity = int(message.text)
        data = await state.get_data()
        product = data.get('selected_product')

        if product:
            user_id = message.from_user.id
            initialize_user(user_id)
            cart = user_data[user_id].get('cart', {})
            product_id = product['name']
            if product_id in cart:
                cart[product_id]['quantity'] += quantity
            else:
                cart[product_id] = {
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity
                }
            user_data[user_id]['cart'] = cart

            cart_info = format_cart(user_id)
            await message.answer(f"Добавлено {quantity} шт. {product['name']} в корзину.\n\n{cart_info}")

            # Возвращаемся к выбору продуктов
            manufacturer = data.get("selected_manufacturer", "")
            if manufacturer:
                products = get_products_by_manufacturer(manufacturer)
                buttons = [KeyboardButton(text=f"{product['name']} - {product['price']} руб.") for product in products]
                buttons.append(KeyboardButton(text="🔙 Назад"))
                keyboard = ReplyKeyboardMarkup(keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)],
                                               resize_keyboard=True)
                await message.answer("Выберите продукт для добавления в корзину:", reply_markup=keyboard)
                await state.set_state(Goods.product_selection)
            else:
                await message.answer("Выберите категорию:", reply_markup=get_category_menu())
                await state.set_state(Goods.category)
        else:
            await message.answer("Продукт не выбран. Пожалуйста, выберите продукт снова.")
    else:
        await message.answer("Пожалуйста, введите корректное количество товара.")

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
