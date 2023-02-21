import sqlite3 as sq
from aiogram.dispatcher import FSMContext


async def start_db() -> None:
    global db, cur
    db = sq.connect('database.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY,"
                "command_name TEXT, captain_name TEXT, email TEXT, phone TEXT)")
    db.commit()


async def create_user(user_id: str) -> None:
    user = cur.execute("SELECT 1 FROM users "
                       "WHERE user_id == '{}'".format(user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?,?,?,?,?)",
                    (user_id, '', '', '', ''))
        db.commit()


def get_user_info(user_id: str) -> list:
    user_info = cur.execute("SELECT command_name, captain_name, email, phone "
                            "FROM users WHERE user_id = "
                            "'{}'".format(user_id)).fetchall()
    return [
        user_info[0][0],
        user_info[0][1],
        user_info[0][2],
        user_info[0][3]
    ]


async def edit_profile(state: FSMContext, user_id: str) -> None:
    async with state.proxy() as data:
        cur.execute("UPDATE users SET command_name = '{}',"
                    "captain_name = '{}', "
                    "email = '{}', phone = '{}' "
                    "WHERE user_id == '{}'".format(
                        data['command_name'], data['captain_name'],
                        data['email'], data['phone'], user_id)
                    )
        db.commit()


def check_user(user_id: str) -> tuple:
    user = cur.execute("SELECT 1 FROM users "
                       "WHERE user_id == '{}'".format(user_id)).fetchone()
    return user
