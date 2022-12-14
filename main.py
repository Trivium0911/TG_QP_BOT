from dataclasses import dataclass
import json
import time
from bs4 import BeautifulSoup
import requests
import os

URL = os.getenv('URL')
URL_POST = os.getenv('URL_POST')
stop_list = ["новички", 'полуфинал', 'финал', 'сезона игр']


@dataclass
class Data:
    url = str
    lst = list


def get_ids(url: Data):
    response = get_page(url=url)
    soup = BeautifulSoup(response.text, 'lxml')
    lst = [x.attrs['id'] for x in soup.find_all('div',
                                                class_='schedule-column')
           if all([i not in x.text.lower() for i in stop_list])]
    return lst


def get_page(url: Data):
    response = requests.get(url=URL)
    response.encoding = 'utf-8-sig'
    return response


def get_actual_games(url: Data):
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


def post_inf(url: Data, lst: Data):
    res = []
    for i in lst:
        dct = {
            'QpRecord[teamName]': os.getenv('TEAM'),
            'QpRecord[captainName]': os.getenv('CAPTAIN'),
            'QpRecord[email]': os.getenv('EMAIL'),
            'QpRecord[phone]': os.getenv('PHONE'),
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


def main():
    games = get_actual_games(url=URL)
    games_ids = get_ids(url=URL)
    post_inf(url=URL_POST, lst=games_ids)


if __name__ == '__main__':
    main()
