import json
import re
# from msilib.schema import CheckBox
from subprocess import check_output
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo, askyesno

table_click_state = []
char_blacklist = ['Модель', 'Коробка', 'Страна']  # Список хар-ик не изменяемых
MAIN_DATA = {}  # буфер для поиска
# ----------------------------------------NOTEBOOK_SETTINGS---------------------------------------------------------

# Создание и настройка главного окна
root = Tk()
root.title("Car Data Base")
root.geometry('{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight()))

# Создание виджета Notebook
notebook = ttk.Notebook()
notebook.pack(expand=True, fill=BOTH)

# Создание и размещение фреймов на экран
frame_list = ttk.Frame(notebook)
frame_list.pack(expand=True, fill=BOTH)

frame_change = ttk.Frame(notebook)
frame_change.pack(expand=True, fill=BOTH)

# Добавление фреймов в качестве вкладок
notebook.add(frame_list, text="Список")
notebook.add(frame_change, text="Изменить")


# ----------------------------------------FUNCTIONS--------------------------------------------------------------

# Удаляет все виджеты, переданные в виде списка CLEAN_ARRAY
def TO_CLEAN_LAST_WIDGETS(CLEAN_ARRAY):
    for widget in CLEAN_ARRAY:
        widget.destroy()


# ["№ авто", "Модель", "Мощность", "Привод", ...]
def to_set_chars_sheet_only_names(data):
    chars_sheet = ["№ авто", "Модель"]
    for car, car_chars in data.items():
        for char, value in car_chars.items():
            if char not in chars_sheet:
                chars_sheet.append(char)
    return chars_sheet


# [("102", "Полный", "-", "Япония"), ("502", "-", "3.5", "США"), ... ]
# Хар-ки расположены в массиве относительно характеристик в массиве из функции to_set_chars_sheet_only_names()
# Такой порядок важен для представления всей информации в виджете Table
def to_set_chars_sheets_with_value(data):
    chars_sheet = to_set_chars_sheet_only_names(data)
    main_array = []
    car_num = 0
    for car, car_chars in data.items():
        car_num += 1
        car_array = [car_num, car]
        for char in chars_sheet[2:]:  # [1:] потому что "модель" добавляется в список на прошлой строке
            if char in car_chars:
                car_array.append(car_chars[char])
            else:
                data[car][char] = '-'
                car_array.append('-')
        main_array.append(car_array)
    with open('Data.json', 'w') as fp:
        json.dump(data, fp)
    return main_array


# [("Модель", "val car"), ("Разгон", "2.4"), ("Расход", "9.0"), ... ]
# Для таблицы характеристик в фрейме ИЗМЕНИТЬ, сохраняет порядок из таблицы фрейма СПИСОК
def to_set_pair_char_value(data, selected_car):
    # Изначально добавляем инфу про модель
    main_array = [('Модель', selected_car)]

    # Делаем список характеристик ровно как в таблице из фрейма
    chars_sheet = to_set_chars_sheet_only_names(data)[2:]
    car_chars = data[selected_car]

    # Берем характеристику из списка, если она есть у машины добавляем пару имя значение, если нет, то "-"
    for char in chars_sheet:
        if char in car_chars:
            main_array.append((char, car_chars[char]))
        else:
            main_array.append((char, '-'))

    return main_array


# Проверка посимвольно для валидации НЕ МЕНЯТЬ НИХУЯ!!!
def is_valid(new_value):
    return re.match("\d{0,30}$", new_value) is not None


# Берет введенный из Entry порядковый номер машины после нажатия кнопки ВЫБРАТЬ
# а потом сует название выбранного авто в переменную SELECTED_CAR и в LABEL_LIST
def to_select_auto():
    # global потому что это значение используется в разных частях программы
    global CLEAN_ARRAY_CHANGE
    global selected_car
    global table_click_state
    global button_change_add_char

    with open('Data.json', 'r') as fp:
        data = json.load(fp)
    if table_click_state != []:
        selected_car_num = int(table_click_state[0])
    else:
        selected_car_num = int(entry_list.get())

    # Проверяем есть ли такой номер в базе
    cars_list = [car for car in data.keys()]
    count_cars = len(cars_list)
    if selected_car_num in set(range(1, count_cars + 1)):
        selected_car = cars_list[selected_car_num - 1]  # машины считаем с 1, а не с 0

        # Меняем лейбл на имя машины
        label_list['text'] = selected_car

        # Обновляем фрейм изменений
        return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)
    else:
        return showerror(title="Ошибка", message="Введен неверный номер")


# Удаляет авто из базы данных, заново вызывает виджет таблицы
def to_delete_auto():
    # Подгружаем все старые виджеты и выбранную машину чтобы удалить
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global MAIN_DATA
    global selected_car
    global table_click_state

    if not selected_car:
        showerror(title="Ошибка", message="Выберите авто для удаления")
    else:
        table_click_state = []
        # Удаляем ключ из словаря
        with open('Data.json', 'r') as fp:
            data = json.load(fp)
        if MAIN_DATA != {}:
            _ = MAIN_DATA.pop(selected_car)
        _ = data.pop(selected_car)
        with open('Data.json', 'w') as fp:
            json.dump(data, fp)

        # Обновляем таблицу и удаляем выбранную машину
        label_list['text'] = 'Выберите номер авто:'
        selected_car = False

        # Обновляем окно изменения
        open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)

        return open_frame_list(CLEAN_ARRAY)


# Удаляет все авто, заново вызывает виджет таблицы
def to_delete_all():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global MAIN_DATA
    global selected_car
    global table_click_state
    result = askyesno(title="Удалить всё", message="Вы уверены, что хотите очистить список?")
    if result:
        if MAIN_DATA != {}:
            with open('Data.json', 'r') as fp:
                data = json.load(fp)
            for car in [car for car in data.keys()]:
                _ = MAIN_DATA.pop(car)
        with open('Data.json', 'w') as fp:
            json.dump({}, fp)
        label_list['text'] = 'Выберите номер авто:'
        selected_car = False
        table_click_state = []
        open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)
    else:
        showinfo("Удалить всё", "Операция отменена")
    return open_frame_list(CLEAN_ARRAY)


# Добавляет машину со всеми '-', проверяет не добавлено уже такой же, в таком случае выдаст ошибку
def to_add_auto():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global selected_car
    global label_list

    with open('Data.json', 'r') as fp:
        data = json.load(fp)

    # Проверка есть ли уже макет
    if '-' in data:
        showerror(title="Ошибка", message="Макет авто уже добавлен\nСмените имя модели или удалите его")
    else:
        # Ставим все хар-ки '-'
        data['-'] = {}
        for name in to_set_chars_sheet_only_names(data)[2:]:
            data['-'][name] = '-'

    # Загружаем новые данные
    with open('Data.json', 'w') as fp:
        json.dump(data, fp)

    # Убираем фокус с выбранной машины для избежания ошибок, обновляем фрейм ИЗМЕНИТЬ и лейбл в фрейме СПИСОК
    selected_car = False
    open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)
    label_list['text'] = 'Выберите номер авто:'

    return open_frame_list(CLEAN_ARRAY)


# Сохраняет в базу данных изменения характеристик, обновляет фрейм СПИСОК, ИЗМЕНИТЬ, если изменения были
def to_save_changes():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global MAIN_DATA
    global dynamic_entries_array, dynamic_checkbox_var_array
    global selected_car
    global label_list  # Чтобы изменить название выбранного авто на новое в фрейме СПИСОК

    with open('Data.json', 'r') as fp:
        data = json.load(fp)

    # С помощью метода get() забираем данные из виджетов и добавляем в value_list
    chars_list = to_set_chars_sheet_only_names(data)[1:]  # Убираем хар-ку "номер авто"
    values_list = []
    count_cheks = -1
    for entry in dynamic_entries_array:
        if str(type(entry)) == "<class 'tkinter.Checkbutton'>":
            count_cheks += 1
            values_list.append(dynamic_checkbox_var_array[count_cheks].get())
        else:
            values_list.append(entry.get())

    # Меняем данные в словаре, если менялось имя машины, то меняем в самом конце
    char_ind = 0  # хар-ки в chars_list
    empty_check = 0  # если будет равен кол-ву характеристик, то выйдет ошибка, что нет изменений
    for new_value in values_list[1:]:  # [1:] т.к. модель машины изменяем после цикла
        char_ind += 1
        if new_value != '':
            data[selected_car][chars_list[char_ind]] = new_value
        else:
            empty_check += 1

    # Механика смены модели авто
    if values_list[0] != '':
        if MAIN_DATA != {}:
            MAIN_DATA[values_list[0]] = MAIN_DATA[selected_car]
            _ = MAIN_DATA.pop(selected_car)
        data[values_list[0]] = data[selected_car]  # Дублируем значение в новый ключ
        _ = data.pop(selected_car)  # Удаляем пару старого ключ-значение

        selected_car = values_list[0]
        label_list['text'] = selected_car
    else:
        empty_check += 1

    # Проверка полностью пустого изменения
    if empty_check == len(chars_list):
        showerror(title="Ошибка", message="Поля для ввода новых значений пусты")
    else:
        with open('Data.json', 'w') as fp:
            json.dump(data, fp)
        open_frame_list(CLEAN_ARRAY)
        return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)


# Добавляет характеристику с именем из entry_change и значением '-'
def to_add_char():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global selected_car
    global entry_change

    with open('Data.json', 'r') as fp:
        data = json.load(fp)

    # Добавляем характеристику под названием из Entry
    name_char = entry_change.get()
    if name_char == '':
        showerror(title='Ошибка', message='Не введено название характеристики')
    elif name_char in data[selected_car]:
        showerror(title='Ошибка', message='Такая характеристика уже добавлена')
    else:
        data[selected_car][name_char] = '-'
        with open('Data.json', 'w') as fp:
            json.dump(data, fp)

        open_frame_list(CLEAN_ARRAY)
    return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)


# Удаляет введенную в entry_change характеристику
def to_delete_char():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global selected_car
    global entry_change

    with open('Data.json', 'r') as fp:
        data = json.load(fp)

    # Удаляет характеристику под названием из Entry
    name_char = entry_change.get()
    if name_char == '':
        showerror(title='Ошибка', message='Не введено название характеристики')
    elif name_char == 'Модель':
        showerror(title='Ошибка', message='Нельзя удалить модель авто')
    elif name_char not in [char for char in data[selected_car].keys()]:
        showerror(title='Ошибка', message='У данного авто нет такой характеристики')
    else:
        _ = data[selected_car].pop(name_char)
        with open('Data.json', 'w') as fp:
            json.dump(data, fp)

        open_frame_list(CLEAN_ARRAY)
    return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)


# Перехватывает закрытие окна поиска и меняет переменную
def finish():
    global search_tk
    global search_tk_check
    global button_change_add_char

    search_tk.destroy()
    search_tk_check = False

    # Если машина выбрана то возвращает возможность добавить хар-ку
    if selected_car:
        button_change_add_char['state'] = 'normal'


# Открывает мини-окно поиска
def open_search_tk():
    global search_tk_check
    global search_tk
    global entry_search_array
    global button_change_add_char
    # Проверка на открытое окно
    if search_tk_check:
        showerror(title='Ошибка', message='Окно поиска уже открыто')
    else:
        # Указываем что окно поиска теперь открыто
        search_tk_check = True

        # А возможность добавить новую хар-ку закрыта, потому что таблица уже будет сделана
        button_change_add_char['state'] = 'disabled'

        # Настройка окна
        search_tk = Tk()
        search_tk.title("Поиск")
        search_tk.geometry("300x300")
        search_tk.protocol("WM_DELETE_WINDOW", finish)

        # Кнопка найти
        start_search_button = Button(search_tk, text="Найти", command=to_start_search, width=32, font=("Arial", 12))
        start_search_button.pack()

        # Фрейм с таблицей
        search_tk_table = ttk.Frame(search_tk)
        search_tk_table.pack()

        with open('Data.json', 'r') as fp:
            data = json.load(fp)

        # Делаем таблицу лейбл - entry
        entry_search_array = []
        rows_count = 0
        for name in to_set_chars_sheet_only_names(data)[1:]:
            rows_count += 1

            Label(search_tk_table, text=name, font=("Arial", 12)).grid(row=rows_count, column=1)

            entry_search = Entry(search_tk_table, font=("Arial", 12))
            entry_search.grid(row=rows_count, column=2)
            entry_search_array.append(entry_search)


# Алгоритм поиска
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
                for element in [el.lower() for el in array_for_search[ind].split()]:
                    if element.lower() in car_values_list[ind].lower():
                        count += 1
                if count == len(array_for_search[ind].split()):
                    car_check_list.append(True)
                else:
                    car_check_list.append(False)
        if all(car_check_list):
            result_array.append(car)
    return result_array


# Запускает поиск, снимает фокус, основная база теперь только с теми машинами, что прошли поиск, старая база в буфере
# После кнопки ОТМЕНА старая база встаёт обратно на главную, применяя на себе те изменения что были с временной
def to_start_search():
    global search_tk, search_tk_check
    global button_list_search
    global selected_car
    global MAIN_DATA
    global button_list_add
    global entry_search_array
    global label_list
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global button_list_cancel

    button_list_cancel['state'] = 'normal'

    # Проверка введено ли хотя бы одно значение для поиска, если нет - ошибка
    entry_value_list = [entry.get() for entry in entry_search_array]
    if all(el == '' for el in entry_value_list):
        showerror(title='Ошибка', message='Данные для поиска не введены')
    else:
        # готовим аргумент для функции поиска, состоит из данных от Entry
        array_for_search = []
        for entry in entry_value_list:
            array_for_search.append(entry)

        new_cars_list = search_algorythm(array_for_search)
        # Проверяем нашлось ли что либо
        if new_cars_list != []:

            # Закрываем прошлое окно, убираем фокус, вырубаем кнопку поиска
            search_tk.destroy()
            button_list_search['state'] = 'disabled'
            button_list_add['state'] = 'disabled'
            label_list['text'] = 'Выберите номер авто:'
            search_tk_check = False
            selected_car = False

            with open('Data.json', 'r') as fp:
                MAIN_DATA = json.load(fp)
            # создаем новую базу данных и новый список машин с помощью алгоритма
            data = {}
            for car in new_cars_list:
                data[car] = MAIN_DATA[car]

            # Записываем в файл
            with open('Data.json', 'w') as fp:
                json.dump(data, fp)

            open_frame_list(CLEAN_ARRAY)
            return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)
        else:
            showerror(title='Ошибка', message='Ничего не найдено')


# Включает кнопку найти, кнопку добавить авто, характеристику, сбрасывает фокус и возвращает базу данных после поиска
def to_cancel_search():
    global CLEAN_ARRAY, CLEAN_ARRAY_CHANGE
    global MAIN_DATA
    global selected_car
    global button_list_add, button_list_search
    global button_list_cancel
    global table_click_state

    table_click_state = []
    button_list_cancel['state'] = 'disabled'

    # Включаем кнопки сбрасываем фокус
    button_list_add['state'] = 'normal'
    button_list_search['state'] = 'normal'
    selected_car = False

    # Возвращаем базу данных
    with open('Data.json', 'r') as fp:
        data = json.load(fp)
    # Дублируем значения ключей в старый массив, для обновления данных
    # Все остальные изменения (удалить, удалить все, сменить имя модели) было учтено на уровне тех функций
    for car in [car for car in data.keys()]:
        MAIN_DATA[car] = data[car]
    with open('Data.json', 'w') as fp:
        json.dump(MAIN_DATA, fp)
    MAIN_DATA = {}
    open_frame_list(CLEAN_ARRAY)
    return open_frame_change(CLEAN_ARRAY_CHANGE, selected_car)


# ----------------------------------------FRAME_LIST--------------------------------------------------------------

# .....................DYNAMIC WIDGETS...........................
# Принимает на вход список виджетов, которые надо очистить
def open_frame_list(CLEAN_ARRAY):
    global table_click_state

    TO_CLEAN_LAST_WIDGETS(CLEAN_ARRAY)
    # Создаём данные корректной формы для таблицы
    with open('Data.json', 'r') as fp:
        data = json.load(fp)
        columns_sheet = to_set_chars_sheet_only_names(data)
        chars_sheet = to_set_chars_sheets_with_value(data)
        columns_count = len(columns_sheet)

    # определяем столбцы
    table_list = ttk.Treeview(frame_list, columns=columns_sheet, show="headings")
    table_list.pack()
    CLEAN_ARRAY.append(table_list)

    # определяем заголовки столбцов
    for char in columns_sheet:
        table_list.heading(char, text=char, anchor='c')

    # добавляем данные
    for car_chars in chars_sheet:
        table_list.insert("", END, values=car_chars)

    style = ttk.Style()
    style.configure('Treeview', font=(None, 10))

    style2 = ttk.Style()
    style2.configure('Treeview.Heading', font=(None, 11))

    def item_selected(event):
        global table_click_state
        selected_row = ''
        for selected_item in table_list.selection():
            item = table_list.item(selected_item)
            row = item['values']
            # selected_row = f'{selected_row}{row}\n'
            selected_row = row
        table_click_state = [selected_row[0]]
        to_select_auto()

    table_list.bind('<<TreeviewSelect>>', item_selected)

    # Настройка столбцов (ДИЗАЙН)
    for i in range(1, columns_count + 1):
        table_list.column(f'#{i}', anchor='c', width=120, minwidth=80)
    return CLEAN_ARRAY


# ------------------------------------------------------------------------------------------------------------------

# Изначально размещаем стартовую таблицу с пустым мусорщиком (виджетов ранее не было)
CLEAN_ARRAY = open_frame_list([])

# //////////////////////////////////////////////////////////////////



# .....................STATIC WIDGETS...........................
# Указатель выбранной машины, изначально ничего (НЕИХУЯ) там нет
selected_car = False

# Указывает открыто ли окно поиска, для устранения дубляжей
search_tk_check = False

# Виджет Label для отображения текущего состояния Entry
label_list = Label(frame_list, text='Введите номер авто:', font=("Arial", 12))
label_list.pack()

# /////Фрейм для поля ввода и крестика//////////
frame_list_entry_cancel = ttk.Frame(frame_list)
frame_list_entry_cancel.pack()

# Виджет Entry и инструкции для валидации
check = (root.register(is_valid), "%P")
entry_list = Entry(frame_list_entry_cancel, validate="key", validatecommand=check, width=29, font=("Arial", 12))
entry_list.grid(row=1, column=1)

# Виджет Button в виде крестика, для отмены
button_list_cancel = Button(frame_list_entry_cancel, text='X', command=to_cancel_search, state='disabled', width=3,
                            height=1)
button_list_cancel.grid(row=1, column=2)
# /////////////////////////////////////////////

# ////Фрейм для кнопки ВЫБРАТЬ и ПОИСК, УДАЛИТЬ и УДАЛИТЬ ВСЁ, ДОБАВИТЬ АВТО////////
frame_list_select_search = ttk.Frame(frame_list)
frame_list_select_search.pack()

# РЕАЛИЗАЦИЯ КНОПКИ "ВЫБРАТЬ" (выбирается авто на которое будет работать вкладка ИЗМЕНИТЬ, а также кнопка "УДАЛИТЬ")
button_list_choose = Button(frame_list_select_search, text="Выбрать", command=to_select_auto, width=15,
                            font=("Arial", 12))
button_list_choose.grid(row=1, column=1)

# РЕАЛИЗАЦИЯ КНОПКИ "ПОИСК" (меняет базу данных, делает ток из нужных машин, отмена крестиком)
button_list_search = Button(frame_list_select_search, text='Поиск', command=open_search_tk, width=15,
                            font=("Arial", 12))
button_list_search.grid(row=1, column=2)

# РЕАЛИЗАЦИЯ КНОПКИ "УДАЛИТЬ" (удаляет выбранное авто)
button_list_delete = Button(frame_list_select_search, text="Удалить", command=to_delete_auto, width=15,
                            font=("Arial", 12))
button_list_delete.grid(row=2, column=1)

# РЕАЛИЗАЦИЯ КНОПКИ "УДАЛИТЬ ВСЁ" (удаляет все машины)
button_list_delete_all = Button(frame_list_select_search, text="Удалить всё", command=to_delete_all, width=15,
                                font=("Arial", 12))
button_list_delete_all.grid(row=2, column=2)

# РЕАЛИЗАЦИЯ КНОПКИ "ДОБАВИТЬ АВТО" (добавляет авто со всеми "-")
button_list_add = Button(frame_list_select_search, text="Добавить авто", command=to_add_auto, width=32,
                         font=("Arial", 12))
button_list_add.grid(row=3, columnspan=2, column=1)

# --------------------------------------------FRAME_CHANGE--------------------------------------------------------
# ..................STATIC WIDGETS..................

# Фрейм для позиционирования кнопок
frame_change_position = ttk.Frame(frame_change)
frame_change_position.pack()

label_change = Label(frame_change_position, text='Выберите авто для изменения', font=("Arial", 12))
label_change.grid(row=1, columnspan=2, column=1)

button_change = Button(frame_change_position, text='Сохранить изменения', state='disabled', command=to_save_changes,
                       width=43, font=("Arial", 12))
button_change.grid(row=2, columnspan=2, column=1)

Label(frame_change_position).grid(row=3)

entry_change = Entry(frame_change_position, font=("Arial", 12), width=43)
entry_change.grid(row=4, columnspan=2, column=1)

button_change_add_char = Button(frame_change_position, text='Добавить характеристику', command=to_add_char,
                                font=("Arial", 12))
button_change_add_char.grid(row=5, column=1)

button_change_delete_char = Button(frame_change_position, text='Удалить характеристику', command=to_delete_char,
                                   font=("Arial", 12))
button_change_delete_char.grid(row=5, column=2)

# Для хранения Entry виджетов, для метода get()
dynamic_entries_array = []
dynamic_checkbox_var_array = []


# ..................DYNAMIC WIDGETS..................
# Принимает на вход список виджетов, которые надо очистить, выбранное авто
def open_frame_change(CLEAN_ARRAY_CHANGE, selected_car):
    TO_CLEAN_LAST_WIDGETS(CLEAN_ARRAY_CHANGE)
    global dynamic_entries_array
    global dynamic_checkbox_var_array

    if not selected_car:
        # Если машина не выбрана приводим все в обычное состояние
        label_change['text'] = 'Выберите авто для изменений'
        button_change['state'] = 'disabled'
        button_change_add_char['state'] = 'disabled'
        button_change_delete_char['state'] = 'disabled'
    else:
        # Делаем кнопку доступной и лейбл - имя авто
        label_change['text'] = selected_car
        button_change['state'] = 'normal'
        if search_tk_check:  # Если окно поиска открыто то добавлять хар-ку нельзя
            button_change_add_char['state'] = 'disabled'
        else:
            button_change_add_char['state'] = 'normal'
        button_change_delete_char['state'] = 'normal'

        # ----------------------Таблица-----------------------------
        # -------(Через Label, Так легче позиционировать Entry)-----

        # делаем отдельный родительский контейнер, чтобы в нем использовать не pack(), а grid() и не получить ошибки
        table_change = ttk.Frame(frame_change, borderwidth=1, relief=SOLID)
        table_change.pack()
        CLEAN_ARRAY_CHANGE.append(table_change)

        # Портируем данные
        with open('Data.json', 'r') as fp:
            data = json.load(fp)

        # Счетчик строки
        row_count = 0

        # Массив Entry виджетов для того чтобы делать get()
        dynamic_entries_array = []
        dynamic_checkbox_var_array = []

        # Размещаем данные по-строчно вместе с Entry
        for char, value in to_set_pair_char_value(data, selected_car):
            row_count += 1

            # Labels
            label_table_change_char = Label(table_change, text=char, font=("Arial", 12))
            label_table_change_value = Label(table_change, text=value, font=("Arial", 12))
            label_table_change_decorative = Label(table_change, text='||', font=("Arial", 12))

            label_table_change_char.grid(row=row_count, column=1)
            label_table_change_value.grid(row=row_count, column=3)
            label_table_change_decorative.grid(row=row_count, column=2)

            CLEAN_ARRAY_CHANGE.append(label_table_change_char)
            CLEAN_ARRAY_CHANGE.append(label_table_change_value)
            CLEAN_ARRAY_CHANGE.append(label_table_change_decorative)

            # Entries
            if char in ['Фары', 'Багажник']:
                checkbox_var = IntVar()
                checkbox_change_dynamic = Checkbutton(table_change, variable=checkbox_var)
                checkbox_change_dynamic.grid(row=row_count, column=4)
                if value == 1:
                    checkbox_change_dynamic['state'] = 'active'
                else:
                    checkbox_change_dynamic['state'] = 'normal'

                CLEAN_ARRAY_CHANGE.append(checkbox_change_dynamic)
                dynamic_entries_array.append(checkbox_change_dynamic)
                dynamic_checkbox_var_array.append(checkbox_var)

            else:
                entry_change_dynamic = Entry(table_change, font=("Arial", 12))
                entry_change_dynamic.grid(row=row_count, column=4)
                if char in char_blacklist:
                    entry_change_dynamic['state'] = 'disabled'

                CLEAN_ARRAY_CHANGE.append(entry_change_dynamic)
                dynamic_entries_array.append(entry_change_dynamic)
    return CLEAN_ARRAY_CHANGE


# ------------------------------------------------------------------------------------------------------------------

CLEAN_ARRAY_CHANGE = open_frame_change([], selected_car)

root.mainloop()
