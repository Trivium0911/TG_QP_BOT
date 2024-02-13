from dataclasses import dataclass
from bs4 import BeautifulSoup
import datetime
import requests
import json
import time
import os

URL = os.getenv('URL')
URL_POST = os.getenv('URL_POST')
stop_list = ["новички", 'полуфинал', 'финал', 'сезона игр']
b_days = {
    "Надя": "11.03",
    "Дима Кужелевский": "09.04",
    "Антон": "12.04",
    "Натали": "04.10",
    "Саша Юшкевич": "09.30",
    "Дима Бориков": "02.10",
    "Катя Фалюк": "11.23",
    "Строгий": "07.12",
    "Кирилл": "09.24",
    "Бандэрос": "12.22",
    "Гребень": "12.25",
    "Игорёк": "07.07",
    "Марина": "06.16",
    "Елена": "11.08",
    }


@dataclass
class Data:
    url = str
    lst = list


def get_ids(url: Data) -> list:
    response = get_page(url=url)
    soup = BeautifulSoup(response.text, 'lxml')
    lst = [x.attrs['id'] for x in soup.find_all('div',
                                                class_='schedule-column')
           if all([i not in x.text.lower() for i in stop_list])]
    return lst


def get_page(url: Data) -> requests.get:
    response = requests.get(url=URL)
    response.encoding = 'utf-8-sig'
    return response


def get_actual_games(url: Data) -> None:
    response = get_page(url)
    soup = BeautifulSoup(response.text, 'lxml')
    lst = [x.text for x in soup.find_all('div', class_='schedule-column')
           if all([i not in x.text.lower() for i in stop_list])]
    res = ['Актуальные игры:  \n']
    for i in lst:
        lst_res = i.replace('\n', ' ').split('  ')
        res.append(f"{lst_res[1].strip()}, {lst_res[2].strip()}, "
                   f"{lst_res[6].strip()} \n")
        time.sleep(1)
    with open('games.txt', 'w', encoding='utf-8-sig') as file:
        file.writelines(res)
    return


def post_inf(url: str, lst: list, user_info: list) -> None:
    res = []
    for i in lst:
        dct = {
            'QpRecord[teamName]': user_info[0],
            'QpRecord[captainName]': user_info[1],
            'QpRecord[email]': user_info[2],
            'QpRecord[phone]': user_info[3],
            'QpRecord[count]': '9',
            'QpRecord[custom_fields_values]': '[]',
            'QpRecord[comment]': '',
            'QpRecord[game_id]': f'{i}',
            'QpRecord[reserve]': '0',
            'reservation': '',
            'QpRecord[site_content_id]': '',
            'have_cert': '1',
            'certificates[]': '',
            'QpRecord[payment_type]': '2',
        }
        s = requests.Session()
        response = s.post(url, dct)
        response.encoding = 'utf-8-sig'
        res.append(response.json())
    with open('reginfo.json', 'w') as file:
        json.dump(res, file, indent=4, ensure_ascii=False)


def check_b_days(dct: dict) -> str:
    today = datetime.date.today()
    res = ""
    for k, v in dct.items():
        date_m, date_d = [int(i) for i in v.split(".")]
        b_day_date = datetime.date(today.year, date_m, date_d)
        delta = b_day_date - today
        if 0 <= delta.days <= 14:
            res += f"Напоминаю, скоро ДР у {k} - {v}\n"
    return res


def main():
    games = get_actual_games(url=URL)
    games_ids = get_ids(url=URL)
    post_inf(url=URL_POST, lst=games_ids)


if __name__ == '__main__':
    main()
