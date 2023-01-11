import csv

import requests
from bs4 import BeautifulSoup
import fake_useragent
import asyncio
import aiohttp


class Free_Proxt_List_Net:
    def __init__(self):
        self.domain = 'https://free-proxy-list.net/'
        self.fake_useragent = lambda: fake_useragent.UserAgent().random.strip()
        self.csv_path = 'free_proxy_list_net.csv'


    async def check(self, session, proxy, port):
        try:
            await asyncio.sleep(1, 5)
            address = 'http://'+proxy+':'+port
            async with await session.get(url='http://httpbin.org/ip', proxy=address, timeout=3.0) as response:
                if response.ok:
                    print(proxy+':'+port, True)
                    return [proxy, True]
                else:
                    print(proxy+':'+port, False)
                    return [proxy, False]
        except asyncio.CancelledError:
            print(proxy, 'Stop')
        except BaseException as _ex:
            print(_ex)
            print(proxy+':'+port, False, 'Timeout')
            return [proxy, False]
    async def main_async(self, proxies_list):
        async with aiohttp.ClientSession(headers={'User-Agent': self.fake_useragent()}, trust_env=True) as session:
            tasks=[]
            for proxy in proxies_list:
                task = asyncio.create_task(self.check(session, proxy['IP Address'], proxy['Port']))
                tasks.append(task)
            return await asyncio.gather(*tasks)
    def check_proxies_async(self, proxies_list):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        gather_res = asyncio.run(self.main_async(proxies_list))
        res_proxies_dict = {}
        for proxy_list in gather_res:
            res_proxies_dict.update({proxy_list[0]: proxy_list[1]})
        return res_proxies_dict



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

        response = requests.get(self.domain, headers={'User-Agent': self.fake_useragent()})
        bs = BeautifulSoup(response.text, 'lxml')
        proxy_params_list = [th.text.strip() for th in bs.find('section', id='list').find('thead').find_all('th')]

        proxy_tr_list = bs.find('section', id='list').find('tbody').find_all('tr')
        proxy_list = []
        for tr in proxy_tr_list:
            proxy_list.append({})
            for i, td in enumerate(tr):
                proxy_list[-1].update({proxy_params_list[i]: td.text.strip('\n')})
            proxy_list[-1].pop(proxy_params_list[-1])

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
        fieldnames_list=self.get_fields_names()
        with open(self.csv_path, flag, encoding='utf-8-sig', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames_list, delimiter=';')
            if flag == 'w': writer.writeheader()
            for proxy in proxy_list:
                writer.writerow(proxy)



    def update(self, filter=[]):
        # Получает proxy с сайта, проверяет работоспособность, добавляет новые
        # filter -- список параметров для новых proxy
        # Возвращает True, либо код ошибки
        proxy_from_site_list = self.parsing()
        if filter:
            proxy_from_site_list = self.filter(proxy_from_site_list, filter)

        # Асинхронка пока не работает
        proxy_checked_list = self.check_proxies_async(proxy_from_site_list)
        good_proxy_site = []
        for proxy in proxy_from_site_list:
            if proxy_checked_list[proxy['IP Address']]:
                good_proxy_site.append(proxy)

        # proxy_checked_list=[]
        # for proxy in proxy_from_site_list:
        #     if self.check_proxy(proxy['IP Address'], proxy['Port']):
        #         proxy_checked_list.append(proxy)


        proxies_from_csv = self.get_from_csv()
        proxies_to_save=[]
        for proxy in good_proxy_site:
            save = True
            for proxy_from_csv in proxies_from_csv:
                if proxy['IP Address'] == proxy_from_csv['IP Address']:
                    save = False
            if save:
                proxies_to_save.append(proxy)

        return self.save_to_csv(proxies_to_save)

    def check_csv(self):
        # Выгружает proxy из csv, проверяет робочие, перезаписывает файл
        # Возвращает True, либо код ошибки
        proxy_from_csv = self.get_from_csv()
        proxy_checked_list = self.check_proxies_async(proxy_from_csv)
        good_proxies_list = []
        for proxy in proxy_from_csv:
            if proxy_checked_list[proxy['IP Address']]:
                good_proxies_list.append(proxy)

        return self.save_to_csv(good_proxies_list, 'w')

    def get_proxies(self, filter=[]):
        proxies_from_csv = self.get_from_csv()
        proxy_checked_list = self.check_proxies_async(proxies_from_csv)
        good_proxies_list = []
        for proxy in proxies_from_csv:
            if proxy_checked_list[proxy['IP Address']]:
                good_proxies_list.append(proxy)

        if filter:
            return self.filter(good_proxies_list, filter)
        return good_proxies_list


parser = Free_Proxt_List_Net()
parser.update()





