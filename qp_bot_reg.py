import json
import telebot as telebot
from flask import Flask, request
from aiogram import Bot, Dispatcher, executor, types
from main import get_actual_games, get_ids, post_inf
import os
from aiogram.dispatcher.filters import Text


BOT_TOKEN = str(os.getenv('BOT_TOKEN'))
bot2 = telebot.TeleBot(BOT_TOKEN)
APP_URL = os.getenv("APP_URL")
URL = os.getenv('URL')
URL_POST = os.getenv('URL_POST')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
server = Flask(__name__)


@server.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot2.process_new_updates([update])
    return '!', 200

@server.route('/')
def webhook():
    bot2.remove_webhook()
    bot2.set_webhook(url=APP_URL)


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

    get_actual_games(URL)

    res = ['Актуальные игры:  \n']
    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            lst_res = line.replace('\n', ' ').split('  ')
            res.append(f"{lst_res[1].strip()}, {lst_res[2].strip()}, {lst_res[6].strip()} \n")
        for strin in res:
            await message.answer(strin)


@dp.message_handler(Text(equals='Регистрация на всё'))
async def reg_games(message: types.Message):
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
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


if __name__ == '__main__':
    main()




