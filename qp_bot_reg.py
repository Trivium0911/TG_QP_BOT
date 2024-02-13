from database import start_db, edit_profile, create_user, check_user, \
    get_user_info
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import get_main_kb, get_register_kb, \
    get_cancel_kb, get_register_check_kb
from main import get_actual_games, get_ids, post_inf, check_b_days, \
    b_days
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher import FSMContext
from states import RegisterStatesGroup
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
users_id_list = [
    str(os.getenv('OWNER')),
    str(os.getenv('GUEST_1')),
    str(os.getenv('GUEST_2')),
    str(os.getenv("GUEST_3")),
]
APP_NAME = os.getenv('APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{APP_NAME}.onrender.com'
WEBHOOK_PATH = f''
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', default=3001))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


async def on_startup(dispatcher):
    await start_db()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await bot.set_my_commands([
        aiogram.types.BotCommand("start", "it is start command..."),
    ])


async def on_shutdown(dispatcher):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    user_id = message.from_user.id
    if not (str(user_id) in users_id_list):
        await message.answer('В доступе отказано')
    else:
        if not (check_user(user_id=message.from_user.id)):
            await message.answer("Это твой первый визит. "
                                 "Давай-ка зарегистрируемся",
                                 reply_markup=get_register_kb())
        else:
            await message.answer('Welcome to the club, buddy')
            await message.answer('Что ж, погнали!',
                                 reply_markup=get_main_kb())


@dp.message_handler(Text(equals="Отмена"), commands='Отмена')
@dp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cansel_func(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if not current_state:
        return
    await state.finish()
    await message.answer("Запустите бота заново")
    await message.delete()


@dp.message_handler(Text(equals="Регистрация пользователя"))
async def make_registration(message: types.Message) -> None:
    await create_user(user_id=message.from_user.id)
    await message.reply("Вы перешли в форму регистрации.",
                        reply_markup=types.ReplyKeyboardRemove())
    await RegisterStatesGroup.command_name.set()
    await message.answer("Пожалуйста, введите название команды:",
                         reply_markup=get_cancel_kb())


@dp.message_handler(state=RegisterStatesGroup.command_name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["command_name"] = message.text
    await RegisterStatesGroup.next()
    await message.reply("Пожалуйста, введите имя капитана:",
                        reply_markup=get_cancel_kb())


@dp.message_handler(state=RegisterStatesGroup.captain_name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["captain_name"] = message.text
    await RegisterStatesGroup.next()
    await message.reply("Пожалуйста, введите email:",
                        reply_markup=get_cancel_kb())


@dp.message_handler(state=RegisterStatesGroup.email)
async def get_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["email"] = message.text
    await RegisterStatesGroup.next()
    await message.reply("Пожалуйста, введите номер телефона:"
                        "(без +375, знаков тире и пробелов)",
                        reply_markup=get_cancel_kb())


@dp.message_handler(state=RegisterStatesGroup.phone)
async def get_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['phone'] = message.text
    await RegisterStatesGroup.next()
    await message.answer("Пожалуйста, проверьте правильность "
                         "введенных данных. Если всё верно, "
                         "нажмите кнопку 'Завершить'.\n\n"
                         f"Команда:   {data['command_name']} \n"
                         f"Капитан:   {data['captain_name']}\n"
                         f"Email:   {data['email']}\n"
                         f"Телефон:  +375 {data['phone']}",
                         reply_markup=get_register_check_kb())


@dp.message_handler(Text(equals="Исправить данные"),
                    state=RegisterStatesGroup.finish_state)
async def register_fix(message: types.Message, state: FSMContext) -> None:
    await RegisterStatesGroup.command_name.set()
    await message.answer("Пожалуйста, введите своё имя:",
                         reply_markup=get_cancel_kb())


@dp.message_handler(Text(equals="Завершить"),
                    state=RegisterStatesGroup.finish_state)
async def start_func(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        await edit_profile(state=state, user_id=message.from_user.id)
    await state.finish()
    await message.answer(text="Операция успешно завершена.",
                         reply_markup=get_main_kb())


@dp.message_handler(Text(equals='Текущие игры Квиз Плиз'))
async def get_games(message: types.Message):
    await message.answer('Please wait...')

    get_actual_games(URL)

    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            await message.answer(line)


@dp.message_handler(Text(equals='Регистрация на все игры'))
async def reg_games(message: types.Message):
    await message.answer('Please wait...')
    lst = get_ids(url=URL)
    user_info = get_user_info(user_id=message.from_user.id)
    post_inf(url=URL_POST, lst=lst, user_info=user_info)

    with open('reginfo.json', 'r') as file:
        load = json.load(file)
        for line in load:
            await message.answer(f"Успех: {line['success']} \n"
                                 f"{line['successMsg'].replace('<br>', ' ')}")


@dp.message_handler(Text(equals='Сформировать шаблон'))
async def make_form(message: types.Message):
    await message.answer('Шаблон')
    res = '\n'
    pre = '\nСостав на игру '
    nums = '\n1. \n2. \n3. \n4. \n5. \n6. \n7. \n8. \n9. \n\n'

    get_actual_games(URL)

    with open('games.txt', 'r', encoding='utf-8-sig') as file:
        for line in file:
            if 'Актуальные игры:' in line:
                continue
            res += pre + f"{line.strip()}:\n\n" + nums + "\n\n"
    res += check_b_days(b_days)
    await message.answer(res)
    res = ''


def main():
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
