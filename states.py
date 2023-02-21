from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterStatesGroup(StatesGroup):
    command_name = State()
    captain_name = State()
    email = State()
    phone = State()
    finish_state = State()
