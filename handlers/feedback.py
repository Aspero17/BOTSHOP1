import logging
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data.usersdb import get_user_info  # Импортируем функцию для получения информации о пользователе
from keyboards.main import get_main_menu

# Укажите ID чата для обратной связи
FEEDBACK_CHAT_ID = -1002204868225  # Замените на ID чата для обратной связи

router = Router()

# Определение состояний для обратной связи
class FeedbackForm(StatesGroup):
    waiting_for_message = State()

# Клавиатура с кнопкой "Назад"
def get_back_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Обработчик команды "Обратная связь"
@router.message(F.text == "✉ Обратная связь")
async def feedback_start(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.full_name} выбрал 'Обратная связь'")
    await message.answer("Пожалуйста, напишите ваше сообщение, и мы передадим его в нашу службу поддержки.",
                         reply_markup=get_back_keyboard())
    await state.set_state(FeedbackForm.waiting_for_message)

# Обработчик сообщения обратной связи
@router.message(FeedbackForm.waiting_for_message)
async def process_feedback_message(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        # Возвращаем пользователя на предыдущий экран
        await message.answer("Вы вернулись в меню.", reply_markup=get_main_menu())
        await state.clear()
        return

    user_id = message.from_user.id

    # Получаем данные пользователя из базы данных
    user_info = get_user_info(user_id)
    user_name = user_info.get('name', "Имя не указано")
    user_phone = user_info.get('phone', "Телефон не указан")

    # Сообщение от пользователя
    feedback_message = message.text

    # Формируем сообщение для отправки в чат обратной связи
    feedback_text = (
        f"Новое сообщение от пользователя:\n\n"
        f"Имя: {user_name}\n"
        f"Телефон: {user_phone}\n\n"
        f"Сообщение:\n{feedback_message}"
    )

    # Отправляем сообщение в указанный чат
    await message.bot.send_message(FEEDBACK_CHAT_ID, feedback_text)

    # Подтверждаем пользователю, что сообщение получено и возвращаем в главное меню
    await message.answer("Спасибо за ваше сообщение! Мы передадим его нашей службе поддержки.",
                         reply_markup=get_main_menu())

    # Очищаем состояние после обработки
    await state.clear()
