from main import get_actual_games, get_ids, post_inf
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
import logging
import aiogram
import json
import os

BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
APP_URL = os.getenv("APP_URL")
URL = os.getenv('URL')
URL_POST = os.getenv('URL_POST')

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await bot.set_my_commands([
        aiogram.types.BotCommand("start", "it is start command..."),
    ])


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer('Ну что, косяк, пора бы тебе напомнить про регистрацию на игры')
    start_buttons = ['Текущие игры Квиз Плиз', 'Регистрация на все игры', 'Всё херня, давай по-новой', 'Сформировать шаблон']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer('Что ж, погнали!', reply_markup=keyboard)


@dp.message_handler(Text(equals='Текущие игры Квиз Плиз'))
async def get_games(message: types.Message):
    await message.answer('Please wait...')

    get_actual_games(URL)

    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            await message.answer(line)


@dp.message_handler(Text(equals='Регистрация на все игры'))
async def get_games(message: types.Message):
    await message.answer('Please wait...')

    lst = get_ids(url=URL)
    post_inf(url=URL_POST, lst=lst)

    with open('reginfo.json', 'r') as file:
        load = json.load(file)
        for line in load:
            await message.answer(f"Успех: {line['success']} \n"
                                 f"{line['successMsg'].replace('<br>', ' ')}")


@dp.message_handler(Text(equals='Сформировать шаблон'))
async def make_form(message: types.Message):
    await message.answer('Шаблон')
    res = ''
    pre = '\nСостав на игру '
    nums = '\n1. \n2. \n3. \n4. \n5. \n6. \n7. \n8. \n9. \n\n'

    get_actual_games(URL)

    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            if 'Актуальные игры:' in line:
                continue
            res += pre + f"{line.strip()}:\n" + nums

    await message.answer(res)
    res = ''


def main():

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


if __name__ == '__main__':
    main()


