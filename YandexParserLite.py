""" Парсер яндекса.
    Все файлы, зависимости, настройки и логика в одном файле.
    Специально для братика :)
"""

""" Перед началом работ необходимо выполнить команду python -m pip install --upgrade pip для обновлния pip 
"""

'Перед началом работ необходимо выполнить команду pip3 install -r requirements.txt при наличии файла requirements.txt '

import asyncio
import inspect
import io
import json
import multiprocessing
import os
import subprocess
import time
from datetime import datetime
from os import listdir
from random import choice, randint, uniform
from time import monotonic, sleep
from typing import Dict, List

import pandas as pd
from idna import unicode


def checking_requirements_txt():
    """Проверка  файла requirements.txt
    """
    try:
        with open(f'{"requirements.txt"}', 'r') as file:
            requirements = file.read()
    except FileNotFoundError:
        assert False, 'Проверьте, что добавили файл requirements.txt'

    assert 'beautifulsoup4' in requirements, 'Проверьте, что beautifulsoup4 есть в файле requirements.txt'
    assert 'lxml' in requirements, 'Проверьте, что lxml есть в файле requirements.txt'
    assert 'pypiwin32' in requirements, 'Проверьте, что pypiwin32 есть в файле requirements.txt'
    assert 'certifi' in requirements, 'Проверьте, что certifi есть в файле requirements.txt'
    assert 'urllib3' in requirements, 'Проверьте, что urllib3 есть в файле requirements.txt'
    assert 'soupsieve' in requirements, 'Проверьте, что soupsieve есть в файле requirements.txt'
    assert 'pandas' in requirements, 'Проверьте, что pandas есть в файле requirements.txt'


checking_requirements_txt()


def _read_requirements(realpath: str = 'requirements.txt'):
    """ Чтение зависимостей из файла requirements.txt
        requirements.txt должен находится в тойже директории / папке с этим файлом
    """
    fullpath = os.path.join(os.path.dirname(__file__), realpath)
    with open(fullpath) as file:
        return [s.strip() for s in file.readlines()
                if (s.strip() and not s.startswith("#"))]


_REQUIREMENTS_TXT = _read_requirements(realpath="requirements.txt")
INSTALL_REQUIRES = [line for line in _REQUIREMENTS_TXT if "://" not in line]


def prepare_venv():
    """ принудительное обновление / создание / подготовка виртуального окружения и venv с помощью subprocess.call
        установка зацисимостей из requirements.txt
    """
    app_venv_name = "venv"

    if not os.path.exists(app_venv_name):
        os.makedirs(f"{app_venv_name}")
    # upgrade pip
    subprocess.call(['pip', 'install', '--upgrade'])
    # update requirements.txt and upgrade venv
    subprocess.call(['pip', 'install', '--upgrade'] + INSTALL_REQUIRES)


prepare_venv()

try:
    import win32com.client as win32
    from win32com.universal import com_error
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install -U pypiwin32 в терминале')

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install beautifulsoup4 в терминале')

try:
    import lxml
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install lxml в терминале')

try:
    import requests
    from requests import Response
    from requests.adapters import HTTPAdapter
    from requests.exceptions import ConnectTimeout, ConnectionError, ProxyError
    from requests.sessions import Session
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install requests в терминале')

try:
    from tqdm import tqdm
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install tqdm в терминале')

try:
    import traceback
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install traceback в терминале')

try:
    from selenium import webdriver
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install selenium в терминале')

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install webdriver_manager в терминале')

try:
    from proxybroker import Broker
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install proxybroker в терминале')

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# ---------------------------------- Setting ----------------------------------


PASSED = False  # включение отладки

__date__ = '16.05.2021'
__author__ = 'kokkaina13@gmail.com (Alex Korshakov)'
PARSER_NAME: str = 'ParserYandexSimplified'
print(f'Invoking __init__.py for {__name__}')

# время ожидания
TIMEOUT: int = 180

# максимальное кооличество прокси
MAX_PROXYES: int = 25

# время ожидания между отправкой повторного запроса
REQUEST_TIMEOUT = 10.24

# базовый url  для отправки запросов
HOST: str = 'https://yandex.ru'

# агент представления запроса
AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
]

# альтернативные заголовки запроса
KAD_HEAD = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': HOST,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': choice(AGENTS)
}

# используемые заголовки запроса
HEADERS = {
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'host': HOST,
    'User-Agent': choice(AGENTS)
}

# базовые заголовки запроса
HEADERS_TEST = {
    'Accept': '*/*',
    'User-Agent': choice(AGENTS)
}

# заголовки таблицы выгрузки
HEADERS_TAB = {
    'rowNom': 'п\п',  # i_row
    'ques': 'Ключ',  # url_ques
    'company_cid': 'Позиция',  # my_company_cid
    'company_link_1': 'Домен',  # my_company_link_1
    'company_url': 'URL',  # my_company_url
    'company_title': 'Заголовок',  # my_company_title
    'company_text': 'Текст',  # my_company_text
    'company_fast_links': 'БС',  # my_company_site_links
    'company_contact': 'Контакты'
}

# ---------------------------------- Servis Setting ----------------------------------


# лимит на колличество запросов с одного ip
RESPONSE_LIMIT: int = 300

# текущая директория
CURRENT_DIR = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# текущая дата
DATE_TODAY = datetime.today().strftime("%d.%m.%Y")

# полный путь к текущей директории
FULL_PATH = CURRENT_DIR + '\\'

# базовое расширение файла выгрузки
EXTENSION = '.xlsx'

# полный путь к файлу с ключами
QUERIES_PATH: str = 'queries.txt'

# полный путь к файлу с прокси
PROXY_PATH: str = 'proxieslist.txt'

# ---------------------------------- URL Setting ----------------------------------

# базовый запрос
BASE_URL_YANDEX: str = 'https://www.yandex.ru/search/ads?text='

# задаём максимальное кооличество запросов
URL_MAX_POS_YANDEX = 1

# Задаём регион. Санкт-Петербург – 2. Краснодар  - 35
# Список идентификаторов российских регионов https://tech.yandex.ru/xml/doc/dg/reference/regions-docpage/
REGION_YANDEX: int = 35

# период
# 1 – последние две недели;
# 2 – последний месяц;
# 3 – три месяца;
# 4 – полгода;
# 5 – год;
# 7 – текущие сутки(даже если новый день наступил пару минут назад, поиск будет
# ограничен именно этой парой минут);
# 77 – сутки(24 часа, независимо от того, сколько длятся секущие сутки);
# 8 – трое суток;
# 9 – неделя
WITHIN_TIME: int = 5

# колличество ссылок в каждой выдаче
NUM_DOC: int = 10  # не рекомендуется менять от слова совсем
# – определяет количество документов (ссылок), отображаемых на одной странице результатов выдачи.
#  по умолчанию = 10
# колличество одновременных процессов / потоков
MAX_PROCESS: int = 1

# ---------------------------------- Pars Setting ----------------------------------


SOUP_NAME: str = 'li'
SOUP_CLASS: str = 'serp-item'
SOUP_ATTRIBUTE: str = 'text'

# ---------------------------------- LOG Setting ----------------------------------


VIS_LOG = False  # True -  Отображение хода процесса в консоли
PRINT_LOG = True  # True -  Запись лога в файл

CONFIG = {'get_main_interval': 6,
          'get_reConnect_interval': 5,  # Time (seconds). Recommended value: 5
          'colors': True,  # True/False. True prints colorful msgs in console
          }

WRITE_TO_JSON = True

# ---------------------------------- browser setting ----------------------------------


BROWSER_SPEED: int = 1


# ---------------------------------- service functions ----------------------------------


def write_json_file(*, data: object = None, name: str = "") -> None:
    """Запись данных в json
    """
    try:
        with io.open(name + '.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4,
                              sort_keys=True,
                              separators=(',', ': '),
                              ensure_ascii=False)
            outfile.write(to_unicode(str_))
    except TypeError as err:
        l_message(calling_script(), f" TypeError: {repr(err)}", color=BColors.FAIL)


def read_json_file(file) -> list:
    """Чтение данных из json
    """
    try:
        with open(file + ".json", 'r', encoding='utf8') as data_file:
            data_loaded = json.load(data_file)
        return data_loaded
    except FileNotFoundError as err:
        l_message(calling_script(), f" FileNotFoundError: {repr(err)}", color=BColors.FAIL)


class BColors:  # colors in console
    """ Список кодов основных цветов для системных сообщений.
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def decorate_msg(msg, color=None) -> str:
    """ Returns: colored msg, if colors are enabled in config and a color is provided for msg
        msg, otherwise
    """
    msg_string = msg
    if CONFIG['colors']:
        msg_string = color + msg + BColors.ENDC
    return msg_string


def write_to_console(*, param_name: str = None, p_value=None):
    """ Запись в консоль.
    """
    try:
        if param_name == 'NLine':
            print('=' * 100)
        NOW = str(datetime.now().strftime("%d.%m.%Y %H.%M.%S")) + " :: "
        try:
            if len(p_value) < 100:
                print(NOW + f'Параметр {param_name} Значение: {p_value}')
            else:
                print(NOW + f'Параметр {param_name} Значение: {p_value[:100] + "..."}')

        except Exception as err:
            print('Не итерируемый параметр', str(err.args), True)
            print(NOW + f'Параметр {param_name} Значение: {p_value}')

    except ConnectionError as err:
        log_vis_rec(param_name='log_vis_rec: Ошибка вывода в консоль', p_value=str(err.args), r_log=True)


def write_to_text_log(*, param_name: str = None, p_value=None, d_path=None):
    """ Запись в логфайл.
    """
    NOW = str(datetime.now().strftime("%d.%m.%Y %H.%M.%S")) + " :: "
    try:
        with open(DATE_TODAY + ' ' + d_path + r'_Log.txt', 'a', encoding='utf-8') as file:
            text = NOW + f'Параметр *** {param_name} *** Значение : {p_value}'
            file.write(text + '\n')

    except ConnectionError as err:
        log_vis_rec(param_name='log_vis_rec: Ошибка записи в файл', p_value=str(err.args), r_log=True)


def log_vis_rec(*, param_name: str = None, p_value=None, d_path=None, r_log: bool = None, r_print: bool = None):
    """ Функция логирования в файл и отображения данны в консоли.
    """
    if r_log:
        write_to_console(param_name=param_name, p_value=p_value)

    if r_print:
        write_to_text_log(param_name=param_name, p_value=p_value, d_path=d_path)


def l_message(names=None, value=None, color=None, r_log=None, r_print=None) -> None:
    """ Функция логирования в файл и отображения данны в терминале.
    :rtype: None
    """
    if isinstance(r_log, type(None)):
        r_log = VIS_LOG
    if isinstance(r_print, type(None)):
        r_print = PRINT_LOG

    name = names[0]
    dir_function = names[1]

    log_vis_rec(param_name=name, p_value=value, d_path=dir_function, r_log=r_log, r_print=r_print)

    if not color:
        return
    try:
        if isinstance(name, str):
            print(decorate_msg(str(name) + ' ' + str(value), color))
        else:
            print(decorate_msg(str(name), color))
    except TypeError as err:
        print(decorate_msg("lm " + name + f" TypeError: {repr(err)}", BColors.FAIL))


def calling_script() -> object:
    """ Получение имени вызывающей функции.
    :rtype: object
    """
    return [str(traceback.extract_stack(None, 2)[0][2]),
            str(traceback.extract_stack(None, 2)[0][0]).replace('.py', '').split('/')[-1]]


# ----------------------------------  Writer functions ----------------------------------


class WriterToXLSX:
    """ Создание файла XLSX и запись данных в файл XLSX.
    """

    def __init__(self, divs_requests, full_path_to_file):
        self.divs_requests = divs_requests
        self.excel_app = None
        self.wbook = None
        self.full_path_to_file = full_path_to_file

    def file_writer(self):
        """Записываем данные в файл Excel.
        """
        if len(self.divs_requests) == 0:
            l_message(calling_script(), '\n Нет данных для записи в файл! \n', color=BColors.FAIL)
            return

        # self.insert_headers_divs_requests()
        excel_app, wbook = self.create_workbook

        if __debug__ and not PASSED:
            assert excel_app is not None, 'Не удалось подключится к excel'
            assert wbook is not None, 'Не удалось создать книгу'

        try:
            self._write_to_sheet()
            wbook.Close(True, self.full_path_to_file)  # сохраняем изменения и закрываем
            self.excel_app_quit()

        except Exception as err:
            l_message(calling_script(), f" Exception: {repr(err)}", color=BColors.FAIL)
            l_message(calling_script(), 'Не удалось записать данные', color=BColors.FAIL)
            self.excel_app_quit()
            return

    def _write_to_sheet(self):
        """Запись данных на лист.
        """
        l_message(calling_script(), 'Начало записи данных в файл', color=BColors.OKBLUE)
        doc_row: int = 1
        for divs_iter in tqdm(self.divs_requests):  # записываем данные

            if doc_row == 1:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = divs_iter['rowNom']
            else:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = doc_row - 1

            self.wbook.Worksheets.Item(1).Cells(doc_row, 2).Value = divs_iter['ques']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 3).Value = divs_iter['company_cid']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 4).Value = divs_iter['company_link_1']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 5).Value = divs_iter['company_url']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 6).Value = divs_iter['company_title']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 7).Value = divs_iter['company_text']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 8).Value = divs_iter['company_fast_links']

            doc_row += 1

        l_message(calling_script(), 'Данные записаны', color=BColors.OKBLUE)

    def insert_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными.
        """
        return self.divs_requests.insert(0, HEADERS_TAB)

    @property
    def create_workbook(self):
        """ Создание обектов приложения Excel и обьекта страницы.
        """
        try:
            self.excel_app = win32.Dispatch("Excel.Application")
            self.excel_app_start()

            if os.path.exists(self.full_path_to_file):  # файл excel существует то удаляем
                os.remove(self.full_path_to_file)

            self.wbook = self.excel_app.Workbooks.Add()
            self.wbook.SaveAs(self.full_path_to_file)
            l_message(calling_script(), f'Книга создана в {self.full_path_to_file}', color=BColors.OKBLUE)

            self.wbook = self.excel_app.Workbooks.Open(self.full_path_to_file)

        except com_error as err:
            l_message(calling_script(), f" pywintypes.com_error: {repr(err)}", color=BColors.FAIL)

        except TypeError as err:
            l_message(calling_script(), f"  TypeError: {repr(err)}", color=BColors.FAIL)
            try:
                self.wbook.Close(False)  # save the workbook
                self.excel_app_quit()
                l_message(calling_script(), "**** Аварийное завершение программы ****", color=BColors.FAIL)

            except AttributeError as err:
                l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
                quit()

        return self.excel_app, self.wbook

    def excel_app_start(self):
        """ Старт приложения Excel
        """
        self.excel_app.DisplayAlerts = False  # отключаем обновление экрана
        self.excel_app.Visible = False
        self.excel_app.ScreenUpdating = False

    def excel_app_quit(self):
        """Выход из приложения Excel
        """
        self.excel_app.DisplayAlerts = True  # отключаем обновление экрана
        self.excel_app.Visible = True
        self.excel_app.ScreenUpdating = True
        self.excel_app.Quit()


class InfoGetter:
    """Класс с функциями получениями данных из частей распарсенного ответа
    """

    def __init__(self, div):
        self.div = div

    def get_my_company_title(self):
        """Найти и вернуть название компании.
        """
        try:
            my_company_title = self.div.find('div', attrs={
                'class': "OrganicTitle-LinkText organic__url-text"}).text
            l_message(calling_script(), f'my_company_text {my_company_title}', color=BColors.OKBLUE)

        except AttributeError as err:
            l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
            my_company_title: str = 'N/A'

        return my_company_title

    def get_my_company_cid(self):
        """Найти и вернуть порядковый номер компании на странице.
        """
        try:
            my_company_cid: str = str(self.div.get('data-cid'))
            l_message(calling_script(), f'company_cid {my_company_cid}', color=BColors.OKBLUE)

        except AttributeError as err:
            l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
            my_company_cid: str = 'N/A'

        return my_company_cid

    def get_my_company_contact(self):
        """Найти и вернуть контакты компании.
        """
        try:
            my_company_contact: str = self.div.find('span', attrs={
                'class': 'VanillaReact CoveredPhone'})

            if my_company_contact is not None:
                my_company_contact = "".join(c for c in my_company_contact['data-vnl'] if c.isdecimal())

            if my_company_contact is None:
                my_company_contact: str = 'N/A'

            l_message(calling_script(), f'company_contact {my_company_contact}', color=BColors.OKBLUE)

        except AttributeError as err:
            l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
            my_company_contact: str = 'N/A'

        return my_company_contact

    def get_my_company_text(self):
        """Найти и вернуть описание компании.
        """
        try:
            my_company_text = self.div.find('div', attrs={
                'class': "text-container typo typo_text_m typo_line_m organic__text"}).text
            l_message(calling_script(), f'company_text  {my_company_text}', color=BColors.OKBLUE)

        except AttributeError:
            my_company_text: str = self.div.text
            l_message(calling_script(), f'company_text  {my_company_text}', color=BColors.OKBLUE)

        return my_company_text

    def get_my_company_fast_links(self):
        """Найти и вернуть ссылку на сайт компании.
        """
        try:
            company_fast_links: str = self.div.find_all('div', attrs={
                'class': 'Sitelinks-Item sitelinks__item'})

            link_string = ''
            for link in company_fast_links:
                try:
                    link_string = link_string + link.text + " "
                except AttributeError:
                    continue

            l_message(calling_script(), f'company_fast_links  {company_fast_links}', color=BColors.OKBLUE)

            if company_fast_links is None or company_fast_links == []:
                company_fast_links: str = 'N/A'
                return company_fast_links

        except AttributeError as err:
            l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
            company_fast_links: str = 'N/A'
            return company_fast_links

        return link_string

    def get_my_company_link_1(self):
        """Найти и вернуть ссылку на сайт компании.
        """
        try:
            my_company_link_1: str = self.div.find('a', attrs={
                'class': 'Link Link_theme_outer Path-Item link path__item'}).find('b').text

            if my_company_link_1 is None:
                my_company_link_1: str = self.div.find('a', attrs={
                    'class': 'link link_theme_outer path__item click i-bem'}).find('b').text

            if my_company_link_1 is None:
                my_company_link_1: str = 'N/A'

            l_message(calling_script(), f'company_link_1 {my_company_link_1}', color=BColors.OKBLUE)

        except AttributeError:
            try:
                my_company_link_1: str = self.div.find('a', attrs={
                    'class': 'link link_theme_outer path__item i-bem'}).find('b').text

            except AttributeError as err:
                l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
                my_company_link_1: str = 'N/A'


        if my_company_link_1== 'N/A':
            breakpoint()

        return my_company_link_1

    def get_my_company_url(self):
        """Найти и вернуть быструю ссылку на сайт компании.
        """
        try:

            my_company_url: str = self.div.find('a').get('href')

            if my_company_url is None:
                return 'N/A'

            l_message(calling_script(), f'company_link_1 {my_company_url}', color=BColors.OKBLUE)

        except AttributeError as err:
            l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
            my_company_url: str = 'N/A'

        return my_company_url


# ---------------------------------- main class ----------------------------------


class Parser:
    """ Базовый класс парсера с основными функциями
    """

    def __init__(self, path_to_queries: str = None, query=None):

        self.urls = None
        self.queries_path = path_to_queries
        self.query = query
        self.divs_requests: list = []  # список c ответами
        self.result: list = []

        self.headers: list = []
        self.divs = None
        self.ques = None
        self.url = None
        self.request = None
        self.session = None

        self.proxyes: list = []  # создаем список c прокси
        self.full_path_to_file = None
        self.get_proxy_path = None
        self.request_timeout = None

        self.get_soup_name = None
        self.get_soup_class = None
        self.get_soup_attribute = None

        self.proxy_maker = ProxyMaker()

    def start_pars(self, urls: object) -> object:
        """ Определение начало работы в базовом классе.
        """
        assert self.urls is not None, f"{calling_script()} urls not passed"

        self.urls = urls

        for number, item_url in enumerate(self.urls):
            l_message(calling_script(), f"\nЗапрос номер: {number + 1} \n", color=BColors.OKBLUE)

            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                if number <= RESPONSE_LIMIT:
                    self.get_response()
                else:
                    self.get_response_with_proxy()

                self.soup_request()  # обработка ответа сервера

                if self.divs is not None:
                    self.divs_text_shelves()
                    self.result.extend(list(self.divs_requests))
                self._time_rand(2, 4)

            except ConnectionError as err:
                l_message(calling_script(), f" ConnectionError: {repr(err)}", color=BColors.FAIL)
                continue

        self.write_data_to_file()

    def write_data_to_file(self):
        """ Запись в файл excel.
        """
        raise NotImplementedError(f'Определите {calling_script()} в {self.__class__.__name__}')

    def divs_text_shelves(self):
        """ Поиск данных в ответе сервера.
        """
        raise NotImplementedError(f'Определите {calling_script()} в {self.__class__.__name__}')

    def get_session(self):
        """ Создание сессии.
        """
        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        self.session = requests.Session()  # устанавливаем сессию
        self.session.mount(str(self.url), adapter_yd)

        return self.session

    def close_session(self):
        """ Закрываем сессию.
        """
        return self.session.close()

    def get_response(self):
        """ Функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку.
        """
        for header in self.headers:
            try:
                self.session = self.get_session()
                self.request: Response = self.session.get(self.url, headers=header, stream=True,
                                                          timeout=self.request_timeout)
                if self.check_request_status_code(self.request):
                    l_message(calling_script(), f'Успешный запрос!', color=BColors.OKBLUE)
                    self.close_session()
                    return self.request
                else:
                    l_message(calling_script(), 'Ошибка при установке соединения! проверьте HEADERS!',
                              color=BColors.FAIL)
                    continue

            except Exception as err:
                l_message(calling_script(), f"Exception: {repr(err)}", color=BColors.FAIL)

    def get_response_with_proxy(self):
        """ Функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку.
        """
        time_start = None

        self.proxyes = self.get_proxy_pool_from_file()

        if not self.proxyes:
            self.proxy_maker.run()
            self.proxyes = self.get_proxy_pool_from_file()

        assert self.proxyes is not None, "proxyes not set"

        data_requests = self._create_data_request()

        for request_number, item_request in enumerate(list(data_requests)):

            if request_number >= RESPONSE_LIMIT:
                return

            for item_data in list(item_request):
                l_message(calling_script(), f"proxy {item_data['proxy']}", color=BColors.OKGREEN)
                try:
                    time_start = monotonic()
                    session = self.get_session()
                    self.request: Response = session.get(self.url,
                                                         headers=item_data['headers'],
                                                         stream=item_data['stream'],
                                                         timeout=item_data['TIMEOUT'],
                                                         proxies=item_data['proxy'])
                    self._measure_time_request(str(calling_script()), time_start)

                    if self.check_request_status_code(self.request):
                        return self.request
                    else:
                        l_message(calling_script(), 'Ошибка при установке соединения! проверьте HEADERS!',
                                  color=BColors.FAIL)
                        continue

                except ConnectTimeout as err:
                    l_message(calling_script(), f"ConnectTimeout: {repr(err)}", color=BColors.FAIL)
                    l_message(calling_script(), "Connection to proxy timed out", color=BColors.FAIL)
                    self._measure_time_request(str(calling_script()), time_start)
                    continue

                except ProxyError as err:
                    l_message(calling_script(), f"ProxyError: {repr(err)}", color=BColors.FAIL)
                    l_message(calling_script(), f"Удалите прокси из списка: {repr(err)}", color=BColors.FAIL)

    @staticmethod
    def _measure_time_request(function: str, t_start):
        """ Исмерение времени выполнения запросаю
        """
        micro_seconds = (monotonic() - t_start) * 1000
        l_message(function,
                  f'Время request: {micro_seconds:2.2f} ms или {str(float(round(micro_seconds / 1000, 2)))} сек.',
                  color=BColors.OKGREEN)

    def _create_data_request(self):
        """ Создание списка данных для запроса через session.get.
        """
        data_request: list = []
        for header in self.headers:
            for proxy in self.proxyes:
                if proxy == "":
                    continue
                data_request.append({"headers": header,
                                     "proxy": {'http': proxy, 'https': proxy},
                                     "timeout": self.request_timeout * 2,
                                     "stream": True
                                     })
        yield data_request

    def check_request_status_code(self, request) -> bool:
        """ Проверка кода ответа запроса.
        """
        if request.status_code == 200:  # если запрос был выполнен успешно то
            l_message(calling_script(), 'Успешный запрос!', color=BColors.OKBLUE)
            return True

        elif request.status_code == 400:
            l_message(calling_script(), f'BAD request {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 401 < request.status_code < 500:
            l_message(calling_script(), f'Client Error {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 500 <= request.status_code < 600:
            l_message(calling_script(), f'Server Error {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        else:
            l_message(calling_script(),
                      f'Неудачный запрос! Ответ {str(request.status_code)} : {str(request.status_code)}',
                      color=BColors.FAIL)
            return False

    def soup_request(self):
        """ Обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves.
        """
        if not hasattr(self.request, self.get_soup_attribute):
            l_message(calling_script(), 'Ответ не содержит текст :(', color=BColors.FAIL)
            return

        if self.request.text == '':
            l_message(calling_script(), 'Ответ не содержит текстовых данных :(', color=BColors.FAIL)
            return

        soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
        self.divs = soup.find_all(class_=self.get_soup_class)  # данные ответа

        if self.divs is None or len(self.divs) == 0:
            l_message(calling_script(), 'Ответ не содержит нужных данных :(', color=BColors.FAIL)
            return

        l_message(calling_script(), f'Всего найдено блоков {str(len(self.divs))}', color=BColors.OKBLUE)

    @staticmethod
    def _time_rand(t_start: int = 1, t_stop: int = 30):
        """ Функция задержки выполнения кода на рандомный промежутокю
        """
        time_random = randint(t_start, t_stop)
        l_message(calling_script(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec',
                  color=BColors.OKBLUE)

        for _ in range(time_random):
            sleep(uniform(0.8, 1.2))

    @staticmethod
    def create_patch(*, path=None):
        """ Создание папки по пути.
        """
        os.makedirs(path)
        l_message(calling_script(), f'Файл создан в {path}', color=BColors.OKBLUE)

    @staticmethod
    def check_folder(*, path: str) -> bool:
        """ Проверка файл или каталог.
        """
        if not os.path.exists(path):
            l_message(calling_script(), 'Файл не найден', color=BColors.OKBLUE)
            return False
        return True

    def check_and_remove_file(self):
        """ Проверка существования файла. Если файла существует - удаляем.
        """
        if os.path.exists(self.full_path_to_file):  # файл excel существует то удаляем
            os.remove(self.full_path_to_file)

    @staticmethod
    def date_today():
        """ Возвращаем текущую дату.
        """
        return datetime.today().strftime("%d.%m.%Y")

    @staticmethod
    def check_ip():
        """Check my public IP via tor.
        """
        try:
            l_message(calling_script(), f'My public IP {requests.get("http://www.icanha4zip.com").text[:-2]}',
                      color=BColors.OKBLUE)
        except requests.exceptions.ConnectionError:
            l_message(calling_script(), 'не удалось проверить IP',
                      color=BColors.OKBLUE)

    def get_proxy_pool_from_file(self):
        """Создаём пул прокси.
        """
        try:
            with open(self.get_proxy_path, 'r', encoding='utf-8') as file:
                return [x.strip() for x in file if x != ""]
        except FileNotFoundError as err:
            l_message(calling_script(), f"FileNotFoundError: {repr(err)}", color=BColors.FAIL)
            return []

    def _load_proxies_list(self):
        """ Добавляем проверенные прокси в proxies_list.
        """
        try:
            with open(PROXIES_LIST, 'r') as file:
                self.proxyes: list = file.read().split('\n')

        except FileNotFoundError as err:
            l_message(calling_script(), f"FileNotFoundError: {repr(err)}", color=BColors.FAIL)
            self.proxyes = []


# ---------------------------------- Parser class ----------------------------------


class ParserYandex(Parser):
    """ Класс парсера Яндекса наследуется от базового парсера.
    """
    headers: List[Dict[str, str]]
    full_path_to_file: str
    FULL_PATH: str
    PROXY_PATH: str
    request_timeout: float
    SOUP_NAME: str
    SOUP_CLASS: str
    SOUP_ATTRIBUTE: str

    def __init__(self, ):
        super(ParserYandex, self).__init__(self)

        self.headers = [HEADERS_TEST, KAD_HEAD]
        self.full_path_to_file = FULL_PATH
        self.get_proxy_path = PROXY_PATH
        self.request_timeout = REQUEST_TIMEOUT

        self.get_full_path = FULL_PATH + PARSER_NAME + ' ' + self.date_today() + EXTENSION

        self.get_soup_name = SOUP_NAME
        self.get_soup_class = SOUP_CLASS
        self.get_soup_attribute = SOUP_ATTRIBUTE

    def start_pars(self, urls):
        """ функция парсера.
        """
        assert urls is not None, str(calling_script()) + 'urls not passed'

        self.urls = urls

        for response_number, item_url in enumerate(self.urls):
            l_message(calling_script(), f"\nЗапрос номер: {response_number + 1} \n", color=BColors.OKBLUE)

            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                if response_number <= RESPONSE_LIMIT:
                    self.get_response()
                else:
                    self.get_response_with_proxy()

                self.soup_request()  # обработка ответа сервера

                if self.divs is not None:
                    self.divs_text_shelves()
                    self.result.extend(list(self.divs_requests))
                self._time_rand(2, 4)

            except ConnectionError as err:
                l_message(calling_script(), f" ConnectionError: {repr(err)}", color=BColors.FAIL)
                continue

        self.write_data_to_file()

    def start_pars_with_selenium(self, urls):
        """ Функция парсера.
        """
        assert urls is not None, str(calling_script()) + 'urls not passed'

        for response_number, item_url in enumerate(self.urls):
            l_message(calling_script(), f"\nЗапрос номер: {response_number + 1} \n", color=BColors.OKBLUE)

            try:
                self.divs_text_shelves()
                self.result.extend(list(self.divs_requests))

            except ConnectionError as err:
                l_message(calling_script(), f" ConnectionError: {repr(err)}", color=BColors.FAIL)
                continue

        self.write_data_to_file()

    def divs_text_shelves(self):
        """ Поиск данных в ответе сайта.
        """

        i_row: int = 1
        for div in tqdm(self.divs):

            info = InfoGetter(div)
            my_company_title: str = info.get_my_company_title()
            my_company_cid: str = info.get_my_company_cid()
            my_company_link_1: str = info.get_my_company_link_1()
            my_company_site_fast_links: str = info.get_my_company_fast_links()
            my_company_text: str = info.get_my_company_text()
            my_company_contact: str = info.get_my_company_contact()
            my_company_url: str = info.get_my_company_url()

            if my_company_title == 'N/A' and \
                    my_company_link_1 == 'N/A' and \
                    my_company_text == 'N/A':
                return

            self.divs_requests.append(
                {'rowNom': i_row,
                 'ques': self.ques,
                 'company_cid': my_company_cid,
                 'company_link_1': my_company_link_1,
                 'company_url': my_company_url,
                 'company_title': my_company_title,
                 'company_text': my_company_text,
                 'company_fast_links': my_company_site_fast_links,
                 'company_contact': my_company_contact,
                 }
            )
            i_row = i_row + 1

            if WRITE_TO_JSON:
                write_json_file(data=self.divs_requests, name=PARSER_NAME + "_divs")

    def _insert_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными.
        """
        return self.divs_requests.insert(0, HEADERS_TAB)

    def write_data_to_file(self, readjsonfile=False):
        """ Запись данных в файл .XLSX
        """
        if readjsonfile:
            self.divs_requests = read_json_file(PARSER_NAME + "_divs")

        self._insert_headers_divs_requests()

        self._recording_with_pandas()

        self._recording_with_pypiwin32()

    def _recording_with_pandas(self):
        try:
            df = pd.DataFrame(self.divs_requests)
            df.to_excel(f'./DataFrame {PARSER_NAME} {self.date_today()}.xlsx',
                        index=False,
                        header=False)
            l_message(calling_script(), f'данные успешно записаны из DataFrame '
                                        f'в файл DataFrame {PARSER_NAME} {self.date_today()}.xlsx',
                      color=BColors.OKBLUE)
        except Exception as err:
            l_message(calling_script(), f" Exception: {repr(err)}", color=BColors.FAIL)

    def _recording_with_pypiwin32(self):
        file_writer = WriterToXLSX(self.divs_requests, self.get_full_path)
        file_writer.file_writer()


class ParserYandexWithSelenium(Parser):
    """ Класс парсера Яндекса наследуется от базового парсера.
    """

    def __init__(self, ):
        super(ParserYandexWithSelenium, self).__init__(self)

        self.divs = None
        self.content = None
        self.get_full_path = FULL_PATH + PARSER_NAME + ' ' + self.date_today() + EXTENSION
        self.fold_path = "\\page"
        self.selenium_divs = []
        self.soup_attribute = SOUP_ATTRIBUTE

    def _insert_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными.
        """
        return self.divs_requests.insert(0, HEADERS_TAB)

    def write_data_to_file(self, readjsonfile=False):
        """ Запись данных в файл .XLSX
        """
        if readjsonfile:
            self.divs_requests = read_json_file(PARSER_NAME + "_divs")

        self._insert_headers_divs_requests()

        self._recording_with_pandas()

        self._recording_with_pypiwin32()

    def _recording_with_pandas(self):
        try:
            df = pd.DataFrame(self.divs_requests)
            df.to_excel(f'./DataFrame {PARSER_NAME} {self.date_today()}.xlsx',
                        index=False,
                        header=False)
            l_message(calling_script(), f'данные успешно записаны из DataFrame '
                                        f'в файл DataFrame {PARSER_NAME} {self.date_today()}.xlsx',
                      color=BColors.OKBLUE)
        except Exception as err:
            l_message(calling_script(), f" Exception: {repr(err)}", color=BColors.FAIL)

    def _recording_with_pypiwin32(self):
        file_writer = WriterToXLSX(self.divs_requests, self.get_full_path)
        file_writer.file_writer()

    @staticmethod
    def get_content_with_selenium(urls):
        """Загрузка страницы целеком с помощью selenium
        """
        web_driver = Webdriver(proxy='')
        web_driver.create()

        for number, url in enumerate(urls):
            web_driver.get_content(number, url)
            sleep(5)

        web_driver.close_and_quit()

    def divs_text_shelves(self):
        """ Поиск данных в ответе сайта.
        """
        i_row: int = 1
        for div in tqdm(self.divs):

            info = InfoGetter(div)
            my_company_title: str = info.get_my_company_title()
            my_company_cid: str = info.get_my_company_cid()
            my_company_link_1: str = info.get_my_company_link_1()
            my_company_site_fast_links: str = info.get_my_company_fast_links()
            my_company_text: str = info.get_my_company_text()
            my_company_contact: str = info.get_my_company_contact()
            my_company_url: str = info.get_my_company_url()

            if my_company_title == 'N/A' and \
                    my_company_cid == 'N/A' and \
                    my_company_link_1 == 'N/A' and \
                    my_company_site_fast_links == 'N/A' and \
                    my_company_text == 'N/A' and \
                    my_company_contact == 'N/A' and \
                    my_company_url == 'N/A':
                return

            self.divs_requests.append(
                {'rowNom': i_row,
                 'ques': self.ques,
                 'company_cid': my_company_cid,
                 'company_link_1': my_company_link_1,
                 'company_url': my_company_url,
                 'company_title': my_company_title,
                 'company_text': my_company_text,
                 'company_fast_links': my_company_site_fast_links,
                 'company_contact': my_company_contact,
                 }
            )
            i_row = i_row + 1

    def get_content_from_file(self, content_file):
        """Получение данных из файйла .html
        :param content_file:
        :return:
        """
        with open(CURRENT_DIR + self.fold_path + "\\" + content_file, encoding='utf-8') as file:
            self.content = file.read()
        return self.content

    def get_selenium_divs(self) -> object:
        """Поиск файлов в папке fold_path
        """
        for filename in listdir(CURRENT_DIR + self.fold_path):
            self.selenium_divs.append(filename)

    def soup_request(self):
        """ Обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves.
        """

        soup = BeautifulSoup(self.content, 'lxml')  # ответ
        self.divs = soup.find_all(class_=self.get_soup_class)  # данные ответа

        if self.divs is None or len(self.divs) == 0:
            l_message(calling_script(), 'Ответ не содержит нужных данных :(', color=BColors.FAIL)
            return

        l_message(calling_script(), f'Всего найдено блоков {str(len(self.divs))}', color=BColors.OKBLUE)

    def start_pars(self, **kvargs):
        """ функция парсера.
        """
        self.get_selenium_divs()

        assert self.selenium_divs is not None, str(calling_script()) + 'divs is None'

        for divs_number, item_divs in enumerate(self.selenium_divs):
            l_message(calling_script(), f"\nСтраница номер: {divs_number + 1} \n", color=BColors.OKBLUE)

            self.get_content_from_file(content_file=item_divs)

            self.soup_request()
            self.divs_text_shelves()
            self.result.extend(list(self.divs_requests))

        self.write_data_to_file()


# ---------------------------------- Webdriver class ----------------------------------


class Webdriver:
    """ Класс webdriver - основной движок для получения данных сайта
    """

    def __init__(self, proxy=''):
        self.proxy = proxy
        self.chrome_driver = None
        self.options = None
        self.content = None

    def create(self):
        """Создание webdriver с опциями
        """
        self.options = self.create_options()
        self.chrome_driver = self.create_webdriver()
        l_message(calling_script(), 'webdriver create', color=BColors.OKBLUE)

    def set_config(self) -> None:
        """ Установление дополнительных опций работы webdriver
        """
        # set timeout to find an element in seconds
        self.chrome_driver.implicitly_wait(5 * BROWSER_SPEED)

        # set page load timeout in seconds
        self.chrome_driver.set_page_load_timeout(15 + BROWSER_SPEED)

    def create_options(self):
        """ Создание опция для webdriver
        """
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("window-size=1366,768")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("no-sandbox")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument("headless")
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument(f"user-agent={AGENTS}")

        if self.proxy != "":
            self.options.add_argument(f"proxy-server={self.proxy}")

        return self.options

    def create_webdriver(self):
        """Создание webdriver
        """
        return webdriver.Chrome(ChromeDriverManager().install(), options=self.options)

    @staticmethod
    def create_folder():
        """Создание папки для сохранеиения загруженных страниц
        """
        if not os.path.exists('page'):
            os.mkdir('page')

    def close_and_quit(self):
        """ Закрытие и уничтожение экземпляра webdriver
        """
        self.chrome_driver.close()
        self.chrome_driver.quit()

    def write_content(self, number):
        """Запись содержимого страницы
        :param number:
        """
        self.create_folder()

        file = 'page/' + str(number) + "_index_page.html"

        with open(file=file, mode="w", encoding="utf-8") as source_file:
            source_file.write(self.content)

        l_message(calling_script(), f'content write in {file}',
                  color=BColors.OKBLUE)

    def get_content(self, number, url):
        """Получение контекта загруженной страницы
        """
        try:
            self.chrome_driver.get(url=url['url'])
            l_message(calling_script(), f"content get", color=BColors.OKBLUE)
            self.set_config()

            self.content = self.chrome_driver.page_source

            self.write_content(number)

        except Exception as err:
            l_message(calling_script(), f" Exception: {repr(err)}", color=BColors.FAIL)
            self.close_and_quit()


# ---------------------------------- constructor url ----------------------------------

def url_constructor_yandex():
    """ Формирование запросов из запчастей.
    """
    queries_path = QUERIES_PATH
    selected_base_url = BASE_URL_YANDEX
    selected_region = REGION_YANDEX
    within_time = WITHIN_TIME
    num_doc = NUM_DOC
    max_pos = URL_MAX_POS_YANDEX

    urls = []
    # открываем файл с ключами по пути path_to_queries и считываем ключи
    with open(queries_path, 'r', encoding='utf-8') as file:
        query = [x.strip() for x in file if x != '']

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        if num_doc == 10:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru'
        else:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru' + '&num_doc=' + str(num_doc)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                l_message(calling_script(), mod_url, color=BColors.OKBLUE)
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем
            else:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    l_message(calling_script(), url, color=BColors.OKBLUE)
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
    return urls


PROXIES_LIST: str = str(CURRENT_DIR) + r'\proxyeslist.txt'
PROXIES: str = str(CURRENT_DIR) + r'\proxies.txt'


class ProxyMaker:

    def __init__(self):
        self.limit = 25
        self.timeout = TIMEOUT
        self.max_proxies = MAX_PROXYES
        self.max_run = 5
        self.proxyes: list = []
        self.valid_proxies_list: list = []

    @staticmethod
    async def _save_proxies(proxies, filename: str):
        """ Сохраняем прокси от Broker в файл PROXIES
            :param proxies: найденный Broker прокси: object
            :param filename: полный путь к файлу для записи и хранения прокси: str
        """
        l_message(calling_script(), f'proxyes {proxies}', color=BColors.OKBLUE)
        with open(filename, 'w') as file:
            while True:
                proxy = await proxies.get()
                if proxy is None:
                    break
                proto = 'https' if 'HTTPS' in proxy.types else 'http'
                row = f'{proto}://{proxy.host}:{proxy.port}\n'
                file.write(row)

    def _get_proxies(self):
        """ Собираем прокси с помощью proxybroker
            :return: proxies_list_get : список найденных прокси: list
        """
        loop = asyncio.get_event_loop()

        proxies = asyncio.Queue()
        broker = Broker(proxies, timeout=12, max_conn=200, max_tries=2, verify_ssl=False, loop=loop)
        tasks = asyncio.gather(
            broker.grab(countries=['RU'], limit=self.limit), self._save_proxies(proxies, filename=PROXIES)
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)

        # записываем собранное в proxies_list_get
        with open(PROXIES, 'r') as prx_row:
            proxies_list_get = prx_row.read().split('\n')

        l_message(calling_script(), f'proxies_list_get {str(proxies_list_get)}', color=BColors.OKBLUE)
        return proxies_list_get

    def _check_proxies(self, proxies_list: list):
        """ Проверяем список прокси
            :return: valid_proxies_list: возвращает список проверенных прокси: list
            :param proxies_list: лист с прокси для проверки : list
        """
        l_message(calling_script(), f'proxies_list {str(proxies_list)}', color=BColors.OKBLUE)
        mgr = multiprocessing.Manager()
        valid_proxies_list: list = mgr.list()

        if len(proxies_list) < 4:
            n_chunks = len(proxies_list)
        else:
            n_chunks: int = 4

        chunks = [proxies_list[i::n_chunks] for i in range(n_chunks)]

        parcs_list: list = []
        for chunk in chunks:
            chunk_p = multiprocessing.Process(target=self._check_proxy, args=(chunk, valid_proxies_list))
            parcs_list.append(chunk_p)
            chunk_p.start()

        for chunk_p in parcs_list:
            chunk_p.join()

        l_message(calling_script(), f'valid_proxies_list {str(valid_proxies_list)}', color=BColors.OKBLUE)

        return valid_proxies_list

    def _check_proxy(self, proxies_for_check, valid_proxies):
        """ Проверяем каждый прокси
            :param proxies_for_check: список прокси для проверки прокси : list
            :param valid_proxies: список валидных прокси : list
        """
        session: Session = requests.Session()

        for nu_proxy in proxies_for_check:
            l_message(calling_script(), f'nu_proxy {str(nu_proxy)}', color=BColors.OKBLUE)
            try:
                # time_rand(2, 3)  # задержка исполнеия
                request = session.get(HOST, headers=HEADERS_TEST, proxies={'http': nu_proxy, 'https': nu_proxy},
                                      timeout=self.timeout)
                l_message(calling_script(), f'request.status_code {str(request.status_code)}', color=BColors.OKBLUE)

                if self._check_request_status_code(request=request, url=nu_proxy):
                    valid_proxies.append(nu_proxy)
                    l_message(calling_script(),
                              f"valid_proxies {str(nu_proxy)} : {str(request.headers['Content-Type'])}",
                              color=BColors.OKBLUE)
                    session.close()
                    return valid_proxies
                else:
                    session.close()

            except ProxyError as err:
                l_message(calling_script(), f"ProxyError: {repr(err)}", color=BColors.FAIL)
                session.close()

            except ConnectTimeout as err:
                l_message(calling_script(), f"ConnectTimeout: {repr(err)}", color=BColors.FAIL)
                session.close()

            except AttributeError as err:
                l_message(calling_script(), f"AttributeError: {repr(err)}", color=BColors.FAIL)
                session.close()

            except Exception as err:
                l_message(calling_script(), f"Exception: {repr(err)}", color=BColors.FAIL)
                session.close()

    @staticmethod
    def _check_request_status_code(request, url) -> bool:
        """ Проверка кода ответа запроса.
        """
        if request.status_code == 200:  # если запрос был выполнен успешно то
            l_message(calling_script(), 'Успешный запрос!', color=BColors.OKBLUE)
            return True

        elif request.status_code == 400:
            l_message(calling_script(), f'BAD request {url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 400 < request.status_code < 500:
            l_message(calling_script(), f'Client Error {url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 500 <= request.status_code < 600:
            l_message(calling_script(), f'Server Error {url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        else:
            l_message(calling_script(),
                      f'Неудачный запрос! Ответ {str(request.status_code)} : {str(request.status_code)}',
                      color=BColors.FAIL)
            return False

    @staticmethod
    def _write_proxies_list(get_proxy: list):
        """ Добавляем проверенные прокси в proxies_list.
            :param get_proxy: добаляет список get_proxy в файл PROXIES_LIST: list
        """
        try:
            with open(PROXIES_LIST, 'w') as file:
                for item in get_proxy:
                    file.write(f"{item}\n")

        except FileNotFoundError as err:
            l_message(calling_script(), f"FileNotFoundError: {repr(err)}", color=BColors.FAIL)

        except TypeError as err:
            l_message(calling_script(), f"TypeError: {repr(err)}", color=BColors.FAIL)

    @staticmethod
    def _app_load_proxies_list(get_proxy: list):
        """ Добавляем проверенные прокси в proxies_list.
            :param get_proxy: добаляет список get_proxy в файл PROXIES_LIST: list
        """
        try:
            # добавляем прокси к уже проверенным
            with open(PROXIES_LIST, 'r') as file:
                proxies_list: list = file.read().split('\n')

        except Exception as err:
            l_message(calling_script(), f"FileNotFoundError: {repr(err)}", color=BColors.FAIL)
            # если файл пустой - обнуляем список
            proxies_list = []

        if proxies_list:
            get_proxy.extend(proxies_list)
        # преобразуев множество чтобы удалить повторы и обратно в list
        get_proxy = list(set(get_proxy))
        l_message(calling_script(), f"{str(get_proxy)}", color=BColors.OKBLUE)

        get_proxy = [x for x in get_proxy if x != ""]

        with open(PROXIES_LIST, 'w') as file:
            file.write('\n'.join(get_proxy))

    @staticmethod
    def _clear_empty_proxy(list_proxy):
        return [x for x in list_proxy if x != ""]

    def _load_proxies_list(self):
        """ Добавляем проверенные прокси в proxies_list.
        """
        try:
            with open(PROXIES_LIST, 'r') as file:
                self.proxyes: list = file.read().split('\n')
                self.proxyes = self._clear_empty_proxy(self.proxyes)

        except FileNotFoundError as err:
            l_message(calling_script(), f"FileNotFoundError: {repr(err)}", color=BColors.FAIL)
            self.proxyes = []

    def _check_proxies_before_run(self):

        self._load_proxies_list()
        if self.proxyes != ['']:
            self.valid_proxies_list = self._check_proxies(proxies_list=self.proxyes)
            self.valid_proxies_list = self._clear_empty_proxy(self.valid_proxies_list)

        if not self.valid_proxies_list:
            os.remove(PROXIES_LIST)

        self._write_proxies_list(self.valid_proxies_list)

        self.proxyes = self.valid_proxies_list

    def run(self):
        """ Основная функция
        """
        l_message(calling_script(), '\n**** Start ****\n', color=BColors.OKBLUE)

        self._check_proxies_before_run()

        while not len(self.proxyes) >= self.max_run * MAX_PROCESS:
            proxies_list = self._get_proxies()
            proxy = self._check_proxies(proxies_list)
            self._app_load_proxies_list(proxy)
            self.proxyes = self._clear_empty_proxy(self.proxyes)
            self._load_proxies_list()
            # self._time_rand(10, 15)

        l_message(calling_script(), '\n**** Done ****\n', color=BColors.OKBLUE)

    @staticmethod
    def _time_rand(t_start, t_stop):
        """ Функция задержки выполнения кода на рандомный промежуток.
        """
        time_random = randint(t_start, t_stop)
        l_message(calling_script(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec',
                  color=BColors.OKBLUE)

        for _ in range(time_random):
            time.sleep(uniform(0.8, 1.2))


#  парсинг с использованием SELENIUM
PARSE_WITH_SELENIUM = False

# Если надо остановить процесс а потом записать всё что насобиралось
# то меняем WRITE_DATA_FROM_FILE  с False на  True
# тогда записываются все собранные данные
# *  не забываем вернуть обратно
WRITE_DATA_FROM_FILE = True


def main():
    """Основная функция с параметрами.
    """
    l_message(calling_script(), '\n**** Start ****\n', color=BColors.OKBLUE)

    if WRITE_DATA_FROM_FILE:
        l_message(calling_script(), 'Выбрана запись из файла .json', color=BColors.OKBLUE)
        parser = ParserYandex()
        parser.write_data_to_file(readjsonfile=True)
        l_message(calling_script(), '\n**** Done ****\n', color=BColors.OKBLUE)
        return

    urls = url_constructor_yandex()

    if PARSE_WITH_SELENIUM:
        l_message(calling_script(), 'Выбрано ParserYandexWithSelenium', color=BColors.OKBLUE)
        parser_selenium = ParserYandexWithSelenium()
        parser_selenium.get_content_with_selenium(urls=urls)
        parser_selenium.start_pars()

    parser = ParserYandex()
    parser.start_pars(urls=urls)

    l_message(calling_script(), '\n**** Done ****\n', color=BColors.OKBLUE)


if __name__ == '__main__':
    # ProxyMaker().run()
    main()
