import logging  # Импорт для настройки логирования
from aiogram import Bot, Dispatcher  # Импорт для работы с ботом и обработчиками сообщений
from aiogram.fsm.storage.memory import MemoryStorage  # Импорт для хранения состояний в памяти
from handlers import registration, profile, goods, general, cart, editcart # Импорт обработчиков для различных функциональностей
from config import API_TOKEN  # Импорт токена API для бота
from handlers.feedback import router as feedback_router  # Импорт маршрутизатора для обработки обратной связи
from utils.database import initialize_db  # Инициализации базы данных 123156165
from data.usersdb import initialize_users_db
from handlers.admin import router as admin_router
# Настройка базового уровня логирования для отслеживания информации
logging.basicConfig(level=logging.INFO)

# Создание экземпляра бота с использованием токена API
bot = Bot(token=API_TOKEN)

# Создание экземпляра диспетчера с использованием хранилища состояний в памяти
dp = Dispatcher(storage=MemoryStorage())

# Регистрация маршрутизаторов (обработчиков) для различных функциональностей
dp.include_router(feedback_router)  # Обработчик для обратной связи
dp.include_router(registration.router)  # Обработчик для регистрации пользователей
dp.include_router(profile.router)  # Обработчик для управления профилем пользователя
dp.include_router(goods.router)  # Обработчик для работы с товарами
dp.include_router(general.router)  # Обработчик для общих команд и запросов

dp.include_router(editcart.router)
dp.include_router(cart.router)
dp.include_router(admin_router)

# Инициализация базы данных
initialize_db()

# Инициализация базы данных
initialize_users_db()

# Запуск бота в режиме опроса
if __name__ == '__main__':
    dp.run_polling(bot)
