import json
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.executor import start_webhook

from main import get_games, get_ids, post_inf
import os
from aiogram.dispatcher.filters import Text


URL = os.getenv('URL')
URL_POST = os.getenv('URL_POST')
bot = Bot(token=str(os.getenv("BOT_TOKEN")))
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('Ну что, косяк, пора бы тебе напомнить про регистрацию на игры')
    start_buttons = ['Текущие игры КП', 'Регистрация на всё', 'Сначала']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Что ж, погнали!', reply_markup=keyboard)


@dp.message_handler(Text(equals='Текущие игры КП'))
async def get_games(message: types.Message):
    await message.answer('Please wait...')

    get_games(URL)

    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            await message.answer(line)


@dp.message_handler(Text(equals='Регистрация на всё'))
async def get_games(message: types.Message):
    await message.answer('Please wait...')

    lst = get_ids(url=URL)
    post_inf(url=URL_POST, lst=lst)

    with open('reginfo.json', 'r') as file:
        load = json.load(file)
        for line in load:
            await message.answer(f"Успех: {line['success']} \n"
                                 f"{line['successMsg'].replace('<br>', ' ')}")


@dp.message_handler(Text(equals='Назад'))
async def start_again(message: types.Message):
    await message.answer('Ну что, косяк, пора бы тебе напомнить про регистрацию на игры')
    start_buttons = ['Текущие игры КП', 'Регистрация на всё', 'Сначала']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Что ж, погнали!', reply_markup=keyboard)


def main():
    executor.start_polling(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


