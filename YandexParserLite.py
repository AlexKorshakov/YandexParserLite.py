""" Парсер яндекса.
"""

""" Перед началом работ необходимо выполнить команду pip3 install -r requirements.txt при наличии файла requirements.txt """
import inspect
import os
from subprocess import call


def _read_requirements(relpath):
    fullpath = os.path.join(os.path.dirname(__file__), relpath)
    with open(fullpath) as file:
        return [s.strip() for s in file.readlines()
                if (s.strip() and not s.startswith("#"))]


_REQUIREMENTS_TXT = _read_requirements("requirements.txt")
INSTALL_REQUIRES = [line for line in _REQUIREMENTS_TXT if "://" not in line]


def prepare_venv():
    app_venv_name = "venv"
    if not os.path.exists(app_venv_name):
        os.mkdir(f" {app_venv_name}")
    # upgrade pip
    call(['pip', 'install', '--upgrade'])
    # update requirements.txt and upgrade venv
    call(['pip', 'install', '--upgrade'] + INSTALL_REQUIRES)


prepare_venv()

import traceback
from datetime import datetime
from random import choice, randint, uniform
from time import sleep, monotonic

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
except ImportError:
    raise ImportError('для установки этой библиотеки введите команду pip install requests в терминале')

from tqdm import tqdm

try:
    with open(f'{"requirements.txt"}', 'r') as f:
        requirements = f.read()
except FileNotFoundError:
    assert False, 'Проверьте, что добавили файл requirements.txt'

assert 'beautifulsoup4' in requirements, 'Проверьте, что beautifulsoup4 в файл requirements.txt'
assert 'lxml' in requirements, 'Проверьте, что lxml в файл requirements.txt'
assert 'pypiwin32' in requirements, 'Проверьте, что pypiwin32 в файл requirements.txt'
assert 'certifi' in requirements, 'Проверьте, что certifi в файл requirements.txt'
assert 'urllib3' in requirements, 'Проверьте, что urllib3 в файл requirements.txt'
assert 'soupsieve' in requirements, 'Проверьте, что soupsieve в файл requirements.txt'

PASSED = False

__date__ = '17.03.2021'
PARSER_NAME: str = 'ParserYandexSimplified'
print(f'Invoking __init__.py for {__name__}')

TIMEOUT = 180
MAX_PROXYES = 25  # максимальное кооличество прокси
REQUEST_TIMEOUT = 10.24
print(f'Invoking __init__.py for {__name__}')

HOST: str = 'https://yandex.ru'

AGENTS = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0']
# 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
# 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)']

kad_head = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': HOST,
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': choice(AGENTS)}

HEADERS = {'Accept': '*/*',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'host': HOST,
           'User-Agent': choice(AGENTS)}

HEADERS_TEST = {'Accept': '*/*',
                'User-Agent': choice(AGENTS)}

headers_tab = {'rowNom': 'п\п',  # i_row
               'ques': 'Ключ',  # url_ques
               'company_title': 'Заголовок',  # my_company_title
               'company_cid': 'Позиция',  # my_company_cid
               'company_link_1': 'Домен',  # my_company_link_1
               'company_sitelinks': 'Быстрая',  # my_company_site_links
               'company_text': 'Текст',  # my_company_text
               'company_contact': 'Контакты'}

current_dir = str(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# базовый запрос
base_url_yandex: str = 'https://www.yandex.ru/search/ads?text='

date_today = datetime.today().strftime("%d.%m.%Y")
full_path = current_dir + '\\'
extension = '.xlsx'

# задаём полный путь к файлу с выгрузкой
report_name = '/Parser_Yandex.xlsx'

# задаём полный путь к файлу с ключами
queries_path = 'queries.txt'

proxy_path = 'proxieslist.txt'

# задаём максимальное кооличество запросов
url_max_pos_yandex = 2

# Задаём регион. Санкт-Петербург – 2. Краснодар  - 35
# Список идентификаторов российских регионов https://tech.yandex.ru/xml/doc/dg/reference/regions-docpage/
region_yandex = 35
region_google = '+' + 'Краснодар'

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
within_time = 5

# колличество ссылок в каждой выдаче
num_doc = 10  # не рекомендуется менять от слова совсем
# – определяет количество документов (ссылок), отображаемых на одной странице результатов выдачи.
#  по умолчанию = 10
# колличество одновременных процессов / потоков
max_process = 1

# параметры парсинга ответов

soup_name = 'li'
soup_class = 'serp-item'
soup_attribute = 'text'

print(f'Invoking __init__.py for {__name__}')

VIS_LOG = True  # True -  Отображение хода процесса в консоли
PRINT_LOG = True  # True -  Запись лога в файл

config = {'get_main_interval': 6,
          'get_reConnect_interval': 5,  # Time (seconds). Recommended value: 5
          'colors': True,  # True/False. True prints colorful msgs in console
          }

NOW = str(datetime.now().strftime("%d.%m.%Y %H.%M.%S")) + " :: "


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
    if config['colors']:
        msg_string = color + msg + BColors.ENDC
    return msg_string


def write_to_console(*, param_name: str = None, p_value=None):
    """ Запись в консоль.
    """
    try:
        if param_name == 'NLine':
            print('=' * 100)

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
    try:
        with open(d_path + r'_Log.txt', 'a', encoding='utf-8') as file:
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


class WriterToXLSX:
    """ Создание файла XLSX и запись данных в файл XLSX.
    """

    def __init__(self, divs_requests, full_path_to_file):
        self.divs_requests = divs_requests
        self.excel_app = None
        self.wbook = None
        self.full_path_to_file = full_path_to_file

    def file_writer(self):
        """Записываем данные в файл Excel."""

        if len(self.divs_requests) == 0:
            l_message(calling_script(), '\n Нет данных для записи в файл! \n', color=BColors.FAIL)
            return

        self.insert_headers_divs_requests()
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
        """Запись данных на лист."""

        l_message(calling_script(), 'Начало записи данных в файл', color=BColors.OKBLUE)
        doc_row: int = 1
        for divs_iter in self.divs_requests:  # записываем данные

            if doc_row == 1:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = divs_iter['rowNom']
            else:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = doc_row - 1
            self.wbook.Worksheets.Item(1).Cells(doc_row, 2).Value = divs_iter['ques']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 3).Value = divs_iter['company_title']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 4).Value = divs_iter['company_cid']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 5).Value = divs_iter['company_link_1']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 7).Value = divs_iter['company_text']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 8).Value = divs_iter['company_contact']
            doc_row += 1
        l_message(calling_script(), 'Данные записаны', color=BColors.OKBLUE)

    def insert_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными."""

        return self.divs_requests.insert(0, headers_tab)

    @property
    def create_workbook(self):
        """ Создание обектов приложения Excel и обьекта страницы."""

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
        """ Старт приложения Excel"""

        self.excel_app.DisplayAlerts = False  # отключаем обновление экрана
        self.excel_app.Visible = False
        self.excel_app.ScreenUpdating = False

    def excel_app_quit(self):
        """Выход из приложения Excel"""

        self.excel_app.DisplayAlerts = True  # отключаем обновление экрана
        self.excel_app.Visible = True
        self.excel_app.ScreenUpdating = True
        self.excel_app.Quit()


def get_my_company_title(div):
    """Найти и вернуть название компании.
    """
    try:
        my_company_title: str = div.find('h2', attrs={
            'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text.strip()
        l_message(calling_script(), f'company_title {my_company_title}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_title: str = 'N/A'

    return my_company_title


def get_my_company_cid(div):
    """Найти и вернуть порядковый номер компании на странице.
    """
    try:
        my_company_cid: str = str(div.get('data-cid'))
        l_message(calling_script(), f'company_cid {my_company_cid}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_cid: str = ''

    return my_company_cid


def get_my_company_contact(div):
    """Найти и вернуть контакты компании.
    """
    try:
        my_company_contact: str = div.find('div', attrs={
            'class': 'serp-meta__item'}).text.strip()

        text: int = my_company_contact.rfind('+')
        if text > 0:
            my_company_contact = my_company_contact[text:]

        l_message(calling_script(), f'company_contact {my_company_contact}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_contact: str = 'N/A'

    return my_company_contact


def get_my_company_text(div):
    """Найти и вернуть описание компании.
    """
    try:
        my_company_text: str = div.find('div', attrs={
            'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text.strip()
        l_message(calling_script(), f'company_text  {my_company_text}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_text: str = ''

    return my_company_text


def get_my_company_sitelinks(div):
    """Найти и вернуть ссылку на сайт компании.
    """
    try:
        my_company_sitelinks: str = div.find('div', attrs={
            'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text.strip()
        l_message(calling_script(), f'company_site_links  {my_company_sitelinks}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_sitelinks: str = 'N/A'

    return my_company_sitelinks


def get_my_company_link_1(div):
    """Найти и вернуть быструю ссылку на сайт компании.
    """
    try:
        my_company_link_1: str = div.find('a', attrs={
            'class': 'link link_theme_outer path__item i-bem'}).text.strip()
        text: int = my_company_link_1.rfind('›')
        if text > 0:
            my_company_link_1 = my_company_link_1[0:text]
        l_message(calling_script(), f'company_link_1 {my_company_link_1}', color=BColors.OKBLUE)

    except AttributeError as err:
        l_message(calling_script(), f" AttributeError: {repr(err)}", color=BColors.FAIL)
        my_company_link_1: str = ''

    return my_company_link_1


class Parser:
    """ Базовый класс парсера.
    """

    def __init__(self, urls, path_to_queries: str, query=None):

        self.urls = urls
        self.queries_path = path_to_queries
        self.query = query
        self.divs_requests: list = []  # список c ответами
        self.result: list = []

        self.headers = []
        self.divs = None
        self.ques = None
        self.url = None
        self.request = None
        self.session = None

        self.proxyes: list = []  # создаем список c прокси
        self.full_path_to_file = None
        self.proxy_path = None
        self.request_timeout = None

        self.soup_name = None
        self.soup_class = None
        self.soup_attribute = None

    def start_work(self):
        """ Определение начало работы в базовом классе.
        """
        assert self.urls is not None, f"{calling_script()} urls not passed"

        for number, item_url in enumerate(self.urls):
            l_message(calling_script(), f"\nЗапрос номер: {number + 1} \n", color=BColors.OKBLUE)

            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                if number <= 100:
                    self.get_response()
                else:
                    self.proxyes = self.get_proxy_pool_from_file()
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
                    l_message(calling_script(), 'Успешный запрос!', color=BColors.OKBLUE)
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
        assert self.proxyes is not None, "proxyes not set"

        data_requests = self._create_data_request()

        for request_number, item_request in enumerate(list(data_requests)):

            if request_number >= 100:
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
                                     "TIMEOUT": self.request_timeout * 2,
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
        if not hasattr(self.request, self.soup_attribute):
            l_message(calling_script(), 'Ответ не содержит текст :(', color=BColors.FAIL)
            return

        if self.request.text == '':
            l_message(calling_script(), 'Ответ не содержит текстовых данных :(', color=BColors.FAIL)
            return

        soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
        self.divs = soup.find_all(class_=self.soup_class)  # данные ответа

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
        l_message(calling_script(), f'My public IP {requests.get("http://www.icanha4zip.com").text[:-2]}',
                  color=BColors.OKBLUE)

    def get_proxy_pool_from_file(self):
        """Создаём пул прокси.
        """
        # открываем файл с ключами по пути path_to_queries и считываем ключи
        with open(self.proxy_path, 'r', encoding='utf-8') as file:
            return [x.strip() for x in file if x != ""]


class ParserYandex(Parser):
    """ Класс парсера Яндекса наследуется от базового парсера.
    """

    def __init__(self, *, urls):
        super(ParserYandex, self).__init__(self, urls)
        self.urls = urls

        self.divs_requests: list = []
        self.result: list = []
        self.proxyes: list = []  # создаем список c прокси

        self.ques = None
        self.url = None
        self.request = None
        self.divs = None

        self.headers = [HEADERS_TEST, kad_head]
        self.full_path_to_file = full_path
        self.proxy_path = proxy_path
        self.request_timeout = REQUEST_TIMEOUT

        self.full_path = full_path + PARSER_NAME + ' ' + date_today + extension

        self.soup_name = soup_name
        self.soup_class = soup_class
        self.soup_attribute = soup_attribute

    def start_work(self):
        """ функция парсера.
        """
        assert self.urls is not None, str(calling_script()) + 'urls not passed'

        for number, item_url in enumerate(self.urls):
            l_message(calling_script(), f"\nЗапрос номер: {number + 1} \n", color=BColors.OKBLUE)

            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                if number <= 100:
                    self.get_response()
                else:
                    self.proxyes = self.get_proxy_pool_from_file()
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

    def divs_text_shelves(self):
        """ Поиск данных в ответе сайта.
        """
        i_row: int = 1
        for div in tqdm(self.divs):
            my_company_title: str = get_my_company_title(div)
            my_company_cid: str = get_my_company_cid(div)
            my_company_link_1: str = get_my_company_link_1(div)
            my_company_site_links: str = get_my_company_sitelinks(div)
            my_company_text: str = get_my_company_text(div)
            my_company_contact: str = get_my_company_contact(div)

            self.divs_requests.append({'rowNom': i_row,
                                       'ques': self.ques,
                                       'company_title': my_company_title,
                                       'company_cid': my_company_cid,
                                       'company_link_1': my_company_link_1,
                                       'company_sitelinks': my_company_site_links,
                                       'company_text': my_company_text,
                                       'company_contact': my_company_contact})
            i_row = i_row + 1

    def write_data_to_file(self):
        """ Запись данных в файл.
        """
        file_writer = WriterToXLSX(self.divs_requests, self.full_path)
        file_writer.file_writer()


def url_constructor_yandex(queries_path, selected_base_url, selected_region, within_time, num_doc=10, max_pos=3):
    """ Формирование запросов из запчастей.
    """
    urls = []
    # открываем файл с ключами по пути path_to_queries и считываем ключи
    with open(queries_path, 'r', encoding='utf-8') as file:
        query = [x.strip() for x in file]

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


def main():
    """Основная функция с параметрами.
    """
    l_message(calling_script(), '\n**** Start ****\n', color=BColors.OKBLUE)

    urls = url_constructor_yandex(queries_path, base_url_yandex, region_yandex, within_time, num_doc,
                                  url_max_pos_yandex)

    parser = ParserYandex(urls=urls)
    parser.start_work()

    l_message(calling_script(), '\n**** Done ****\n', color=BColors.OKBLUE)


if __name__ == '__main__':
    main()
