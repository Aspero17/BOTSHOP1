from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup
from utils.functions import get_manufacturer_keyboard

router = Router()


@router.message(Command("flour"))
async def handle_flour_category(message: types.Message):
    category = 'flour'  # Убедитесь, что категория соответствует вашему JSON
    keyboard: ReplyKeyboardMarkup = get_manufacturer_keyboard(category)

    if keyboard is None:
        await message.answer("Произошла ошибка при загрузке клавиатуры.")
    else:
        await message.answer("Выберите производителя муки:", reply_markup=keyboard)
