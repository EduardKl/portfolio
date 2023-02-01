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


class Free_Proxt_Cz:
    def __init__(self):
        self.domain = 'https://free-proxy.cz/en/'
        self.fake_useragent = lambda: fake_useragent.UserAgent().random.strip()
        self.csv_path = 'free_proxy_cz.csv'


    async def check(self, protocol, ip, port):
        await asyncio.sleep(1, 5)
        if not protocol == 'HTTPS':
            if protocol == 'SOCKS5': proxy_type = ProxyType.SOCKS5
            elif protocol == 'SOCKS4': proxy_type = ProxyType.SOCKS4
            else: proxy_type = ProxyType.HTTP
            connector = ProxyConnector(
                    proxy_type=proxy_type,
                    host=ip,
                    port=port,
                    rdns=True
            )
            try:
                async with aiohttp.ClientSession(connector=connector, headers={'User-Agent': self.fake_useragent()},
                                                 trust_env=True) as session:
                    try:
                        async with await session.get(url='http://httpbin.org/ip', timeout=3.0) as response:
                            if response.ok:
                                print(f'{protocol}://{ip}', True)
                                return [ip, True]
                            else:
                                print(f'{protocol}://{ip}', False)
                                return [ip, False]
                    except asyncio.CancelledError:
                        print(f'{protocol}://{ip}', 'Stop')
                    except BaseException as _ex:
                        print(f'{protocol}://{ip}', False, 'Timeout')
                        return [ip, False]
            except:
                print(f'{protocol}://{ip}', 'no session')
        else:
            try:
                async with aiohttp.ClientSession(headers={'User-Agent': self.fake_useragent()},
                                                 trust_env=True) as session:
                    try:
                        address = f'http://{ip}:{port}'
                        async with await session.get(url='http://httpbin.org/ip', proxy=address, timeout=3.0) as response:
                            if response.ok:
                                print(f'{protocol}://{ip}', True)
                                return [ip, True]
                            else:
                                print(f'{protocol}://{ip}', False)
                                return [ip, False]
                    except asyncio.CancelledError:
                        print(f'{protocol}://{ip}', 'Stop')
                    except BaseException as _ex:
                        print(_ex)
                        print(f'{protocol}://{ip}', False, 'Timeout')
                        return [ip, False]
            except:
                print(f'{protocol}://{ip}', 'no session')

    async def main_async(self, proxies_list):
        tasks=[]
        for proxy in proxies_list:
            protocol = proxy['Protocol']
            ip = proxy['IP address']
            port = proxy['Port']

            task = asyncio.create_task(self.check(protocol, ip, port))
            tasks.append(task)
        return await asyncio.gather(*tasks)
    def check_proxies_async(self, proxies_list):
        print('CHECKING...')
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        gather_res = asyncio.run(self.main_async(proxies_list))
        res_proxies_dict = {}
        for proxy_list in gather_res:
            res_proxies_dict.update({proxy_list[0]: proxy_list[1]})
        return res_proxies_dict


    def get_fields_names_site(self):
        response = requests.get(self.domain, headers={'User-Agent': self.fake_useragent()})
        bs = BeautifulSoup(response.text, 'lxml')
        fields_names_list = [th.text.strip(' ') for th in bs.find('table', id='proxy_list').find('thead').find_all('th')]
        return fields_names_list
    def get_fields_names(self):
        # Возвращает список названий полей csv
        with open(self.csv_path, 'r', encoding='utf-8-sig') as file:
            row = file.readline().strip('\n')
            fields_names_list = row.split(';')
            return fields_names_list

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

    def parsing(self):
        # Получает proxy с сайта, все если filter пуст
        # filter -- параметры отбора proxy с сайта
        # Возвращает список

        print('PARSING...')
        options_chrome = webdriver.ChromeOptions()
        options_chrome.add_argument('--headless')
        with webdriver.Chrome(options=options_chrome) as browser:
            proxy_list = []
            for page in range(1, 6):
                print(f'Page > {page}')
                browser.get(self.domain+f'proxylist/main/{page}')

                table = browser.find_element(By.ID, 'proxy_list')
                proxy_params_list = [th.text for th in table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')]
                tr_list_wbrr = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

                for i, tr in enumerate(tr_list_wbrr, 1):
                    print(f'Page {page}, {i} proxy')
                    td_list_wbrr = tr.find_elements(By.TAG_NAME, 'td')
                    if len(td_list_wbrr) < 2: continue
                    proxy_list.append({})
                    for i, td in enumerate(td_list_wbrr):
                        proxy_list[-1].update({proxy_params_list[i]: td.text})

        return proxy_list

    def check_proxy(self, proxy, port):
        # Проверяет proxy на работоспособность
        # proxy -- адрес для проверки
        # Возвращает True, либо код ошибки
        address = 'http://'+proxy+':'+port
        proxy_dict = {
            'http': address,
            'https': address
        }
        try:
            response = requests.get('https://httpbin.org/ip', headers={'User-Agent': self.fake_useragent()}, proxies=proxy_dict, timeout=1.0)
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
                if i==0: continue
                proxy_from_csv_list.append(proxy)


        return proxy_from_csv_list

    def save_to_csv(self, proxy_list, flag='a'):
        # Сохраняет proxy в файл csv
        # Возвращает True, либо код ошибки
        print('SAVING...')
        if os.path.exists('free_proxy_cz.csv'):
            fieldnames_list=self.get_fields_names()
        else:
            fieldnames_list=self.get_fields_names_site()
        with open(self.csv_path, flag, encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames_list, delimiter=';')
            if flag == 'w': writer.writeheader()
            for proxy in proxy_list:
                writer.writerow(proxy)
        print('END SAVING')



    def update(self, filter=[]):
        # Получает proxy с сайта, проверяет работоспособность, добавляет новые
        # filter -- список параметров для новых proxy
        # Возвращает True, либо код ошибки
        print('UPDATING...')
        proxy_from_site_list = self.parsing()
        if filter:
            proxy_from_site_list = self.filter(proxy_from_site_list, filter)

        proxy_checked_list = self.check_proxies_async(proxy_from_site_list)
        good_proxy_site = []
        for proxy in proxy_from_site_list:
            if proxy_checked_list[proxy['IP address']]:
                good_proxy_site.append(proxy)

        # proxy_checked_list=[]
        # for proxy in proxy_from_site_list:
        #     if self.check_proxy(proxy['IP address'], proxy['Port']):
        #         proxy_checked_list.append(proxy)

        if os.path.exists('free_proxy_cz.csv'):
            proxies_from_csv = self.get_from_csv()
            proxies_to_save=[]
            for proxy in good_proxy_site:
                save = True
                for proxy_from_csv in proxies_from_csv:
                    if proxy['IP address'] == proxy_from_csv['IP address']:
                        save = False
                if save:
                    proxies_to_save.append(proxy)

            return self.save_to_csv(proxies_to_save)
        else:
            return self.save_to_csv(good_proxy_site, 'w')

    def check_csv(self):
        # Выгружает proxy из csv, проверяет робочие, перезаписывает файл
        # Возвращает True, либо код ошибки
        proxy_from_csv = self.get_from_csv()
        proxy_checked_list = self.check_proxies_async(proxy_from_csv)
        good_proxies_list = []
        for proxy in proxy_from_csv:
            if proxy_checked_list[proxy['IP address']]:
                good_proxies_list.append(proxy)

        return self.save_to_csv(good_proxies_list, 'w')

    def get_proxies(self, filter=[]):
        proxies_from_csv = self.get_from_csv()
        proxy_checked_list = self.check_proxies_async(proxies_from_csv)
        good_proxies_list = []
        for proxy in proxies_from_csv:
            if proxy_checked_list[proxy['IP address']]:
                good_proxies_list.append(proxy)

        if filter:
            return self.filter(good_proxies_list, filter)
        return good_proxies_list


parser = Free_Proxt_Cz()
print(parser.update())