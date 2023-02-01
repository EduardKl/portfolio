import time
import random
import json
from pprint import pprint
import csv
import os.path
import requests
from bs4 import BeautifulSoup
import fake_useragent
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
from selenium import webdriver
from selenium.webdriver.common.by import By


class FreeProxyNet:
    def __init__(self):
        self.domain = 'https://www.freeproxylists.net/?cl=true'
        self.fake_useragent = lambda: fake_useragent.UserAgent().random.strip()
        self.csv_path = 'freeproxylists.csv'



    async def pars_page(self, url, params_proxy_list, proxies_for_pars):
        # Корутина парсит прокси со страницы
        # url -- ссылка на страницу для парсинга
        # params_proxy_list -- список с параметрами прокси адреса
        # proxies_for_pars -- список прокси для парсинга
        # Возвращает список словарей прокси со страницы
        await asyncio.sleep(3, 10)

        url_list = url.split('start=')
        if len(url_list) > 1:
            page = int(int(url_list[1]) / 64 + 1)  # Высчитывание номера страницы из ссылки для выведения в консоль
        else:
            page = 1

        proxies_list = []  # список для спаршенных прокси
        for proxy_num, proxy in enumerate(proxies_for_pars, 1):
            proxy_address = f'http://{proxy["IP Address"]}:{proxy["Port"]}'

            async with aiohttp.ClientSession(headers={'User-Agent': self.fake_useragent()}, trust_env=True) as session:
                try:
                    async with await session.get(url=url, proxy=proxy_address, timeout=3.0) as response:
                        if response.ok:
                            bs = BeautifulSoup(response.text(), 'lxml')
                            proxy_line_list = bs.find('div', 'table_block').find('tbody').find_all('tr')
                            for line_num, line in enumerate(proxy_line_list, 1):
                                proxies_list.append({})
                                param_list = line.find('td')
                                for i, param in enumerate(param_list):
                                    proxies_list[-1].update({params_proxy_list[i]: param.text.strip()})
                                print(f'Page {page}, {line_num} proxy is getted')

                            return proxies_list

                        else:
                            print(f'Proxy {proxy_num}/{len(proxies_for_pars)}: Page {page} No ok')
                except TimeoutError:
                    print(f'Proxy {proxy_num}/{len(proxies_for_pars)}: Page {page} Timeout')
                    await asyncio.sleep(3, 5)
                except asyncio.CancelledError as cancel_er:
                    print(f'Proxy {proxy_num}/{len(proxies_for_pars)}: Page {page} Canceled')
                except BaseException:
                    print(f'{proxy_address} {page} BIG ERROR')
    async def pars_async(self, params_tuple):
        # Корутина собирает таски парсеры по страницам
        # param_turple = (max_page, params_proxy_list, proxies_for_pars), где
        # max_page -- номер последней страницы на сайте
        # params_proxy_list -- список с параметрами прокси адреса
        # proxies_for_pars -- список с прокси для парсинга
        # Возвращает список прокси с сайта
        max_page = params_tuple[0]
        params_proxy_list = params_tuple[1]
        proxies_for_pars = params_tuple[2]

        tasks = []
        for page in range(0, max_page + 1):
            url = self.domain
            if page: url += f'?start={64 * page}'
            task = asyncio.create_task(self.pars_page(url, params_proxy_list, proxies_for_pars))
            tasks.append(task)
        return await asyncio.gather(*tasks)

    async def check_http(self, ip, port):
        # Корутина отправляет запрос на http/https прокси и отдаёт response корутине check
        # ip -- адрес проверяемого прокси
        # port -- порт проверяемого прокси
        # Возвращает объект response
        proxy_address = f'http://{ip}:{port}'
        async with aiohttp.ClientSession(headers={'User-Agent': self.fake_useragent()}, trust_env=True) as session:
            async with await session.get(url='http://httpbin.org/ip', proxy=proxy_address, timeout=3.0) as response:
                pprint(response)
    async def check_socks(self, protocol, ip, port):
        # Корутина отправляет запрос на socks прокси и отдаёт response корутине check
        # protocol -- протокол проверяемого прокси
        # ip -- адрес проверяемого прокси
        # port -- порт проверяемого прокси
        # Возвращает объект response
        if protocol == 'SOCKS5':
            proxy_type = ProxyType.SOCKS5
        elif protocol == 'SOCKS4':
            proxy_type = ProxyType.SOCKS4
        else:
            proxy_type = ProxyType.HTTP

        connector = ProxyConnector(
            proxy_type=proxy_type,
            host=ip,
            port=port,
            rdns=True
        )

        async with aiohttp.ClientSession(connector=connector, headers={'User-Agent': self.fake_useragent()}, trust_env=True) as session:
            async with await session.get(url='http://httpbin.org/ip', timeout=3.0) as response:
                pprint(response)

    async def check(self, protocol, ip, port):
        # Корутина отправляет запрос на прокси
        # protocol -- протокол проверяемого прокси
        # ip -- адрес проверяемого прокси
        # port -- порт проверяемого прокси
        # Возвращает список с 2-я эдементами: адрес и bool результат запроса
        await asyncio.sleep(1, 5)
        try:
            pass
            # if protocol in ['HTTP', 'HTTPS']:
            #     response = await self.check_http(ip, port)
            # else:
            #     response = await self.check_socks(protocol, ip, port)
            #
            # pprint(response)
            # if response.ok:
            #     print(f'{protocol}://{ip}', True)
            #     return [ip, True]
            # else:
            #     print(f'{protocol}://{ip}', False)
            #     return [ip, False]
        except TimeoutError:
            print(f'{protocol}://{ip}', 'Timeout')
        except asyncio.CancelledError:
            print(f'{protocol}://{ip}', 'Stop')
        # except BaseException as _ex:
        #     print(f'{protocol}://{ip}', False, 'Timeout')
        #     return [ip, False]
    async def check_proxies(self, params_tuple):
        # Корутина собирает и запускает таски чекеры
        # params_tuple -- кортеж *args аргументов из функции раннера
        # Возвращает результат запущенных задач
        print('CHECKING...')
        proxies_list = params_tuple[0]

        tasks = []
        for proxy in proxies_list:
            protocol = proxy['Protocol']
            ip = proxy['IP Address']
            port = proxy['Port']

            task = asyncio.create_task(self.check(protocol, ip, port))
            tasks.append(task)
        await asyncio.gather(*tasks)

    # ДОПИСАТЬ!!!!
    def main_async(self, func, *args):
        # Функция запускает переданную в аргументы корутину
        # func() -- корутина для запуска
        # args -- кортеж с аргументами для корутины
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        gather_res = asyncio.run(func(args))
        pass



    # Дописать обработку ошибок
    def get_browser(self):
        # Возвращает объект webdriver
        options_chrome = webdriver.ChromeOptions()
        options_chrome.add_argument('--headless')
        return webdriver.Chrome(options=options_chrome)
    def quit_browser(self, browser):
        # Закрывает браузер
        browser.quit()

    # ДОПИСАТЬ комментарии и обработку исключений
    def get_proxy_params(self, browser):
        # Получение списка названий параметров прокси
        print('GET FIELDS NAMES...')
        try:
            browser.get(self.domain)
            proxy_params_by = browser.find_element(By.CLASS_NAME, 'DataGrid').find_element(By.CLASS_NAME, 'Caption').find_elements(By.TAG_NAME, 'td')
            proxy_params_list = [param_by.text for param_by in proxy_params_by]

            return proxy_params_list
        except:
            print('Get params proxy FAILED')
    def get_fields_names(self):
        # Возвращает список названий полей csv
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            row = file.readline().strip('\n')
            fields_names_list = row.split(';')
            return fields_names_list

    # ДОПИСАТЬ!!!!
    def get_max_page(self, browser):
        # Получение номера последней страницы
        print('GETTING MAX PAGE...')
        try:
            browser.get(self.domain)
            pages_links_list = [link.text.strip() for link in browser.find_element(By.CLASS_NAME, 'page').find_elements(By.TAG_NAME, 'a')]
            if not pages_links_list[-1].isdigit(): pages_links_list.pop()  # Последняя ссылка -- это ссылка на след. страницу (надпись "Next" вместо цифры), удаляем последний элемент списка
            max_page = int(pages_links_list[-1])
            return max_page
        except TypeError:
            # Если .isdigit() выдало ошибку
            print('Get Max Page FAILED TypeError')
        except AttributeError:
            print('Get Max Page FAILED AttributeError')



    def filter(self, proxy_list, filter):
        # Отбирает прокси из списка по фильтру
        # proxy_list -- список прокси для отбора
        # filter -- словарь с параметрами и их значениями для отбора
        # filter = {'port': XX, 'country': ['Finland', 'France']}
        # Возвращает список отобранных proxy, пустой список, если подходящих нет

        if not filter:
            return proxy_list

        res_proxy_list = []
        for proxy in proxy_list:
            for param in filter:
                if isinstance(filter['param'], dict):
                    if proxy[param] in filter[param]:
                        res_proxy_list.append(proxy)
                if proxy[param] == filter[param]:
                    res_proxy_list.append(proxy)

        return res_proxy_list

    def check_proxy(self, proxy, port):
        # Проверяет proxy на работоспособность
        # proxy -- адрес для проверки
        # Возвращает True, либо код ошибки
        address = 'http://' + proxy + ':' + port
        proxy_dict = {
            'http': address,
            'https': address
        }
        try:
            response = requests.get('https://httpbin.org/ip', headers={'User-Agent': self.fake_useragent()},
                                    proxies=proxy_dict, timeout=1.0)
            print(proxy, response.status_code == 200)
            return response.status_code == 200
        except:
            print(proxy, False)
            return False

    def get_from_csv(self):
        # Выгружает proxy из csv файла
        # filter -- параметры для отбора proxy
        # Возвращает список
        print('GETTING FROM CSV...')
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, fieldnames=self.get_fields_names(), delimiter=';')
            proxy_from_csv_list = []
            for i, proxy in enumerate(reader):
                if i == 0: continue
                proxy_from_csv_list.append(proxy)

        return proxy_from_csv_list

    def save_to_csv(self, proxy_list, flag='a'):
        # Сохраняет proxy в файл csv
        # Возвращает True, либо код ошибки
        print('SAVING...')
        if os.path.exists(self.csv_path):
            fieldnames_list = self.get_fields_names()
        else:
            fieldnames_list = self.get_fields_names_site()
        with open(self.csv_path, flag, encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames_list, delimiter=';')
            if flag == 'w': writer.writeheader()
            for proxy in proxy_list:
                writer.writerow(proxy)
        print('END SAVING')

    def parsing(self, filter = []):
        # Получает proxy с сайта, все если filter пуст
        # filter -- параметры отбора proxy с сайта
        # Возвращает список

        print('PARSING...')
        proxy_site_list = []
        browser = self.get_browser()
        max_page = self.get_max_page(browser)
        proxy_params_list = self.get_proxy_params(browser)
        max_page = 1
        for page in range(1, max_page+1):
            #  ЗАКОНЧИЛ ЗДЕСЬ!!!!
            print(f'Page > {page}')
            url = f'{self.domain}?page={page}'

            try:
                browser.get(url)
                page_bs = BeautifulSoup('', 'lxml')
                #  ЗАКОНЧИЛ ЗДЕСЬ!!!!
                proxy_tr_list = [proxy_tr for proxy_tr in browser.find_element(By.CLASS_NAME, 'DataGrid').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')]
                for proxy_tr_num, proxy_tr in enumerate(proxy_tr_list, 1):
                    if not proxy_tr_num - 1: continue  # Пропускаем строку с заголовками
                    if not proxy_tr.text: continue  # Отсеиваем строки с рекламой
                    print(f'Page {page}, {proxy_tr_num} proxy')
                    proxy_site_list.append({})
                    for param_num, proxy_td in enumerate(proxy_tr.find_elements(By.TAG_NAME, 'td')):
                        proxy_site_list[-1].update({proxy_params_list[param_num]: proxy_td.text.strip()})
            except:
                print('GET PAGE FAILED')
                pass

        return proxy_site_list

    # ДОПИСАТЬ!!!!
    def update(self, filter=[]):
        # Получает proxy с сайта, проверяет работоспособность, добавляет новые
        # filter -- список параметров для новых proxy
        # Возвращает True, либо код ошибки
        print('UPDATING...')
        proxy_site_list = self.parsing()
        if filter:
            proxy_site_list = self.filter(proxy_site_list, filter)

        # proxies_checked_list = self.main_async(self.check_proxies, proxy_site_list)
        # good_proxy_site = []
        # for proxy in proxy_site_list:
        #     if proxies_checked_list[proxy['IP Address']]:
        #         good_proxy_site.append(proxy)

        if os.path.exists(self.csv_path):
            proxies_from_csv = self.get_from_csv()
            proxies_to_save = []
            for proxy in proxy_site_list:
                save = True
                for proxy_from_csv in proxies_from_csv:
                    if proxy['IP Address'] == proxy_from_csv['IP Address']:
                        save = False
                if save:
                    proxies_to_save.append(proxy)

            return self.save_to_csv(proxies_to_save)
        else:
            return self.save_to_csv(proxy_site_list, 'w')

    def check_csv(self):
        # Выгружает proxy из csv, проверяет робочие, перезаписывает файл
        # Возвращает True, либо код ошибки
        proxy_from_csv = self.get_from_csv()
        proxy_checked_list = self.main_async(self.check_proxies, proxy_from_csv)
        good_proxies_list = []
        for proxy in proxy_from_csv:
            if proxy_checked_list[proxy['IP address']]:
                good_proxies_list.append(proxy)

        return self.save_to_csv(good_proxies_list, 'w')

    def get_proxies(self, filter=[]):
        proxies_from_csv = self.get_from_csv()
        proxy_checked_list = self.main_async(self.check_proxies, proxies_from_csv)
        good_proxies_list = []
        for proxy in proxies_from_csv:
            if proxy_checked_list[proxy['IP address']]:
                good_proxies_list.append(proxy)

        if filter:
            return self.filter(good_proxies_list, filter)
        return good_proxies_list


parser = FreeProxyNet()
print('RUN')
parser.update()