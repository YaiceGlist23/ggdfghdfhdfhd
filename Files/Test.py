import json
from traceback import print_tb


def to_set_chars_sheet_only_names(data):
    chars_sheet = ["№ авто", "Модель"]
    for car, car_chars in data.items():
        for char, value in car_chars.items():
            if char not in chars_sheet:
                chars_sheet.append(char)
    return chars_sheet

def search_algorythm(array_for_search):
    with open('Data.json', 'r') as fp:
        data = json.load(fp)
        chars_list = to_set_chars_sheet_only_names(data)[1:]
    result_array = []

    for car in [car for car in data.keys()]:
        car_check_list = []
        car_values_list = [car]
        for char, value in data[car].items():
            car_values_list.append(value)

        ind = -1
        for char in chars_list:
            ind += 1
            if array_for_search[ind] == '':
                car_check_list.append(True)
            elif array_for_search[ind] == '-':
                car_check_list.append(car_values_list[ind] == '-')

            else:
                count = 0
                for element in [el.lower() for el in  array_for_search[ind].split()]:
                    if element.lower() in car_values_list[ind].lower():
                        count += 1
                if count == len(array_for_search[ind].split()):
                    car_check_list.append(True)
                else:
                    car_check_list.append(False)
        if all(car_check_list):
            result_array.append(car)
    return result_array



search_algorythm(['Uli', '', '', '', '', '', '', ''])