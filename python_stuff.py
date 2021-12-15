import collections
import re

from pandas import read_csv

from numpy.lib.npyio import load


def load_sx3_table(filename: str) -> dict:
    prefix_dict = {}
    df = read_csv(f'{filename}', delimiter=';', error_bad_lines=False).values
    for i in df:
        if i[3] in prefix_dict:
            prefix_dict[i[3]].append(i[0])
        else:
            prefix_dict[i[3]] = [i[0]]
    return prefix_dict

def get_prefix_by_name_list(list_of_names: list, table: dict) -> str:
    """ 
    Функция получения префикса по списку переданных имен гридов:
    Принимает список гридов (>= 3 элементов) и таблицу переводов,
    возвращает префикс. Если префиксов > 1 - возвращает пустой список
    ["Заказ", "Альтернат.", "Фктр конвер.", "Фктр конвер.", "Ввод MRP",
    "Дт.ср.дейс.", "Description"] -> 'GI'
    """    
    try:
        list_of_names_copy = list_of_names.copy()
        list_of_len_names = []
        if list_of_names_copy[0] == " ":
            list_of_names_copy.pop(0)
        for i in list_of_names_copy:
            i = i.strip()
            list_of_len_names.append(len(table[i]))
        list_of_names_with_less_length = []
        def get_three_index():
            index = list_of_len_names.index(min(list_of_len_names))
            list_of_names_with_less_length.append(list_of_names_copy[index].strip())
            list_of_len_names.pop(index)
            list_of_names_copy.pop(index)
        get_three_index()
        get_three_index()
        get_three_index()
        first_list = table[list_of_names_with_less_length[0]]
        second_list = table[list_of_names_with_less_length[1]]
        third_list = table[list_of_names_with_less_length[2]]
        prefix_list = first_list + second_list + third_list
        re_mask = "([a-zA-Z0-9]{1,3}[^_])"
        for i in prefix_list:
            index = prefix_list.index(i)
            prefix_list[index] = re.search(re_mask, i).group(1)
        counter = collections.Counter(prefix_list)
        prefix_list.clear()
        for prefix, count in counter.items():
            if count >= 3:
                prefix_list.append(prefix)
        return prefix_list
    except:
        prefix_list = []
        return prefix_list

def get_code_by_grid_name(grid_name: str, prefix: str, prefix_dict: dict) -> str:
    """
    Функция получения кода поля по имени грида:
    Получает на вход имя поля, префикс, полученный из get_prefix_by_neighbours,
    и словарь переводов
    ('% наценки', 'BZ', prefix_dict) -> 'BZ_MARKUP'
    """
    prefix_len = len(prefix)
    code_list = prefix_dict[grid_name]
    for i in code_list:
        if i[:prefix_len] == prefix:
            return i


def grid_translator(grid_dict: dict) -> dict:
    """
    Функция перевода гридов: 
    Получает на вход словарь вида: {номер грида: [список имен гридов]}
    Возвращает словарь вида: {номер грида: [переводы имен гридов]}
    """
    output_dict = {}
    table = load_sx3_table("C:\proj\instruments\SX3_update\sx3.csv")
    for key, value in grid_dict.items():
        if len(value) >= 3:
            output_list = []
            prefix = get_prefix_by_name_list(value, table)
            if len(prefix) == 1:
                for name in value:
                    if name == " ":
                        continue
                    name = name.strip()
                    translate = get_code_by_grid_name(name, prefix[0], table)
                    if translate:
                        output_list.append(translate.strip())
                    else:
                        output_list.append('None')
                if value[0] == " ":
                    output_list.insert(0, 'None')
                output_dict[key] = output_list
            else:
                output_dict[key] = 'more than one prefix found, could not find translation'
        elif len(value) < 3:
            output_dict[key] = 'length of the grid is too small, could not find translation '
        else:
            print('something else')
    return output_dict