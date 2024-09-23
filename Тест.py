from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '1789660026:AAFdRnH8x3bniLtVhyPucGkGAP1OtaUZz8U'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

def get_main_menu() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.button(text="🛒 Товары")
    kb_builder.button(text="🛍 Корзина")
    kb_builder.row()
    kb_builder.button(text="👤 Мой профиль")
    kb_builder.button(text="✉ Обратная связь")
    return kb_builder.as_markup(resize_keyboard=True)

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_menu())

dp.include_router(router)

if __name__ == '__main__':
    dp.run_polling(bot)



###############корзина№№№№№№№№№№№№№№№№№


from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.storage import user_data, initialize_user
from keyboards.cart import get_cart_keyboard
from utils.item_details import get_item_details

router = Router()

def format_cart(user_id: int) -> str:
    cart = user_data.get(user_id, {}).get('cart', {})
    if not cart:
        return "Ваша корзина пуста."

    total_cost = 0
    cart_items = []

    for item_id, item in cart.items():
        item_total = item['price'] * item['quantity']
        total_cost += item_total
        cart_items.append(f"{item['name']} - {item['quantity']} шт. по {item['price']} руб. (Итого: {item_total} руб.)")

    return "\n".join(cart_items) + f"\n\nОбщая стоимость: {total_cost} руб."

@router.message(F.text == "🛍 Корзина")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_user(user_id)
    cart_info = format_cart(user_id)
    keyboard = get_cart_keyboard()  # Создание клавиатуры
    await message.answer(cart_info, reply_markup=keyboard)


@router.message(F.text == "🗑 Очистить корзину")
async def clear_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_user(user_id)
    user_data[user_id]['cart'] = {}
    await message.answer("Ваша корзина была очищена.", reply_markup=get_cart_keyboard())

@router.message(F.text == "➕ Добавить товар")
async def add_item_to_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_user(user_id)
    await message.answer("Введите ID товара и количество через пробел (например, 'item_id 2'): ")

@router.message(F.text == "➖ Убрать товар")
async def remove_item_from_cart(message: types.Message):
    user_id = message.from_user.id
    initialize_user(user_id)
    await message.answer("Введите ID товара и количество через пробел (например, 'item_id 1'): ")

@router.message()
async def process_add_remove_item(message: types.Message):
    user_id = message.from_user.id
    text = message.text.split()
    if len(text) < 2:
        return await message.answer("Введите команду правильно.")

    command = text[0]
    item_id = text[1]
    quantity = int(text[2]) if len(text) > 2 else 1

    if command == "➕":  # Добавление
        if item_id in user_data[user_id]['cart']:
            user_data[user_id]['cart'][item_id]['quantity'] += quantity
        else:
            item_details = get_item_details(item_id)
            user_data[user_id]['cart'][item_id] = item_details
            user_data[user_id]['cart'][item_id]['quantity'] = quantity
        await message.answer(f"Товар {item_id} добавлен в корзину.")

    elif command == "➖":  # Удаление
        if item_id in user_data[user_id]['cart']:
            if user_data[user_id]['cart'][item_id]['quantity'] > quantity:
                user_data[user_id]['cart'][item_id]['quantity'] -= quantity
            else:
                del user_data[user_id]['cart'][item_id]
            await message.answer(f"Товар {item_id} удален из корзины.")
        else:
            await message.answer("Товар не найден в корзине.")


####################

import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.products import get_flour_keyboard
from keyboards.category import get_category_menu
from utils.storage import user_data, get_products_in_category
from keyboards.main import get_main_menu

router = Router()

class Goods(StatesGroup):
    category = State()
    products = State()

@router.message(F.text == "🛒 Товары")
async def show_goods(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал раздел 'Товары'")
    await message.answer("Выберите категорию:", reply_markup=get_category_menu())
    await state.set_state(Goods.category)



@router.message(F.text == "🍚 Мука")
async def flour_menu(message: types.Message):
    await message.answer("Выберите производителя муки:", reply_markup=get_flour_keyboard())

@router.message(F.text.in_([
    "Производитель 1",
    "Производитель 2",
    "Производитель 3",
    "Производитель 4",
    "Производитель 5",
    "Производитель 6",
    "Производитель 7"
]))
async def show_flour_details(message: types.Message):
    manufacturer = message.text
    await message.answer(f"Информация о {manufacturer}.")

@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Возвращаемся в меню категорий.", reply_markup=get_main_menu())


    ########## ЭТО ФАЙЛ GOODS

    import logging
    from aiogram import types, Router, F
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from utils.functions import get_manufacturer_keyboard, get_products_in_category
    from keyboards.main import get_main_menu
    from keyboards.category import get_category_menu
    from utils.functions import get_products_in_category

    router = Router()

    class Goods(StatesGroup):
        category = State()
        manufacturer = State()
        product_selection = State()  # Добавлено для выбора продукта

    @router.message(F.text == "🛒 Товары")
    async def show_goods(message: types.Message, state: FSMContext):
        logging.info("Пользователь выбрал раздел 'Товары'")
        await message.answer("Выберите категорию:", reply_markup=get_category_menu())
        await state.set_state(Goods.category)

    @router.message(Goods.category)
    async def handle_category_selection(message: types.Message, state: FSMContext):
        category = message.text
        logging.info("Пользователь выбрал категорию: %s", category)

        if category == "🔙 Назад":
            await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
            await state.clear()
        else:
            # Используем функцию для генерации клавиатуры
            keyboard = get_manufacturer_keyboard(category)
            if keyboard:
                category_name = get_category_name(category)  # Получаем название категории для сообщения
                await message.answer(f"Выберите {category_name}:", reply_markup=keyboard)
                await state.set_state(Goods.manufacturer)
            else:
                await message.answer("Категория не найдена или произошла ошибка.", reply_markup=get_category_menu())

    def get_category_name(category_key):
        """Функция для получения названия категории по ключу."""
        category_names = {
            "flour": "производителя муки",
            "yeast": "производителя дрожжей",
            "butter": "производителя масла",
            "salt_soda_sugar": "производителя соли, соды и сахара",
            "eggs": "продуктов из яиц",
            "rice": "продуктов из риса",
            "vinegar": "производителя уксуса",
            "spices": "приправ"
        }
        return category_names.get(category_key, "товары")

    @router.message(Goods.manufacturer)
    async def handle_manufacturer_selection(message: types.Message, state: FSMContext):
        manufacturer = message.text
        logging.info("Пользователь выбрал производителя: %s", manufacturer)

        if manufacturer == "🔙 Назад":
            await message.answer("Вы вернулись в меню категорий.", reply_markup=get_category_menu())
            await state.set_state(Goods.category)
        else:
            try:
                # Получаем все продукты для выбранной категории
                category = get_products_in_category(await state.get_state())
                products = get_products_in_category(category)

                if not products:
                    await message.answer("Не удалось загрузить данные о продуктах.")
                    return

                # Фильтруем продукты по выбранному производителю
                filtered_products = {
                    product_id: product_info
                    for product_id, product_info in products.items()
                    if product_info.get('manufacturer') == manufacturer
                }

                if filtered_products:
                    # Создаем сообщение с кнопками для выбора количества
                    products_message = []
                    for product_id, product_info in filtered_products.items():
                        name = product_info['name']
                        price = product_info.get('price', 'Цена не указана')
                        button_text = f"{name} - {price} руб."
                        button = InlineKeyboardButton(button_text, callback_data=f"select_product:{product_id}")
                        products_message.append(button)

                    markup = InlineKeyboardMarkup(row_width=1)
                    markup.add(*products_message)
                    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_category"))

                    await message.answer("Выберите продукт для добавления в корзину:", reply_markup=markup)
                    await state.set_state(Goods.product_selection)
                else:
                    await message.answer(f"Продукты от производителя '{manufacturer}' не найдены.",
                                         reply_markup=get_manufacturer_keyboard(category))
            except Exception as e:
                logging.error("Ошибка при обработке выбора производителя: %s", e)
                await message.answer("Произошла ошибка. Попробуйте снова.",
                                     reply_markup=get_manufacturer_keyboard(category))

    @router.callback_query(lambda c: c.data and c.data.startswith('select_product:'))
    async def select_product(callback: types.CallbackQuery, state: FSMContext):
        product_id = callback.data.split(':')[1]
        # Сохраните выбранный продукт и запросите количество
        await state.update_data(product_id=product_id)
        await callback.message.answer("Введите количество товара:")
        await state.set_state(Goods.product_selection)

    @router.message(Goods.product_selection)
    async def handle_product_quantity(message: types.Message, state: FSMContext):
        try:
            quantity = int(message.text)
            user_data = await state.get_data()
            product_id = user_data.get('product_id')

            # Здесь нужно реализовать логику добавления товара в корзину
            # Например, обновить корзину пользователя в базе данных

            await message.answer(f"Товар добавлен в корзину. Количество: {quantity}")
            await message.answer("Выберите следующую категорию:", reply_markup=get_category_menu())
            await state.clear()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число.")



################## ФАЙЛ FUNCTIONS

from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging
import json


def get_manufacturer_keyboard(category):
    try:
        with open('data/categories.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error("Файл 'data/categories.json' не найден.")
        return None
    except json.JSONDecodeError:
        logging.error("Ошибка декодирования JSON.")
        return None
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return None

    category_data = data['categories'].get(category)
    if not category_data:
        logging.error(f"Категория '{category}' не найдена в файле.")
        return None

    manufacturers = category_data.get('manufacturers', [])
    products = category_data.get('products', {})

    keyboard = ReplyKeyboardBuilder()

    if manufacturers:
        for manufacturer in manufacturers:
            keyboard.row(KeyboardButton(text=manufacturer))
    else:
        for product_key, product_info in products.items():
            product_name = product_info['name']
            price = product_info.get('price')
            if price is not None:
                product_name += f" - {price} руб."
            keyboard.row(KeyboardButton(text=product_name))

    keyboard.row(KeyboardButton(text="🔙 Назад"))

    return keyboard.as_markup(resize_keyboard=True)


def get_products_in_category(category):
    try:
        with open('data/categories.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error("Файл 'data/categories.json' не найден.")
        return None
    except json.JSONDecodeError:
        logging.error("Ошибка декодирования JSON.")
        return None
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return None

    category_data = data['categories'].get(category)
    if not category_data:
        logging.error(f"Категория '{category}' не найдена в файле.")
        return None

    return category_data.get('products', {})


def get_flour_types_keyboard(products):
    """Создает клавиатуру для выбора видов муки."""
    keyboard = ReplyKeyboardBuilder()

    for product_key, product_info in products.items():
        product_name = product_info['name']
        price = product_info.get('price', 'Цена не указана')
        button_text = f"{product_name} - {price} руб."
        keyboard.row(KeyboardButton(text=button_text))

    keyboard.row(KeyboardButton(text="🔙 Назад"))

    return keyboard.as_markup(resize_keyboard=True)


def get_add_to_cart_keyboard():
    """Создает клавиатуру для выбора количества товара для добавления в корзину."""
    quantities = [1, 2, 3, 5, 10]
    keyboard = ReplyKeyboardBuilder()

    for quantity in quantities:
        keyboard.row(KeyboardButton(text=f"{quantity} шт."))

    keyboard.row(KeyboardButton(text="🔙 Назад"))
    return keyboard.as_markup(resize_keyboard=True)


def get_product_preview_keyboard(products):
    """Создает клавиатуру для предварительного просмотра товаров и выбора количества."""
    keyboard = InlineKeyboardMarkup(row_width=1)

    for product_id, product_info in products.items():
        name = product_info['name']
        price = product_info.get('price', 'Цена не указана')
        button_text = f"{name} - {price} руб."
        button = InlineKeyboardButton(button_text, callback_data=f"select_product:{product_id}")
        keyboard.add(button)

    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_category"))

    return keyboard



################# ФАЙЛ GOODS

import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.main import get_main_menu
from keyboards.category import get_category_menu
from TEST.database import get_manufacturers, get_products_by_manufacturer

router = Router()

class Goods(StatesGroup):
    category = State()
    manufacturer = State()
    product_selection = State()  # Добавлено для выбора продукта

@router.message(F.text == "🛒 Товары")
async def show_goods(message: types.Message, state: FSMContext):
    logging.info("Пользователь выбрал раздел 'Товары'")
    await message.answer("Выберите категорию:", reply_markup=get_category_menu())
    await state.set_state(Goods.category)

@router.message(Goods.category)
async def handle_category_selection(message: types.Message, state: FSMContext):
    category = message.text
    logging.info("Пользователь выбрал категорию: %s", category)

    if category == "🔙 Назад":
        await message.answer("Вы вернулись в главное меню.", reply_markup=get_main_menu())
        await state.clear()
    else:
        # Используем базу данных для получения производителей по категории
        manufacturers = get_manufacturers(category)
        if manufacturers:
            keyboard = InlineKeyboardMarkup(row_width=1)
            for manufacturer in manufacturers:
                button = InlineKeyboardButton(manufacturer, callback_data=f"select_manufacturer:{manufacturer}")
                keyboard.add(button)
            keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu"))
            await message.answer(f"Выберите производителя для категории '{category}':", reply_markup=keyboard)
            await state.set_state(Goods.manufacturer)
        else:
            await message.answer("Категория не найдена или произошла ошибка.", reply_markup=get_category_menu())

@router.callback_query(lambda c: c.data and c.data.startswith('select_manufacturer:'))
async def handle_manufacturer_selection(callback: types.CallbackQuery, state: FSMContext):
    manufacturer = callback.data.split(':')[1]
    logging.info("Пользователь выбрал производителя: %s", manufacturer)

    try:
        # Получаем все продукты для выбранного производителя
        products = get_products_by_manufacturer(manufacturer)

        if not products:
            await callback.message.answer("Не удалось загрузить данные о продуктах.")
            return

        # Создаем сообщение с кнопками для выбора количества
        products_message = []
        for product in products:
            name = product['name']
            price = product.get('price', 'Цена не указана')
            button_text = f"{name} - {price} руб."
            button = InlineKeyboardButton(button_text, callback_data=f"select_product:{product['id']}")
            products_message.append(button)

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(*products_message)
        markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_category"))

        await callback.message.answer("Выберите продукт для добавления в корзину:", reply_markup=markup)
        await state.set_state(Goods.product_selection)
    except Exception as e:
        logging.error("Ошибка при обработке выбора производителя: %s", e)
        await callback.message.answer("Произошла ошибка. Попробуйте снова.", reply_markup=get_category_menu())

@router.callback_query(lambda c: c.data and c.data.startswith('select_product:'))
async def select_product(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.split(':')[1]
    # Сохраните выбранный продукт и запросите количество
    await state.update_data(product_id=product_id)
    await callback.message.answer("Введите количество товара:")
    await state.set_state(Goods.product_selection)

@router.message(Goods.product_selection)
async def handle_product_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        user_data = await state.get_data()
        product_id = user_data.get('product_id')

        # Здесь нужно реализовать логику добавления товара в корзину
        # Например, обновить корзину пользователя в базе данных

        await message.answer(f"Товар добавлен в корзину. Количество: {quantity}")
        await message.answer("Выберите следующую категорию:", reply_markup=get_category_menu())
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
