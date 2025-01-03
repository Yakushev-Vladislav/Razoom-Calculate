"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль отвечает за прорисовку и конфигурацию окна настройки списка листового
материала и окна стоимостей изделий.

Модуль содержит класс и его подкласс:
- ChildMaterials - Класс-родитель конфигурации окна настройки списка
листового материала.
    > ChildMatrixMaterial - Подкласс конфигурации дочернего окна с таблицей
    стоимостей изделий из выбранного пользователем материала.
"""


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import askokcancel

from app_logger import AppLogger
from binds import BindEntry
from binds import BalloonTips
from materials import Materials, Interpolation
from path_getting import PathName


class ChildMaterials(tk.Toplevel):
    """
    Класс конфигурации дочернего окна настроек писка листового материала.

    Содержит методы: reset_entries_data, get_data_child, click_add_material,
    click_del_material, click_reset_materials, grab_focus,
    run_matrix_window, add_binds, material_table_bind, add_tips, destroy_child.

    Пример использования:
    child_window = ChildMaterials(parent, width, height, theme, icon=logo_path)
    child_window.grab_focus()
    """
    def __init__(self, parent, width: int, height: int, theme: str,
                 title: str = 'Листовой материал',
                 resizable: tuple = (False, False), icon: str | None = None):
        """
        Конфигурация и прорисовка дочернего окна редактирования списка
        листового материала.
        :param parent: Класс родительского окна
        :param width: Ширина окна
        :param height: Высота окна
        :param theme: Тема, используемая в родительском классе
        :param title: Название окна
        :param resizable: Изменяемость окна. По умолчанию: (False, False)
        :param icon: Иконка окна. По умолчанию: None
        """
        # Создание дочернего окна поверх основного
        super().__init__(parent)
        AppLogger(
            'ChildMaterials',
            'info',
            f'Открытие дочернего окна редактирования базы листового материала.'
        )
        self.title(title)
        self.geometry(f"{width}x{height}+20+20")
        self.resizable(resizable[0], resizable[1])
        if icon:
            self.iconbitmap(PathName.resource_path(icon))

        # Создание переменной - ссылки на родителя
        self.parent = parent

        # Установка стиля окна
        self.style_child = ttk.Style(self)
        self.style_child.theme_use(theme)

        # Создание переменной, хранящей массив данных для таблицы
        self.data = []

        # Создание переменной конфигурации
        self.config_material_data = Materials()

        # Создание переменной для отслеживания событий
        self.not_use = None

        # Конфигурация отзывчивости окна
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=50)
        self.columnconfigure(index=2, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=2)

        # Создание формы для основных виджетов
        self.panel_settings = ttk.Frame(self, padding=(0, 0, 0, 0))
        self.panel_settings.grid(row=1, column=0, padx=0, pady=(0, 0),
                                 sticky="nsew", columnspan=3)
        # Конфигурация формы виджетов
        self.panel_settings.columnconfigure(index=0, weight=1)
        self.panel_settings.columnconfigure(index=1, weight=1)
        self.panel_settings.columnconfigure(index=2, weight=1)
        self.panel_settings.columnconfigure(index=3, weight=1)
        self.panel_settings.columnconfigure(index=4, weight=1)

        self.panel_settings.rowconfigure(index=0, weight=1)
        self.panel_settings.rowconfigure(index=1, weight=1)
        self.panel_settings.rowconfigure(index=2, weight=1)
        self.panel_settings.rowconfigure(index=3, weight=1)
        self.panel_settings.rowconfigure(index=4, weight=1)
        self.panel_settings.rowconfigure(index=5, weight=1)

        # Создание и конфигурация таблицы
        tree_scroll = ttk.Scrollbar(self)
        tree_scroll.grid(row=0, column=2, padx=0, pady=0,
                         sticky="nsew")
        self.material_table = ttk.Treeview(
            self,
            selectmode="extended",
            yscrollcommand=tree_scroll.set,
            height=8,
            columns=('#0', '#1', '#2', '#3'),
            show="headings"
        )
        self.material_table.column(0, width=195, anchor="w")
        self.material_table.column(1, width=100, anchor="center")
        self.material_table.column(2, width=100, anchor="center")
        self.material_table.column(3, width=100, anchor="center")

        self.material_table.heading(0, text="Материал", anchor="center")
        self.material_table.heading(1, text="Ширина, мм", anchor="center")
        self.material_table.heading(2, text="Высота, мм", anchor="center")
        self.material_table.heading(3, text="Стоимость, руб.",
                                    anchor="center")
        self.material_table.selection()
        self.material_table.configure(yscrollcommand=tree_scroll.set)

        # Упаковка таблицы
        self.material_table.grid(
            row=0, column=1, padx=0, pady=0, sticky="nsew"
        )

        # Добавление данных в таблицу
        self.get_data_child()

        # Окно ввода -Названия материала-
        self.ent_name_mat = ttk.Entry(
            self.panel_settings,
            width=18
        )
        self.ent_name_mat.grid(row=0, column=0, padx=10, pady=15,
                               sticky='nsew', rowspan=2)

        # Окно ввода -Ширина листа-
        self.ent_width_mat = ttk.Entry(
            self.panel_settings,
            width=18
        )
        self.ent_width_mat.grid(row=0, column=1, padx=10, pady=15,
                                sticky='nsew', rowspan=2)

        # Окно ввода -Высота листа-
        self.ent_height_mat = ttk.Entry(
            self.panel_settings,
            width=18
        )
        self.ent_height_mat.grid(row=0, column=2, padx=10, pady=15,
                                 sticky='nsew', rowspan=2)

        # Окно ввода -Стоимость материала-
        self.ent_price_mat = ttk.Entry(
            self.panel_settings,
            width=18
        )
        self.ent_price_mat.grid(row=0, column=3, padx=10, pady=15,
                                sticky='nsew', rowspan=2)

        # Кнопка добавления материала в таблицу
        self.btn_add = ttk.Button(
            self.panel_settings,
            width=4,
            text="Добавить/редактировать материал",
            command=self.click_add_material
        )
        self.btn_add.grid(row=2, column=0, padx=10, pady=15, sticky='nsew',
                          columnspan=4)

        # Форма с переключателем типа лазера и ее конфигурация
        self.panel_laser_type = ttk.Frame(self.panel_settings, padding=0)
        self.panel_laser_type.grid(row=0, column=4, padx=0, pady=(0, 0),
                                   sticky="nsew", rowspan=2)
        self.panel_laser_type.rowconfigure(index=0, weight=1)
        self.panel_laser_type.rowconfigure(index=1, weight=1)

        # Создание и упаковка переключателей типа лазера
        self.rb_laser_type = tk.IntVar(value=1)

        self.rbt_solid = ttk.Radiobutton(
            self.panel_laser_type,
            text="Диодный лазер",
            variable=self.rb_laser_type,
            value=1
        )
        self.rbt_solid.grid(row=0, column=0, padx=15, pady=(5, 0),
                            sticky="nsew")
        self.rbt_co2 = ttk.Radiobutton(
            self.panel_laser_type,
            text="Газовый лазер",
            variable=self.rb_laser_type,
            value=2
        )
        self.rbt_co2.grid(row=1, column=0, padx=15, pady=(5, 0),
                          sticky="nsew")

        # Разделительная черта
        ttk.Separator(self.panel_settings).grid(
            row=3, column=0, columnspan=5, pady=(5, 0), sticky='ew'
        )

        # Кнопка удаления выбранного материала из таблицы
        self.btn_del = ttk.Button(
            self.panel_settings,
            width=3,
            text="Удалить выбранный материал",
            command=self.click_del_material
        )
        self.btn_del.grid(
            row=5, column=0, padx=10, pady=15, sticky='nsew',
            columnspan=2)

        # Кнопка сброса таблицы "по умолчанию"
        self.btn_get_default = ttk.Button(
            self.panel_settings,
            text="Сброс",
            command=self.click_reset_materials
        )
        self.btn_get_default.grid(
            row=2, column=4, padx=(0, 10), pady=15, sticky='nsew')

        # Кнопка открытия дочернего окна с матрицей стоимостей
        self.btn_matrix_run = ttk.Button(
            self.panel_settings,
            text="Редактировать таблицу стоимостей",
            command=self.run_matrix_window
        )
        self.btn_matrix_run.grid(
            row=5, column=2, padx=(10, 10), pady=15, sticky='nsew',
            columnspan=2)

        # Кнопка закрытия окна
        self.btn_destroy = ttk.Button(
            self.panel_settings,
            text="Выход",
            command=self.destroy_child
        )
        self.btn_destroy.grid(
            row=5, column=4, padx=(0, 10), pady=15, sticky='nsew')

        # Устанавливаем подсказки и фоновый текст
        self.add_binds()
        self.add_tips()

    def get_data_child(self) -> None:
        """
        Метод, обеспечивающий заполнение таблицы данными.
        """
        try:
            # Получаем данные из файла конфигурации
            self.data = list()
            temp_data = self.config_material_data.material_config['MAIN']
            for k, v in temp_data.items():
                temp = [k]
                temp.extend([x for x in v.split(',')])
                self.data.append(temp)

            # Заполняем данными таблицу
            for data in self.data:
                self.material_table.insert('', index='end', values=data)

            # Удаляем временные переменные
            del temp_data, temp

        except KeyError as e:
            AppLogger(
                'ChildMaterials.get_data_child',
                'error',
                f'При добавлении данных в таблицу возникло исключение: "'
                f'{e}": файл конфигурации пуст или отсутствуют данные '
                f'раздела [MAIN]',
                info=True
            )

    def click_add_material(self) -> None:
        """
        Метод, реализующий добавление в таблицу элемента из
        пользовательского интерфейса.
        """
        # Создаем временную переменную конфигурации
        temp_new = self.config_material_data.material_config
        # Считывание данных из полей ввода
        new_name = self.ent_name_mat.get()
        new_width = self.ent_width_mat.get()
        new_height = self.ent_height_mat.get()
        new_price = self.ent_price_mat.get()
        type_of_laser = 'solid' if self.rb_laser_type.get() == 1 else 'gas'

        # Если поля не заполнены - вызов сообщения об ошибке
        if (new_name == '' or new_width == '' or new_height == '' or
                new_price == ''):
            tk.messagebox.showerror('Ошибка записи', 'Данные пусты')
            AppLogger(
                'ChildMaterials.click_add_material',
                'error',
                f'Ошибка добавлении элемента в таблицу "Листовой материал": '
                f'Данные не введены!'
            )

        # Если введенные данные не подходят под формат
        elif (new_width.isdigit() is False) or (
                new_height.isdigit() is False) or (
                new_price.isdigit() is False) or (
                new_name == 'Материал'
        ):
            tk.messagebox.showerror(
                'Ошибка записи',
                'Введите данные'
            )
            AppLogger(
                'ChildMaterials.click_add_material',
                'error',
                f'Ошибка добавлении элемента в таблицу "Листовой материал": '
                f'Данные введены некорректно: ('
                f'{new_name, new_width, new_height, new_price}).'
            )

        # Иначе запись в файл
        else:
            # Записываем новые данные в файл конфигурации
            temp_new['MAIN'][new_name] = (f'{new_width}, {new_height},'
                                          f' {new_price}, {type_of_laser}')
            self.config_material_data.update_materials(some_new=temp_new)

            # Создание матрицы стоимостей
            self.config_material_data.add_matrix_file(new_name, type_of_laser)

            # Обновление данных в таблице
            # Очистка таблицы
            for item in self.material_table.get_children():
                self.material_table.delete(item)

            # Запись новых данных в таблицу
            self.get_data_child()

            # Очистка и установка фонового текста в полях ввода
            self.reset_entries_data()

            self.update()
            AppLogger(
                'ChildMaterials.click_add_material',
                'info',
                f'Добавлен новый элемент в таблицу "Листовой материал":'
                f' {new_name}.'
            )

    def click_del_material(self) -> None:
        """
        Метод удаления выделенного в таблице материала (выделенной
        пользователем строки).
        """
        # Создание временной переменной конфигурации
        deleted_data_config = self.config_material_data.material_config

        try:  # Проверка на то, что пользователь выбрал материал
            deleted_data = self.material_table.item(
                self.material_table.focus())
            material_name = str(deleted_data["values"][0])

            # Удаление выбранного элемента
            if askokcancel('Удаление элемента',
                           f'Вы действительно хотите удалить:\n'
                           f'"{material_name}"'):
                deleted_data_config.remove_option(
                    'MAIN', material_name)

                # Обновление данных в файле конфигурации
                self.config_material_data.update_materials(
                    some_new=deleted_data_config)

                # Удаление файла с матрицей стоимостей
                self.config_material_data.del_matrix_file(material_name)

                AppLogger(
                    'ChildMaterials.click_del_material',
                    'info',
                    f'Удаление элемента "{material_name}" из списка '
                    f'листового материала.'
                )

        except (ValueError, KeyboardInterrupt, IndexError) as e:
            tk.messagebox.showerror(
                'Ошибка удаления!',
                'Выберите в таблице удаляемую строку.'
            )
            AppLogger(
                'ChildMaterials.click_del_data',
                'error',
                f'При удалении элемента из списка листового материала было '
                f'вызвано исключение "{e}" - Элемент не выбран или '
                f'отсутствует в списке.'
            )
        # Обновление данных в таблице
        # Очистка таблицы
        for item in self.material_table.get_children():
            self.material_table.delete(item)

        # Запись новых данных в таблицу
        self.get_data_child()

        # Сбрасываем поля ввода
        self.reset_entries_data()

        del deleted_data_config

    def click_reset_materials(self) -> None:
        """
        Метод сброса базы материала до настроек "по-умолчанию". После сброса
        реализуется обновление данных в таблице.
        """
        if askokcancel('Сброс настроек', 'Вы действительно хотите сбросить '
                                         'настройки по умолчанию?'):
            self.config_material_data.get_default()
            AppLogger(
                'ChildMaterials.get_default_materials',
                'info',
                f'База листового материала была сброшена до настроек '
                f'"По-умолчанию".'
            )

        # Переопределение переменной конфигурации
        del self.config_material_data
        self.config_material_data = Materials()
        # Обновление данных в таблице
        # Очистка таблицы
        for item in self.material_table.get_children():
            self.material_table.delete(item)

        # Запись новых данных в таблицу
        self.get_data_child()

        # Сбрасываем данные в полях ввода
        self.reset_entries_data()

    def run_matrix_window(self) -> None:
        """
        Метод открытия дочернего окна с таблицей (матрицей) стоимостей изделий
        для выбранного листового материала.
        """
        # Считывание название материала
        try:
            matrix_material_name = self.material_table.item(
                    self.material_table.focus())['values'][0]
            matrix_child = ChildMatrixMaterial(
                self,
                830,
                310,
                theme='forest-light',
                icon=PathName.resource_path("resources\\Company_logo.ico"),
                material_name=matrix_material_name
            )
            matrix_child.grab_focus()

        except (ValueError, KeyboardInterrupt, IndexError):
            tk.messagebox.showerror(
                'Ошибка конфигурирования!',
                'Выберите в таблице строку.'
            )

    def reset_entries_data(self) -> None:
        """
        Метод удаления текста из полей ввода и установка фонового текста.
        """
        # Сбрасываем поля ввода
        self.ent_name_mat.delete(0, tk.END)
        self.ent_width_mat.delete(0, tk.END)
        self.ent_height_mat.delete(0, tk.END)
        self.ent_price_mat.delete(0, tk.END)
        self.add_binds()

    def add_binds(self) -> None:
        """
        Установка фонового текста в полях ввода и связывание действий
        пользователя в интерфейсе приложения с командами.
        """

        # Получение выделенного в таблице материала
        self.material_table.bind('<Button-1>', self.material_table_bind)

        # Установка фонового текста в полях ввода
        BindEntry(self.ent_name_mat, text='Материал')
        BindEntry(self.ent_width_mat, text='Ширина, мм')
        BindEntry(self.ent_height_mat, text='Высота, мм')
        BindEntry(self.ent_price_mat, text='Цена, руб')

    def material_table_bind(self, event=None) -> None:
        """
        Метод, реализующий заполнение полей ввода названия материала и его
        параметров (ширина, высота, стоимость) при выделении строки в таблице
        (считывание строки из таблицы).
        :param event: Считывает выделение пользователем строки в таблице
        """
        try:  # Проверка на то, что пользователь выбрал материал
            data = self.material_table.item(
                self.material_table.focus())
            material_name = str(data["values"][0])
            material_width = str(data["values"][1])
            material_height = str(data["values"][2])
            material_cost = str(data["values"][3])

            self.ent_name_mat.delete(0, tk.END)
            BindEntry(self.ent_name_mat, text=material_name)
            self.ent_width_mat.delete(0, tk.END)
            BindEntry(self.ent_width_mat, text=material_width)
            self.ent_height_mat.delete(0, tk.END)
            BindEntry(self.ent_height_mat, text=material_height)
            self.ent_price_mat.delete(0, tk.END)
            BindEntry(self.ent_price_mat, text=material_cost)
        except (ValueError, KeyboardInterrupt, IndexError):
            self.reset_entries_data()
        self.not_use = event

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса.
        """
        # Установка подсказок
        BalloonTips(self.ent_name_mat,
                    text=f'Название материала.\n\n'
                         f'Выделите двойным нажатием строку в таблице,\n'
                         f'чтобы редактировать существующий материал.')
        BalloonTips(self.ent_width_mat, text='Ширина, мм')
        BalloonTips(self.ent_height_mat, text='Высота, мм')
        BalloonTips(self.ent_price_mat, text='Цена, руб')
        BalloonTips(self.btn_del,
                    text=f'Для удаления выделите строку в таблице.')
        BalloonTips(self.btn_matrix_run,
                    text=f'Для редактирования выделите строку в таблице.')
        BalloonTips(self.btn_get_default, text='Сброс настроек '
                                               '"по-умолчанию".')

    def grab_focus(self) -> None:
        """
        Метод захвата фокуса на дочернем окне.
        """
        self.grab_set()
        self.focus_set()
        self.wait_window()

    def destroy_child(self) -> None:
        """
        Метод, реализующий разрушение (закрытие) окна.
        """
        self.destroy()


class ChildMatrixMaterial(tk.Toplevel):
    """
    Класс конфигурации и прорисовки дочернего окна с таблицей стоимостей
    изделий из выбранного материала.

    Класс содержит методы: draw_widgets, draw_solid_widget, draw_gas_widget,
    add_entries_data, click_save_matrix, click_reset_matrix, grab_focus,
    destroy_child.

    Пример использования:
    matrix_child = ChildMatrixMaterial(parent, width, height, theme,
    icon=logo_path)
    """
    def __init__(self, parent, width: int, height: int, theme: str,
                 material_name: str | None = None,
                 title: str = f'Матрица стоимостей материала',
                 resizable: tuple = (False, False),
                 icon: str | None = None) -> None:
        """
        Конфигурация и прорисовка дочернего окна с таблицей стоимостей
        изделий из выбранного материала.

        :param parent: Родительское окно (Листовой материал);
        :param width: Ширина окна;
        :param height: Высота окна;
        :param theme: Тема окна;
        :param material_name: Наименование материала;
        :param title: Название окна;
        :param resizable: Возможность растягивания окна;
        :param icon: Иконка окна;
        """
        # Создание дочернего окна поверх основного
        super().__init__(parent)
        AppLogger(
            'ChildMatrixMaterial',
            'info',
            f'Открытие дочернего окна редактирования стоимости выбранного '
            f'листового материала: {material_name}.'
        )
        if material_name:
            title = f'Матрица стоимостей материала "{material_name}"'
            self.title(title)
        else:
            self.title(title)
        self.geometry(f"{width}x{height}+50+150")
        self.resizable(resizable[0], resizable[1])
        if icon:
            self.iconbitmap(PathName.resource_path(icon))

        # Установка стиля окна
        self.style_child = ttk.Style(self)
        self.style_child.theme_use(theme)

        # Создание основной переменной конфигурации для выбранного материала
        self.config_matrix_cost = Interpolation(material_name)
        self.string_name_list = list()

        # Название материала
        self.material_name = material_name

        # Создание основных виджетов окна (полей ввода)
        # Создаем матрицу полей ввода
        self.matrix_entries = list()

        # ___Нулевая строка "Мелкие"___
        self.ent_tiny_one = ttk.Entry(self, width=10)
        self.ent_tiny_five = ttk.Entry(self, width=10)
        self.ent_tiny_fifteen = ttk.Entry(self, width=10)
        self.ent_tiny_fifty = ttk.Entry(self, width=10)
        self.ent_tiny_one_hundred_fifty = ttk.Entry(self, width=10)
        self.ent_tiny_five_hundred = ttk.Entry(self, width=10)
        self.ent_tiny_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.tiny_entries = [self.ent_tiny_one,
                             self.ent_tiny_five,
                             self.ent_tiny_fifteen,
                             self.ent_tiny_fifty,
                             self.ent_tiny_one_hundred_fifty,
                             self.ent_tiny_five_hundred,
                             self.ent_tiny_one_thousand]

        self.matrix_entries.append(self.tiny_entries)

        # ___Первая строка "Маленькие"___
        self.ent_little_one = ttk.Entry(self, width=10)
        self.ent_little_five = ttk.Entry(self, width=10)
        self.ent_little_fifteen = ttk.Entry(self, width=10)
        self.ent_little_fifty = ttk.Entry(self, width=10)
        self.ent_little_one_hundred_fifty = ttk.Entry(self,
                                                      width=10)
        self.ent_little_five_hundred = ttk.Entry(self, width=10)
        self.ent_little_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.little_entries = [self.ent_little_one,
                               self.ent_little_five,
                               self.ent_little_fifteen,
                               self.ent_little_fifty,
                               self.ent_little_one_hundred_fifty,
                               self.ent_little_five_hundred,
                               self.ent_little_one_thousand]

        self.matrix_entries.append(self.little_entries)

        # ___Вторая строка "Средние"___
        self.ent_middle_one = ttk.Entry(self, width=10)
        self.ent_middle_five = ttk.Entry(self, width=10)
        self.ent_middle_fifteen = ttk.Entry(self, width=10)
        self.ent_middle_fifty = ttk.Entry(self, width=10)
        self.ent_middle_one_hundred_fifty = ttk.Entry(self,
                                                      width=10)
        self.ent_middle_five_hundred = ttk.Entry(self, width=10)
        self.ent_middle_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.middle_entries = [self.ent_middle_one,
                               self.ent_middle_five,
                               self.ent_middle_fifteen,
                               self.ent_middle_fifty,
                               self.ent_middle_one_hundred_fifty,
                               self.ent_middle_five_hundred,
                               self.ent_middle_one_thousand]

        self.matrix_entries.append(self.middle_entries)

        # ___Третья строка "Большие"___
        self.ent_big_one = ttk.Entry(self, width=10)
        self.ent_big_five = ttk.Entry(self, width=10)
        self.ent_big_fifteen = ttk.Entry(self, width=10)
        self.ent_big_fifty = ttk.Entry(self, width=10)
        self.ent_big_one_hundred_fifty = ttk.Entry(self, width=10)
        self.ent_big_five_hundred = ttk.Entry(self, width=10)
        self.ent_big_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.big_entries = [self.ent_big_one,
                            self.ent_big_five,
                            self.ent_big_fifteen,
                            self.ent_big_fifty,
                            self.ent_big_one_hundred_fifty,
                            self.ent_big_five_hundred,
                            self.ent_big_one_thousand]

        self.matrix_entries.append(self.big_entries)

        # ___Четвертая (пятая для СО2) строка "Негабаритные (Огромные)"___
        self.ent_oversize_one = ttk.Entry(self, width=10)
        self.ent_oversize_five = ttk.Entry(self, width=10)
        self.ent_oversize_fifteen = ttk.Entry(self, width=10)
        self.ent_oversize_fifty = ttk.Entry(self, width=10)
        self.ent_oversize_one_hundred_fifty = ttk.Entry(self,
                                                        width=10)
        self.ent_oversize_five_hundred = ttk.Entry(self, width=10)
        self.ent_oversize_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.oversize_entries = [self.ent_oversize_one,
                                 self.ent_oversize_five,
                                 self.ent_oversize_fifteen,
                                 self.ent_oversize_fifty,
                                 self.ent_oversize_one_hundred_fifty,
                                 self.ent_oversize_five_hundred,
                                 self.ent_oversize_one_thousand]

        self.matrix_entries.append(self.oversize_entries)

        # ___Строка "Очень большие" для СО2___
        self.ent_very_big_one = ttk.Entry(self, width=10)
        self.ent_very_big_five = ttk.Entry(self, width=10)
        self.ent_very_big_fifteen = ttk.Entry(self, width=10)
        self.ent_very_big_fifty = ttk.Entry(self, width=10)
        self.ent_very_big_one_hundred_fifty = ttk.Entry(self,
                                                        width=10)
        self.ent_very_big_five_hundred = ttk.Entry(self, width=10)
        self.ent_very_big_one_thousand = ttk.Entry(self, width=10)

        # Добавляем поля в список для дальнейшего удобного пользования
        self.very_big_entries = [self.ent_very_big_one,
                                 self.ent_very_big_five,
                                 self.ent_very_big_fifteen,
                                 self.ent_very_big_fifty,
                                 self.ent_very_big_one_hundred_fifty,
                                 self.ent_very_big_five_hundred,
                                 self.ent_very_big_one_thousand]

        self.matrix_entries.append(self.very_big_entries)

        # Кнопка сохранения результатов
        self.btn_save = ttk.Button(
            self,
            width=4,
            text="Сохранить",
            command=self.click_save_matrix
        )
        # Кнопка сброса изменений
        self.btn_reset = ttk.Button(
            self,
            width=4,
            text="Сброс",
            command=self.click_reset_matrix
        )
        # Прорисовка интерфейса окна (виджетов)
        self.draw_widgets()

        # Запись данных в поля ввода
        self.add_entries_data()

    def draw_widgets(self) -> None:
        """
        Метод прорисовки основных виджетов окна с учетом типа оборудования.
        """
        # Если твердотельное оборудование
        if self.config_matrix_cost.get_laser_type() == 'solid':
            self.draw_solid_widget()
        else:  # Иначе - газовое оборудование
            self.draw_gas_widget()

        # Упаковка формы
        self.grid()

        # Упаковка виджетов
        # Подписи столбцов
        volume_list = [1, 5, 15, 50, 150, 500, 1000]
        for i in range(7):
            ttk.Label(self, text=f'{volume_list[i]} шт').grid(
                row=0, column=(i+1), padx=0, pady=(15, 0), sticky='ns'
            )
        # Подписи строк
        ttk.Label(self, text='Мелкие (10х10мм):').grid(
            row=1, column=0, padx=10, pady=0, sticky='nsew'
        )
        ttk.Label(self, text='Маленькие (50х30мм):').grid(
            row=2, column=0, padx=10, pady=0, sticky='nsew'
        )
        ttk.Label(self, text='Средние (100х50мм):').grid(
            row=3, column=0, padx=10, pady=0, sticky='nsew'
        )
        ttk.Label(self, text='Большие (200х150мм):').grid(
            row=4, column=0, padx=10, pady=0, sticky='nsew'
        )

        # Поля ввода
        # Нулевая строка "Мелкие"___
        for i in range(7):
            self.tiny_entries[i].grid(
                row=1, column=(i + 1), padx=2, pady=2, sticky='ns'
            )
        self.ent_tiny_one_thousand.grid(
            row=1, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        # ___Первая строка "Маленькие"___
        for i in range(7):
            self.little_entries[i].grid(
                row=2, column=(i+1), padx=2, pady=2, sticky='ns'
            )
        self.ent_little_one_thousand.grid(
            row=2, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        # ___Вторая строка "Средние"___
        for i in range(7):
            self.middle_entries[i].grid(
                row=3, column=(i + 1), padx=2, pady=2, sticky='ns'
            )
        self.ent_middle_one_thousand.grid(
            row=3, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        # ___Третья строка "Большие"___
        for i in range(7):
            self.big_entries[i].grid(
                row=4, column=(i + 1), padx=2, pady=2, sticky='ns'
            )
        self.ent_big_one_thousand.grid(
            row=4, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        # ___Четвертая строка "Негабаритные"___
        for i in range(7):
            self.oversize_entries[i].grid(
                row=5, column=(i + 1), padx=2, pady=2, sticky='ns'
            )
        self.ent_oversize_one_thousand.grid(
            row=5, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        BalloonTips(self.btn_reset, text='Сброс настроек "по-умолчанию".')

    def draw_solid_widget(self) -> None:
        """
        Метод прорисовки виджетов для твердотельного лазера.
        """
        # Конфигурация формы
        for i in range(8):
            self.columnconfigure(index=i, weight=1)
        for j in range(7):
            self.rowconfigure(index=j, weight=1)

        # Подписи данных (строк)
        ttk.Label(self, text='Негабаритные (300х200мм):').grid(
            row=5, column=0, padx=10, pady=0, sticky='nsew'
        )

        # Кнопки
        self.btn_save.grid(
            row=6, column=1, padx=(2, 10), pady=10, sticky='nsew', columnspan=7
        )

        self.btn_reset.grid(
            row=6, column=0, padx=10, pady=10, sticky='nsew', columnspan=1
        )

    def draw_gas_widget(self) -> None:
        """
        Метод прорисовки виджетов для газового лазера.
        """
        # Конфигурация формы
        for i in range(8):
            self.columnconfigure(index=i, weight=1)
        for j in range(8):
            self.rowconfigure(index=j, weight=1)

        # Подписи данных (строк)
        ttk.Label(self,
                  text='Очень большие (300х250мм):').grid(
            row=5, column=0, padx=10, pady=0, sticky='nsew'
        )
        ttk.Label(self,
                  text='Огромные (600х400мм):').grid(
            row=6, column=0, padx=10, pady=0, sticky='nsew'
        )

        # ___Пятая строка "Огромные"___
        for i in range(7):
            self.very_big_entries[i].grid(
                row=6, column=(i + 1), padx=2, pady=2, sticky='ns'
            )
        self.ent_very_big_one_thousand.grid(
            row=6, column=7, padx=(2, 10), pady=2, sticky='nsew'
        )

        # Кнопки
        self.btn_save.grid(
            row=7, column=1, padx=(2, 10), pady=10, sticky='nsew',
            columnspan=7
        )

        self.btn_reset.grid(
            row=7, column=0, padx=10, pady=10, sticky='nsew', columnspan=1
        )

    def add_entries_data(self) -> None:
        """
        Метод записи данных в поля ввода. Данные берутся из
        соответствующего файла конфигурации для выбранного материала.
        """
        # Создание временной локальной переменной конфигурации
        temp_config = self.config_matrix_cost.matrix_config['COSTS']

        # Создание списка названий строк
        self.string_name_list = list()
        for key in temp_config.keys():
            self.string_name_list.append(key)

        try:
            # Записываем данные в поля ввода
            for i in range(len(self.string_name_list)):
                temp_string = [float(x) for x in temp_config[
                    self.string_name_list[i]].split(', ')]
                for j in range(len(temp_string)):
                    self.matrix_entries[i][j].delete(0, tk.END)
                    self.matrix_entries[i][j].insert(
                        0, f'{temp_string[j]:.0f}')
        except (ValueError, KeyError, TypeError, FileNotFoundError) as e:
            AppLogger(
                'ChildMatrixMaterial.add_entries_data',
                'error',
                f'При считывание данных о стоимости материала '
                f'{self.string_name_list} возникло исключение: {e}',
                info=True
            )

    def click_save_matrix(self) -> None:
        """
        Метод сохранения изменений в файле конфигурации.
        """
        # Создание локальной переменной конфига
        temp_config = self.config_matrix_cost.matrix_config

        try:
            if askokcancel('Сохранение',
                           'Сохранить матрицу стоимостей?'):
                # Считывание данных
                for i in range(len(self.string_name_list)):
                    temp_string = list()
                    for item in self.matrix_entries[i]:
                        temp_string.append(str(int(item.get())))
                    temp_config['COSTS'][self.string_name_list[i]] =\
                        ', '.join(temp_string)
                AppLogger(
                    'ChildMatrixMaterial.click_save_matrix',
                    'info',
                    f'Сохранение изменений в матрице стоимостей материала:'
                    f' "{self.material_name}"'
                )

            # Запись новых данных в файл
            self.config_matrix_cost.update_matrix(some_new=temp_config)

        except (ValueError, TypeError) as e:
            tk.messagebox.showerror(
                'Ошибка сохранения',
                'Данные введены некорректно.'
            )
            AppLogger(
                'ChildMatrixMaterial.click_save_matrix',
                'error',
                f'При сохранении изменений в матрице стоимостей материала:'
                f' "{self.material_name}" вызвано исключение "{e}"',
                info=True
            )
            # Обновляем данные в полях ввода
            self.add_entries_data()

    def click_reset_matrix(self) -> None:
        """
        Метод сброса настроек "по-умолчанию"
        """
        if askokcancel('Сброс',
                       'Сбросить матрицу стоимостей?'):
            # Создание локальной переменной конфига
            self.config_matrix_cost.get_default()
            self.config_matrix_cost = Interpolation(self.material_name)

            # Обновляем данные в полях ввода
            self.add_entries_data()
            AppLogger(
                'ChildMatrixMaterial.click_reset_matrix',
                'info',
                f'Сброс матрицы стоимостей материала:'
                f' "{self.material_name}" до настроек "По-умолчанию".'
            )

        else:
            pass

    def grab_focus(self) -> None:
        """
        Метод сохранения фокуса на дочернем окне.
        """
        self.grab_set()
        self.focus_set()
        self.wait_window()

    def destroy_child(self) -> None:
        """
        Метод закрытия (разрушения) дочернего окна.
        """
        self.destroy()
