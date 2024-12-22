"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль отвечает за прорисовку и конфигурацию окна расчета режимов глубокой
гравировки.

Модуль содержит класс и его подкласс:
- ChildPowerSet - Класс-родитель конфигурации окна расчетов режимов глубокой
 гравировки.
    > DepthSettingsWindow - Подкласс конфигурации дочернего окна с
    настройками параметров глубокой гравировки для различных материалов.
"""


import tkinter as tk
from tkinter.messagebox import showerror,  askokcancel
from tkinter import ttk


from app_logger import AppLogger
from binds import BindEntry, BalloonTips
from calculations import DeepEngraving
from path_getting import PathName
from settings_configuration import DepthSet


class ChildPowerSet(tk.Toplevel):
    """
    Класс конфигурации дочернего окна расчета режимов глубокой гравировки.

    Содержит методы: update_combo_data, depth_calculation,
    run_child_settings, dynamic_update_combo, add_binds, add_tips,
    grab_focus, destroy_child.

    Пример использования:
    child_window = ChildPowerSet(parent, width, height, theme, icon=logo_path)
    child_window.grab_focus()
    """
    def __init__(self, parent, width: int, height: int, theme: str,
                 title: str = 'Глубокая гравировка',
                 resizable: tuple = (False, False),
                 icon: str | None = None) -> None:
        """
        Конфигурация и прорисовка дочернего окна расчета режимов глубокой
        гравировки.
        :param parent: Класс-родитель
        :param width: Ширина окна
        :param height: Высота окна
        :param theme: Тема окна (приложения)
        :param title: Название окна
        :param resizable: Изменяемость окна. По умолчанию: (False, False)
        :param icon: Иконка окна. По умолчанию: None
        """
        # Инициализация окна
        super().__init__(parent)
        AppLogger(
            'ChildPowerSet',
            'info',
            f'Открытие дочернего окна расчетов глубокой гравировки'
        )

        # Конфигурация окна
        self.title(title)
        self.geometry(f"{width}x{height}+20+20")
        self.resizable(resizable[0], resizable[1])
        if icon:
            self.iconbitmap(PathName.resource_path(icon))

        # Установка стиля окна
        self.style_child = ttk.Style(self)
        self.style_child.theme_use(theme)
        self.theme = theme

        # Конфигурация отзывчивости окна
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=2)

        # Создание переменных
        self.not_use = None
        self.combo_list = list()

        # Создание форм окна
        self.widget_panel = ttk.Frame(self, padding=0)
        self.widget_panel.grid(row=0, column=0, padx=0, pady=(0, 0),
                               sticky="nsew")
        self.info_panel = ttk.LabelFrame(
            self, text="Режимы гравировки и комментарии.",
            padding=(0, 0, 0, 0), height=180)
        self.info_panel.grid(row=1, column=0, padx=15, pady=(10, 10),
                             sticky="nsew")
        # Отключаем динамическое изменение размера формы
        self.info_panel.grid_propagate(False)

        # Конфигурация отзывчивости форм
        self.widget_panel.columnconfigure(index=0, weight=1)
        self.widget_panel.columnconfigure(index=1, weight=1)
        self.widget_panel.columnconfigure(index=2, weight=1)
        self.widget_panel.rowconfigure(index=0, weight=1)
        self.widget_panel.rowconfigure(index=1, weight=1)
        self.widget_panel.rowconfigure(index=2, weight=1)

        self.info_panel.columnconfigure(index=0, weight=5)
        self.info_panel.columnconfigure(index=1, weight=1)
        self.info_panel.columnconfigure(index=2, weight=1)
        self.info_panel.rowconfigure(index=0, weight=1)
        self.info_panel.rowconfigure(index=1, weight=3)

        # Упаковка виджетов блока ввода и выбора данных
        # Список материалов для выбора
        self.update_combo_data()
        self.cmb_depths = ttk.Combobox(
            self.widget_panel,
            values=self.combo_list,
            takefocus=False
        )
        self.cmb_depths.current(0)
        self.cmb_depths.grid(
            row=0, column=0, padx=15, pady=10, columnspan=3, sticky='nsew'
        )

        # Окно ввода глубины гравировки
        ttk.Label(self.widget_panel, text="Глубина гравировки, мм").grid(
            row=1, column=0, padx=20, pady=10, sticky='nsew'
        )
        self.ent_depth = ttk.Entry(self.widget_panel,
                                   width=50, takefocus=False)
        self.ent_depth.grid(row=1, column=1, padx=(0, 15), pady=10,
                            sticky='nsew', columnspan=2)

        # Кнопка запуска расчетов
        self.btn_depth_of_engraving = ttk.Button(
            self.widget_panel,
            text="Выполнить расчет",
            command=self.depth_calculation
        )
        self.btn_depth_of_engraving.grid(
            row=2, column=0, padx=(15, 15), pady=10,
            sticky='nsew', columnspan=2
        )

        # Кнопка запуска окна настройки материалов для глубокой гравировки
        self.btn_settings = ttk.Button(
            self.widget_panel,
            text="Настройка параметров",
            command=self.run_child_settings
        )
        self.btn_settings.grid(
            row=2, column=2, padx=(0, 15), pady=10, sticky='nsew')

        # Упаковка виджетов вывода результатов и комментариев
        # Комментарии к режимам гравировки
        ttk.Label(self.info_panel,
                  text=f"Расчеты выполнены для\n"
                       f"оборудования LaserBee.\n\n"
                       f"Параметры гравировки:\n"
                       f"Детализация: 40 лин/мм;\n"
                       f"Режимы: (95/900/30);\n"
                       f"Оптимизация: двунаправленная.",
                  foreground='#1E1F22',
                  font="Arial 12",
                  justify='center'
                  ).grid(row=0, column=2, padx=(20, 10), pady=10,
                         sticky='nsew', rowspan=2)
        # Разделительная линия
        ttk.Separator(self.info_panel, orient="vertical").grid(
            row=0, column=1, padx=0, pady=(0, 10), sticky='ns', rowspan=2)

        # Результаты расчета
        self.lbl_result_comment = ttk.Label(
            self.info_panel,
            text=f"Основной комментарий",
            font='Arial 13',
            foreground='dark red'
            )
        self.lbl_result_comment.grid(row=0, column=0, padx=5, pady=5,
                                     sticky='ns')

        self.lbl_result_power = ttk.Label(
            self.info_panel,
            text=f"Рекомендуемый алгоритм гравировки",
            font='Arial 13',
            foreground='#217346'
        )
        self.lbl_result_power.grid(row=1, column=0, padx=5, pady=(5, 10),
                                   sticky='n')

        # Установка подсказок и фонового текста
        self.add_binds()
        self.add_tips()

    def update_combo_data(self) -> None:
        """
        Метод добавления/обновления данных для выпадающего списка.
        """
        # Создание локально переменной конфигурации
        temp_config = DepthSet()
        # Добавление данных из переменной конфигурации в список
        self.combo_list = temp_config.get_materials_list()

    def depth_calculation(self) -> None:
        """
        Метод расчета количества проходов для глубокой гравировки.
        """
        try:
            # Считывание данных с интерфейса
            depth = float(self.ent_depth.get())
            name = self.cmb_depths.get()

            # Получаем переменную конфигурации
            temp_config = DeepEngraving(material_name=name)

            # Получаем результаты расчетов
            result_comment, result_power, powers = temp_config.depth_calculate(
                depth=depth)
        except (TypeError, ValueError) as e:
            AppLogger(
                'ChildPowerSet.depth_calculation',
                'error',
                f'При считывании глубины гравировки возникло исключение '
                f'{e}. Данные введены некорректно!',
                info=True
            )
            showerror(
                'Ошибка считывания данных',
                'Глубина гравировки введена некорректно!'
            )

            # Обнуляем данные результатов
            self.lbl_result_comment.config(
                text=f"Основной комментарий"
            )
            self.lbl_result_power.config(
                text=f"Рекомендуемый алгоритм гравировки"
            )

            # Обнуляем данные интерфейса
            self.ent_depth.delete(0, tk.END)
            self.add_binds()
            self.update_combo_data()
            self.cmb_depths.current(0)

        except (KeyError, FileNotFoundError) as e:
            AppLogger(
                'ChildPowerSet.depth_calculation',
                'error',
                f'При считывании выбранного материала возникло исключение '
                f'{e}. Такого материала нет в базе, либо отсутствует сам '
                f'файл базы!',
                info=True
            )
            showerror(
                'Ошибка считывания данных',
                'Такого материала нет в базе,\n либо отсутствует сам файл '
                'базы!'
            )

            # Обнуляем данные результатов
            self.lbl_result_comment.config(
                text=f"Основной комментарий"
            )
            self.lbl_result_power.config(
                text=f"Рекомендуемый алгоритм гравировки"
            )

            # Обнуляем данные интерфейса
            self.ent_depth.delete(0, tk.END)
            self.add_binds()
            self.update_combo_data()
            self.cmb_depths.current(0)

        else:
            if len(powers) == 0:  # Если гравировка без смены фокуса
                self.lbl_result_comment.config(
                    text=result_comment
                )
                self.lbl_result_power.config(
                    text=f"Рекомендуемый алгоритм гравировки:\n{'-'*56}\n"
                         f"Гравировка выполняется в одну установку,\n"
                         f"количество проходов: {result_power:.0f} шт."
                )
                # Запись расчетов в лог
                AppLogger(
                    'ChildPowerSet.depth_calculation',
                    'info',
                    f"Произведен расчет глубокой гравировки."
                )
            else:  # Если требуется смена фокуса
                self.lbl_result_comment.config(
                    text=result_comment
                )
                self.lbl_result_power.config(
                    text=f"Рекомендуемый алгоритм гравировки:\n{'-'*50}\n"
                         f"{powers[0]:.0f} цикла(ов):\n"
                         f"  - {powers[1]:.0f} проходов;\n"
                         f"  - Смена фокуса на {powers[2]} вниз.\n"
                         f"В конце добавляем"
                         f" еще {powers[3]} проходов(а).\n{'-'*50}\n"
                         f"ИТОГО ПРОХОДОВ: {result_power:.0f} шт."
                )
                # Запись расчетов в лог
                AppLogger(
                    'ChildPowerSet.depth_calculation',
                    'info',
                    f"Произведен расчет глубокой гравировки."
                )

    def run_child_settings(self) -> None:
        """
        Метод открытия дочернего окна с настройками параметров глубокой
        гравировки.
        """
        try:
            # Запуск дочернего окно
            settings_window = DepthSettingsWindow(
                self,
                800,
                400,
                theme=self.theme,
                icon=PathName.resource_path("resources\\Company_logo.ico")
            )
            settings_window.grab_focus()
        except Exception as e:
            AppLogger(
                'ChildPowerSet.run_child_settings',
                'error',
                f"При открытии окна настройки параметров глубокой"
                f" гравировки возникло исключение {e}",
                info=True
            )

    def dynamic_update_combo(self, event=None) -> None:
        """
        Метод обновления файла конфигурации со списком материалов при
        фокусировке в выпадающий список (обновление после изменения настроек).
        """
        # Обновление данных
        self.update_combo_data()
        self.cmb_depths.configure(values=self.combo_list)

        self.not_use = event
        self.cmb_depths.update()

    def add_binds(self) -> None:
        """
        Установка фонового текста в полях ввода и связывание действий
        пользователя в интерфейсе приложения с командами.
        """
        BindEntry(self.ent_depth, text="Глубина гравировки, мм")
        self.bind('<FocusIn>', self.dynamic_update_combo)

        # Расчет при нажатии на Enter
        self.bind('<Return>', self.return_by_keyboard)

    def return_by_keyboard(self, event=None) -> None:
        """
        Выполнение расчетов при нажатии Return (клавиша Enter)
        :param event: Нажатие клавиши Enter а клавиатуре
        """
        self.depth_calculation()
        self.not_use = event

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса.
        """
        BalloonTips(self.cmb_depths,
                    text=f"Выберите материал, для которого\n"
                         f"планируете выполнить расчет.")
        BalloonTips(self.ent_depth,
                    text="Глубина гравировки, мм")

    def grab_focus(self) -> None:
        """
        Метод сохранения фокуса на дочернем окне
        """
        self.grab_set()
        self.focus_set()
        self.wait_window()

    def destroy_child(self) -> None:
        """
        Метод закрытия (разрушения) дочернего окна
        """
        self.destroy()


class DepthSettingsWindow(tk.Toplevel):
    """
    Подкласс конфигурации дочернего окна с настройками списка материалов и
    параметров глубокой гравировки.

    Содержит методы: update_table_data, click_add_element,
    click_delete_element, click_reset_depths, add_binds, add_bind_treeview,
    add_tips, grab_focus, destroy_child.

    Пример использования:
    child_window = DepthSettingsWindow(parent, width, height, theme,
                                       icon=logo_path)
    child_window.grab_focus()
    """
    def __init__(self, parent, width: int, height: int, theme: str,
                 title: str = 'Параметры глубокой гравировки',
                 resizable: tuple = (False, False),
                 icon: str | None = None) -> None:
        """
        Конфигурация и прорисовка дочернего окна настройки списка материалов
        и параметров глубокой гравировки.
        :param parent: Класс-родитель
        :param width: Ширина окна
        :param height: Высота окна
        :param theme: Тема окна (приложения)
        :param title: Название окна
        :param resizable: Изменяемость окна. По умолчанию: (False, False)
        :param icon: Иконка окна. По умолчанию: None
        """
        super().__init__(parent)

        AppLogger(
            'DepthSettingsWindow',
            'info',
            f'Открытие дочернего окна настройки параметров глубокой гравировки'
        )

        # Конфигурация окна
        self.title(title)
        self.geometry(f"{width}x{height}+50+50")
        self.resizable(resizable[0], resizable[1])
        if icon:
            self.iconbitmap(PathName.resource_path(icon))

        # Установка стиля окна
        self.style_child = ttk.Style(self)
        self.style_child.theme_use(theme)

        # Конфигурация отзывчивости окна
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=50)
        self.columnconfigure(index=2, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=2)

        # Конфигурация форм вкладки
        self.panel_table = ttk.Frame(
            self, padding=(0, 0, 0, 0))
        self.panel_table.grid(row=0, column=0, padx=0, pady=(0, 0),
                              sticky="nsew")
        self.panel_widgets = ttk.Frame(
            self, padding=(0, 0, 0, 0))
        self.panel_widgets.grid(row=1, column=0, padx=0, pady=(0, 0),
                                sticky="nsew", columnspan=3)

        # Конфигурация отзывчивости форм
        self.panel_widgets.columnconfigure(index=0, weight=1)
        self.panel_widgets.columnconfigure(index=1, weight=1)
        self.panel_widgets.columnconfigure(index=2, weight=1)
        self.panel_widgets.columnconfigure(index=3, weight=1)
        self.panel_widgets.rowconfigure(index=0, weight=1)
        self.panel_widgets.rowconfigure(index=1, weight=1)
        self.panel_widgets.rowconfigure(index=2, weight=1)

        # Создание переменных
        self.depth_settings = DepthSet()
        self.not_use = None

        # ___ Создание виджетов ___
        # Создание и конфигурация таблицы
        tree_scroll = ttk.Scrollbar(self)
        tree_scroll.grid(row=0, column=2, padx=0, pady=0,
                         sticky="nsew")
        self.depth_table = ttk.Treeview(
            self,
            selectmode="extended",
            yscrollcommand=tree_scroll.set,
            height=7,
            columns=('#1', '#2', '#3'),
            show="headings"
        )
        self.depth_table.column(0, width=300, anchor="w")
        self.depth_table.column(1, width=200, anchor="center")
        self.depth_table.column(2, width=200, anchor="center")

        self.depth_table.heading(0, text="Название материала", anchor="center")
        self.depth_table.heading(1, text="Шаг глубины, мм",
                                 anchor="center")
        self.depth_table.heading(2, text="Количество проходов, шт",
                                 anchor="center")
        self.depth_table.selection()
        self.depth_table.configure(yscrollcommand=tree_scroll.set)

        # Упаковка таблицы
        self.depth_table.grid(
            row=0, column=1, padx=0, pady=0, sticky="nsew"
        )

        # Добавление данных в таблицу
        self.update_table_data()

        # Окно ввода __ Название материала __
        self.ent_name = ttk.Entry(
            self.panel_widgets,
            width=10,
            takefocus=False
        )
        self.ent_name.grid(row=0, column=0, padx=5, pady=(5, 10),
                           sticky='nsew', columnspan=1)

        # Окно ввода __ Шаг глубины __
        self.ent_depth = ttk.Entry(
            self.panel_widgets,
            width=10,
            takefocus=False
        )
        self.ent_depth.grid(row=0, column=1, padx=5, pady=(5, 10),
                            sticky='nsew')

        # Окно ввода __ Количество проходов на шаг __
        self.ent_power = ttk.Entry(
            self.panel_widgets,
            width=10,
            takefocus=False
        )
        self.ent_power.grid(row=0, column=2, padx=5, pady=(5, 10),
                            sticky='nsew')

        # Создание кнопки добавления работы
        self.btn_add_new_element = ttk.Button(
            self.panel_widgets,
            width=10,
            text="Добавить/изменить элемент",
            command=self.click_add_element
        )
        self.btn_add_new_element.grid(
            row=0, column=3, padx=5, pady=(5, 10), sticky='nsew', columnspan=1)

        # Разделительная черта
        ttk.Separator(self.panel_widgets).grid(
            row=1, column=0, columnspan=4, pady=5, sticky='ew'
        )
        # Создание кнопки удаления материала
        self.btn_delete_element = ttk.Button(
            self.panel_widgets,
            width=10,
            text="Удалить элемент из таблицы",
            command=self.click_delete_element
        )
        self.btn_delete_element.grid(
            row=2, column=0, padx=5, pady=(10, 20), sticky='nsew',
            columnspan=3)

        # Создание кнопки сброса списка по-умолчанию
        self.btn_reset_depths = ttk.Button(
            self.panel_widgets,
            width=10,
            text='Сброс параметров',
            command=self.click_reset_depths
        )
        self.btn_reset_depths.grid(
            row=2, column=3, padx=5, pady=(10, 20), sticky='nsew')

        # Устанавливаем фоновый текст и подсказки
        self.add_binds()
        self.add_tips()

    def update_table_data(self) -> None:
        """
        Метод обновления/добавления данных в таблицу параметров глубокой
        гравировки.
        """
        # Очистка таблицы
        self.depth_table.delete(*self.depth_table.get_children())
        # Создание переменной данных для таблицы
        table_data = list()
        try:
            # Считывание информации из конфига
            depths = self.depth_settings.config['MAIN']
            for k, v in depths.items():
                temp_depth, temp_power = v.split(', ')
                temp = [k, temp_depth, temp_power]
                table_data.append(temp)
            for data in table_data:
                self.depth_table.insert('', index='end', values=data)

            del depths
        except Exception as e:
            AppLogger(
                'DepthSettingsWindow.update_table_data',
                'error',
                f'При получении данных из файла "deep_engraving.ini" '
                f'для заполнения таблицы параметров глубокой гравировки '
                f'вызвано исключение {e}',
                info=True
            )

    def click_add_element(self) -> None:
        """
        Метод добавления нового либо изменения существующего элемента в таблицу
        """
        # Создание локальной переменной конфигурации
        add_temp_config = self.depth_settings.config

        try:
            # Считываем данные из полей ввода
            name = self.ent_name.get()
            depth = float(self.ent_depth.get())
            power = int(self.ent_power.get())

            # Добавляем элемент в переменную конфигурации
            add_temp_config['MAIN'][name] = f"{depth}, {power}"

            AppLogger(
                'DepthSettingsWindow.click_add_element',
                'info',
                f"В таблицу параметров глубокой гравировки был добавлен "
                f"новый элемент: {name}: {depth}, {power}"
            )

            # Обнуляем данные в полях ввода
            self.ent_name.delete(0, tk.END)
            self.ent_depth.delete(0, tk.END)
            self.ent_power.delete(0, tk.END)
            self.add_binds()
        except (ValueError, KeyError) as e:
            tk.messagebox.showerror(
                'Ошибка добавления',
                'Параметры материала введены некорректно!'
            )
            AppLogger(
                'DepthSettingsWindow.click_add_element',
                'error',
                f"При добавлении/изменении элемента в таблицу параметров "
                f"глубокой гравировки было вызвано исключение: {e}",
                info=True
            )

        # Добавляем данные в файл конфигурации и обновляем переменную
        self.depth_settings.update_settings(some_new=add_temp_config)
        self.depth_settings = DepthSet()

        # Обновляем данные в таблице
        self.update_table_data()

    def click_delete_element(self) -> None:
        """
        Метод удаления выделенной в таблице строки.
        """
        # Создаем локальную переменную конфигурации
        temp_config_with_deleted_item = self.depth_settings.config

        try:
            # Считывание данных выделенной в таблице строки
            deleted_item = self.depth_table.item(self.depth_table.focus())
            if askokcancel('Удаление элемента',
                           f'Вы действительно хотите удалить:\n'
                           f'"{str(deleted_item["values"][0])}"'):
                # Удаление элемента
                temp_config_with_deleted_item.remove_option(
                    'MAIN', str(deleted_item['values'][0]))
                # Обновление данных в файле
                self.depth_settings.update_settings(
                    some_new=temp_config_with_deleted_item)
                # Обновление переменной конфигурации
                self.depth_settings = DepthSet()
                AppLogger(
                    'DepthSettingsWindow.click_delete_element',
                    'info',
                    f'Элемент "{str(deleted_item["values"][0])}"'
                    f' был удален из списка параметров глубокой гравировки.'
                )
        except (ValueError, KeyboardInterrupt, IndexError) as e:
            tk.messagebox.showerror(
                'Ошибка удаления!',
                'Выберите в таблице удаляемую строку.'
            )
            AppLogger(
                'DepthSettingsWindow.click_delete_element',
                'error',
                f'При удалении элемента из списка параметров глубокой'
                f' гравировки было вызвано исключение {e}: - Элемент не был '
                f'выбран в таблице, или такого элемента не существует в '
                f'списке.',
                info=True
            )

        # Обновление данных в таблице
        self.update_table_data()

        del temp_config_with_deleted_item

    def click_reset_depths(self) -> None:
        """
        Метод сброса параметров глубокой гравировки до настроек "По-умолчанию".
        """
        if askokcancel('Сброс параметров глубокой гравировки',
                       'Вы действительно хотите сбросить параметры '
                       'глубокой гравировки "По-умолчанию"?'):
            # Производим сброс параметров
            self.depth_settings.default_settings()

            # Переопределяем переменную конфигурации после сброса
            self.depth_settings = DepthSet()

            # Обновляем данные в таблице и полях ввода
            self.update_table_data()
            self.ent_name.delete(0, tk.END)
            self.ent_depth.delete(0, tk.END)
            self.ent_power.delete(0, tk.END)
            self.add_binds()

            AppLogger(
                'DepthSettingsWindow.click_reset_depths',
                'info',
                f'Параметры глубокой гравировки были сброшены до настроек '
                f'"По-умолчанию"'
            )

    def add_binds(self) -> None:
        """
        Установка фонового текста в полях ввода и связывание действий
        пользователя в интерфейсе приложения с командами.
        """
        BindEntry(self.ent_name, text=f"Название материала")
        BindEntry(self.ent_depth, text=f"Шаг глубины, мм")
        BindEntry(self.ent_power, text=f"Количество проходов, шт")

        self.depth_table.bind('<Button-1>', self.add_bind_treeview)

    def add_bind_treeview(self, event=None) -> None:
        """
        Метод, реализующий заполнение полей ввода названия работы и ее
        стоимости при выделении строки в таблице (считывание строки из
        таблицы).
        :param event: Считывает выделение пользователем строки в таблице
        """
        try:  # Проверка на то, что пользователь выбрал материал
            data = self.depth_table.item(
                self.depth_table.focus())
            self.ent_name.delete(0, tk.END)
            self.ent_depth.delete(0, tk.END)
            self.ent_power.delete(0, tk.END)
            BindEntry(self.ent_name, text=str(data["values"][0]))
            BindEntry(self.ent_depth, text=str(data["values"][1]))
            BindEntry(self.ent_power, text=str(data["values"][2]))
        except (ValueError, KeyboardInterrupt, IndexError):
            self.ent_name.delete(0, tk.END)
            self.ent_depth.delete(0, tk.END)
            self.ent_power.delete(0, tk.END)
            self.add_binds()
        self.not_use = event

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса.
        """
        BalloonTips(self.ent_name,
                    text="Введите название материала.\n"
                         "Выделите двойным нажатием строку в таблице,\n"
                         "чтобы редактировать существующий материал.")
        BalloonTips(self.ent_depth,
                    text="Введите шаг глубины для материала,\n"
                         "при котором требуется смена фокуса, мм")
        BalloonTips(self.ent_power,
                    text="Введите количество проходов,\n"
                         "для достижения глубины шага, шт")
        BalloonTips(self.btn_delete_element,
                    text="Для удаления элемента выделите строку в таблице.")
        BalloonTips(self.btn_reset_depths,
                    text='Сброс настроек до параметров "По-умолчанию"')

    def grab_focus(self) -> None:
        """
        Метод сохранения фокуса на дочернем окне
        """
        self.grab_set()
        self.focus_set()
        self.wait_window()

    def destroy_child(self) -> None:
        """
        Метод закрытия (разрушения) дочернего окна
        """
        self.destroy()
