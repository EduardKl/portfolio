import random
import os



class Eng_Exercises:
    def __init__(self):
        print("""\
                Выберите тип упражнения:
                1. Перевод на русский
                2. Обратный перевод
                """)
        self.type = int(input())

    def chenge_type(self):
        # Функция меняет тип упражнения
        # 0 -- писать перевод на русском
        # 1 -- писать обратный перевод на английский
        print('Тип изменён')
        if self.type == 0: self.type = 1
        else: self.type = 0
    def get_dict_names(self):
        pass
    def get_dict(self, dict_name='home_items'):
        dictionary = []
        with open(f'dictionaries/{dict_name}.txt', 'r', encoding='utf-8') as file:
            for i, line in enumerate(file.readlines()):
                if not i: continue
                line.strip('\n')
                line_list = line.split('--')
                eng = line_list[0].strip()
                rus = line_list[1].strip()
                if rus.find(',') != -1:
                    rus = [word.strip() for word in rus.split(',')]

                dictionary.append((eng, rus))
        return dictionary
    def get_dict_from_dir(self):
        dict_names_list = []
        for root, dirs, files in os.walk("./dictionaries"):
            for filename in files:
                dict_names_list.append({})
                with open(f'./dictionaries/{filename}', 'r', encoding='utf-8') as file:
                    dict_names_list[-1].update({'name': file.readline().strip('\n'), 'code': filename[:-4]})
        return dict_names_list
    def choice_dict(self):
        # Выводит в консоль пронумированный список словарей из папки
        # Возвращает название файла выбранного словаря
        dict_names_list = self.get_dict_from_dir()
        for i, dict_names in enumerate(dict_names_list, 1):
            print(f'{i}. {dict_names["name"]}')
        choice = int(input()) - 1
        return dict_names_list[choice]['code']

    # Поправить код!!!
    def start(self):
        while True:
            # Выбор и загрузка словаря, при запуске программы или смене тематики
            if ('answer' not in locals()) or (answer == 2):
                dict_name = self.choice_dict()
                dictyonary = self.get_dict(dict_name)

            # Получение случайного слова из списка
            word_tuple = random.choice(dictyonary)
            eng = word_tuple[0]
            rus = word_tuple[1]
            if self.type == 1:
                question = eng
                translation = rus
            else:
                if isinstance(rus, list):
                    question = random.choice(rus)
                else:
                    question = rus
                translation = eng


            answer = input(f'{question} -- ').lower()
            if answer.isdigit(): answer = int(answer)
            if not answer: break
            if answer == 1: self.chenge_type()
            if answer == 2: continue

            # Проверка введённого значения
            if self.type == 1:
                if isinstance(rus, list):
                    if answer in rus: print('+')
                    else: print('-', rus)
                else:
                    if answer == rus: print('+')
                    else: print('-', rus)
            else:
                if answer == eng:
                    print('+')
                else:
                    print('-', eng)

obj = Eng_Exercises()
obj.start()