# Алгоритм для приведения файлов из dictionaries в нужный вид

import os
from pprint import pprint

en_alphabet = 'abcdefghijklmnopqrstuvwxyz'
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

for dir in os.walk("./dictionaries"):
    files = dir[2]
    for filename in files:
        next_file = False
        with open(f'./dictionaries/{filename}', 'r', encoding='utf-8') as file_read:
            lines_to_save = []
            for i, line in enumerate(file_read.readlines()):
                if not i:
                    lines_to_save.append(line)
                    continue
                if line.find('--') != -1:
                    next_file = True
                    break

                for num, char in enumerate(line):
                    if ru_alphabet.find(char) != -1:
                        english = line[:num].strip()
                        translation = line[num:].strip()

                        for k, rus_char in enumerate(translation):
                            if rus_char not in ru_alphabet+' ,':
                                translation = translation[:k].strip()


                        english_list = english.split()

                        # Для исправления уже пройденных файлов
                        # while '--' in english_list: english_list.remove('--')
                        for word in english_list:
                            if word in ['a', 'an', 'at']:
                                english_list.remove(word)
                        english = ' '.join(english_list)
                        lines_to_save.append(f'{english} -- {translation}\n')
                        break

        if next_file: continue

        with open(f'./dictionaries/{filename}', 'w', encoding='utf-8') as file_write:
            for line in lines_to_save:
                file_write.write(line)



