# Хранилище данных пользователей
user_data = {}

# Инициализация данных пользователя
def initialize_user(user_id: int):
    if user_id not in user_data:
        user_data[user_id] = {
            'cart': {}  # Корзина пользователя
        }

# Функция удаления товара из корзины
# Функция удаления товара из корзины
def remove_from_cart(user_id: int, item_id: str):
    """Удаление товара из корзины пользователя."""
    if user_id in user_data and item_id in user_data[user_id]['cart']:
        del user_data[user_id]['cart'][item_id]

# Функция добавления товара в корзину
import logging

# Функция добавления товара в корзину
import logging

def add_to_cart(user_id: int, item_id: str, quantity: int, price: float = None, name: str = None):
    initialize_user(user_id)
    cart = user_data[user_id]['cart']

    if item_id in cart:
        old_quantity = cart[item_id]['quantity']
        cart[item_id]['quantity'] += quantity
        logging.info(f"Item '{item_id}' updated. Old quantity: {old_quantity}, New quantity: {cart[item_id]['quantity']}")
        if cart[item_id]['quantity'] <= 0:
            logging.info(f"Item '{item_id}' quantity is <= 0, removing from cart.")
            del cart[item_id]
    else:
        if quantity > 0 and price is not None and name is not None:
            cart[item_id] = {
                'quantity': quantity,
                'price': price,
                'name': name
            }
            logging.info(f"Item '{item_id}' added to cart. Quantity: {quantity}, Price: {price}, Name: {name}")
