"""
Copyright (c) 2024 Yakushev Vladislav

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________

Razoom-laser - аn application for automating cost calculations and some other
parameters in the work of the operator of the "Razoom" company.

Основной скрипт запуска программы.

Содержит класс:
- App - основной класс конфигурации программы. Отвечает за прорисовку
главного окна приложения.

Подклассы (не прямые наследники):
    > AppMenu - класс конфигурации основной полосы меню приложения;

    > PersonalCalculateTab - класс конфигурации первой вкладки главного окна
    "Частные лица";

    > SheetMaterialsTab - класс конфигурации второй вкладки главного окна
    "Листовой материал";

    > IndustrialCalculateTab - класс конфигурации третьей вкладки главного окна
    "Промышленный расчет".

Пример использования (запуска):
window = App()
window.run()

Для стилизации интерфейса приложения была взята библиотека Forest-ttk-theme
(https://github.com/rdbende/Forest-ttk-theme).
Для работы с всплывающими подсказками использована библиотека Custom-Tooltip
(https://github.com/jessielw/Custom-Tkinter-Tooltip).

"""

import os
from math import ceil
from textwrap import wrap

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import askokcancel

from app_logger import AppLogger
from binds import BindEntry
from binds import BalloonTips
from bmp_read import MonochromeBMP
from calculations import RatioArea
from child_config_window import ChildConfigSet, ConfigSet, StandardSet
from child_materials_window import ChildMaterials
from child_power_set_window import ChildPowerSet
from materials import Materials, Interpolation, ContainerPacking
from path_getting import PathName
from resources_links import OpenUrl


class App(tk.Tk):
    """
    Основной класс конфигурации главного окна приложения. Связывает класс
    конфигурации полосы меню приложения, а также классы конфигурации вкладок
    главного окна.

    Содержит методы: round_result, add_binds, add_tips,
    get_return_by_keyboard, run, destroy_window.

    """
    def __init__(self):
        """
        Конфигурация главного окна приложения.
        """

        # Создание основного окна и его конфигурация
        super().__init__()
        self.title("Razoom-Calculate")
        self.option_add("*tearOff", False)
        self.iconbitmap(
            PathName.resource_path("resources\\Company_logo.ico")
        )
        self.resizable(True, True)

        # Минимальные размеры окна и расположение
        self.geometry(f"{1000}x{750}+10+10")
        self.minsize(1000, 750)
        self.geometry("%dx%d" % (self.winfo_width(),
                                 self.winfo_height()))

        # Создание стиля и его конфигурация
        self.style = ttk.Style(self)
        self.theme = 'forest-light'
        self.tk.call("source", PathName.resource_path(
            "resources\\forest-light.tcl"))
        self.style.theme_use(self.theme)

        # Стилизуем текст кнопки основного расчета
        self.style.configure('my.TButton', font='Arial 13',)

        # Переменная для bind методов
        self.not_use = None

        # Переменные основных настроек (конфигурации) программы
        self.main_settings = ConfigSet().config
        self.standard_works = StandardSet().config

        # Создание основных вкладок
        self.tabs_control = ttk.Notebook(self)
        self.tab_personal_calculate = PersonalCalculateTab(
            self.tabs_control,
            self.round_result,
            self.destroy_window,
            (self.main_settings, self.standard_works))
        self.tab_sheet_material = SheetMaterialsTab(
            self.tabs_control,
            self.round_result)
        self.tab_industrial_calculator = IndustrialCalculateTab(
            self.tabs_control,
            self.round_result,
            self.main_settings)

        # Добавление вкладок в набор
        self.tabs_control.add(self.tab_personal_calculate,
                              text='Частные лица')
        self.tabs_control.add(self.tab_sheet_material,
                              text='Листовой материал')
        self.tabs_control.add(self.tab_industrial_calculator,
                              text='Промышленный расчёт')
        # Упаковка вкладок
        self.tabs_control.pack(fill='both', expand=True)

        # Создание ползунка изменения размера
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.place(relx=0.972, rely=0.965)

        # Создаем меню и упаковываем (прорисовываем
        self.app_menu = AppMenu(self,
                                self.theme,
                                self.destroy_window,
                                self.tab_personal_calculate.settings_update,
                                )

    @staticmethod
    def round_result(cost: int | float) -> int:
        """
        Метод округления результатов с учетом получившейся суммы.
        :param cost: Число, передаваемое для округления.
        :return: Округленное число
        """
        if cost >= 800:
            return int(round(cost/50) * 50)
        elif 250 <= cost < 800:
            return int(round(cost/10) * 10)
        elif 85 <= cost < 250:
            return int(round(cost/5) * 5)
        else:
            return int(cost)

    def add_binds(self) -> None:
        """
        Установка фонового текста в полях ввода главного окна и связывание
        действий пользователя в интерфейсе приложения с командами (расчет
        от клавиши Enter/Return).
        """
        # Расчет стоимости при нажатии на Enter в главном окне (1 и 2 вкладки)
        self.bind('<Return>', self.return_by_keyboard)

        # Обновление списка дополнительных ресурсов
        self.app_menu.add_binds()

        # Установка фонового текста в поля ввода
        self.tab_industrial_calculator.add_binds()
        self.tab_personal_calculate.add_binds()
        self.tab_sheet_material.add_binds()

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса.
        """
        self.tab_industrial_calculator.add_tips()
        self.tab_personal_calculate.add_tips()
        self.tab_sheet_material.add_tips()

    def return_by_keyboard(self, event=None) -> None:
        """
        Выполнение расчетов при нажатии Return (клавиша Enter)
        :param event: Нажатие клавиши Enter а клавиатуре
        """
        # Расчет на первой вкладке
        if self.tabs_control.tabs().index(self.tabs_control.select()) == 0:
            self.tab_personal_calculate.main_calculation()
        # Расчет на второй вкладке
        elif self.tabs_control.tabs().index(self.tabs_control.select()) == 1:
            self.tab_sheet_material.material_calculation()

        self.not_use = event

    def run(self) -> None:
        """
        Запуск приложения.
        """
        # Прорисовка виджетов и окна
        self.add_binds()
        self.add_tips()
        self.mainloop()

    def destroy_window(self) -> None:
        """
        Разрушение окна (закрытие приложения).
        """
        if askokcancel('Выход', 'Вы действительно хотите выйти?'):
            self.destroy()


class AppMenu(tk.Menu):
    """
    Класс, отвечающий за конфигурацию основной полосы меню приложения.
    Также класс связывает главное окно программы с дочерними окнами:
    - предварительной настройки программы;
    - настройки списка листового материала с параметрами;
    - расчетов глубокой гравировки.

    Содержит методы: draw_menu, update_url_set, run_child_materials,
    run_child_power, run_child_settings, open_resource, get_url_menu_data,
    open_guide, open_help, add_binds, watch_log.
    """
    def __init__(self, parent, theme: str, destroy_method,
                 update_method) -> None:
        """
        Метод инициализации и прорисовки полосы меню.
        :param parent: Класс - родитель;
        :param theme: Тема приложения;
        :param destroy_method: Метод разрушения (закрытия) приложения;
        :param update_method: Метод обновления данных после настройки.
        """

        # Инициализация меню
        super().__init__(parent)

        # Переменная родительского класса
        self.parent = parent

        # Определяем переменную конфигурации дополнительных ресурсов
        self.url_settings = OpenUrl()

        # Переменная для обработки событий
        self.not_use = None

        # Определяем переменные методов
        # Закрытие окна
        self.destroy_window = destroy_method
        # Обновление окна
        self.update_settings_method = update_method

        # Определяем переменную темы окна
        self.theme = theme

        # Определяем все подменю
        self.file_menu = tk.Menu(self)
        self.help_menu = tk.Menu(self)
        self.resources_menu = tk.Menu(self)
        self.update_menu = tk.Menu(self)

        self.draw_menu()

    def draw_menu(self) -> None:
        """
        Метод конфигурации полосы меню. Метод отвечает за связь функционала
        всех подменю с соответствующими командами.
        """
        # Создаем первое подменю -Файл-
        self.file_menu.add_command(label='Настройки программы',
                                   command=self.run_child_settings)
        self.file_menu.add_command(label='Листовой материал',
                                   command=self.run_child_materials)
        self.file_menu.add_command(label='Глубокая гравировка',
                                   command=self.run_child_power)
        self.file_menu.add_command(label='Просмотр расчетов',
                                   command=self.watch_log)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Выход', command=self.destroy_window)

        # Создаем второе подменю -Помощь-
        self.help_menu.add_command(label='Руководство пользователя',
                                   command=self.open_guide)
        self.help_menu.add_separator()
        self.help_menu.add_command(label='Справка',
                                   command=self.open_help)

        # Создаем выпадающий список-подменю "Дополнительные ресурсы"
        self.get_url_menu_data()

        # Подменю (команда) обновить
        # Конфигурация подменю и меню
        self.add_cascade(label='Файл', menu=self.file_menu)
        self.add_cascade(label='Помощь', menu=self.help_menu)
        self.add_command(
            label='Обновить',
            command=self.update_settings_method)
        self.add_cascade(label='Дополнительные ресурсы',
                         menu=self.resources_menu)
        self.parent.configure(menu=self)

    def update_url_set(self, event=None) -> None:
        """
        Метод обновления файла конфигурации дополнительных ресурсов после
        внесения изменений в окне предварительной настройки.
        :param event: Событие (возвращение фокуса на вкладку после закрытия
        окна предварительной настройки)
        """
        try:
            # Обновляем переменную конфигурации
            self.url_settings = OpenUrl()

            # Обновляем список дополнительных ресурсов
            self.resources_menu = tk.Menu(self.parent)
            self.get_url_menu_data()
            self.delete('Дополнительные ресурсы')
            self.add_cascade(label='Дополнительные ресурсы',
                             menu=self.resources_menu)
            self.update()
            self.parent.config(menu=self)

        except Exception as e:
            AppLogger(
                "App.update_url_set",
                "error",
                f"При обновлении списка дополнительных ресурсов было"
                f" вызвано исключение: {e}",
                info=True
            )

        self.not_use = event

    def run_child_materials(self) -> None:
        """
        Открытие дочернего окна редактирования листового материала.
        """
        try:
            # Открытие дочернего окна
            child = ChildMaterials(
                self,
                900,
                450,
                theme=self.theme,
                icon=PathName.resource_path("resources\\Company_logo.ico")
            )
            child.grab_focus()
        except tk.TclError as e:
            AppLogger(
                'AppMenu.run_child_materials',
                'warning',
                f"При упаковке дочернего окна редактирования "
                f"листового материала возникло исключение {e}: "
                f"Окно было закрыто слишком быстро. Виджеты не успели "
                f"прорисоваться / сформировать подсказки или фоновый текст."
            )

    def run_child_power(self) -> None:
        """
        Открытие дочернего окна подбора режимов для выбранного изделия
        (материала), а также выбор оборудования для выполнения работы.
        """
        try:
            child = ChildPowerSet(
                self,
                700,
                450,
                theme=self.theme,
                icon=PathName.resource_path("resources\\Company_logo.ico")
            )
            child.grab_focus()
        except tk.TclError as e:
            AppLogger(
                'AppMenu.run_child_power',
                'warning',
                f"При упаковке дочернего окна расчетов глубокой гравировки "
                f"было вызвано исключение {e}: "
                f"Окно было закрыто слишком быстро. Виджеты не успели "
                f"прорисоваться / сформировать подсказки или фоновый текст."
            )

    def run_child_settings(self) -> None:
        """
        Открытие дочернего окна предварительной настройки программы.
        """
        try:
            child = ChildConfigSet(
                self,
                900,
                450,
                theme=self.theme,
                icon=PathName.resource_path("resources\\Company_logo.ico")
            )
            child.grab_focus()
        except tk.TclError as e:
            AppLogger(
                'AppMenu.run_child_settings',
                'warning',
                f"При упаковке дочернего окна предварительной настройки "
                f"программы возникло исключение {e}: Окно было закрыто "
                f"слишком быстро. Виджеты не успели прорисоваться / "
                f"сформировать подсказки или фоновый текст."
            )

    def open_resource(self, resource_name: str) -> None:
        """
        Метод открытия выбранного ресурса в веб браузере.
        """
        try:
            # Открытие ресурса в веб-браузере
            self.url_settings.open_url(name=resource_name.lower())
        except Exception as e:
            AppLogger(
                "AppMenu.open_resource",
                "error",
                f"При попытке открыть ресурс {resource_name} возникло "
                f"исключение {e}",
                info=True
            )

    def get_url_menu_data(self) -> None:
        """
        Метод добавления данных в меню-список "Дополнительные ресурсы"
        """

        # Создаем выпадающий список-подменю "Дополнительные ресурсы"
        resources_list = list()
        # Создаем список названий ресурсов для подменю
        for key in self.url_settings.url_config['MAIN'].keys():
            resources_list.append(key.capitalize())
        # Устанавливаем для каждого элемента команду
        for i in range(len(resources_list)):
            self.resources_menu.add_command(
                label=resources_list[i],
                command=lambda name=resources_list[i]: self.open_resource(name)
            )

    @staticmethod
    def open_guide() -> None:
        """
        Метод открытия руководства пользователя (документ .pdf формата)
        """
        try:
            os.startfile(PathName.resource_path(
                "resources\\help\\user_guide.pdf"))
            AppLogger(
                'AppMenu.open_guide',
                'info',
                f'Открыто руководство пользователя'
            )
        except Exception as e:
            AppLogger(
                'AppMenu.open_guide',
                'error',
                f'При открытии руководства пользователя возникло исключение:'
                f'{e}',
                info=True
            )

    @staticmethod
    def open_help() -> None:
        """
        Метод открытия правки CHM
        """
        try:
            os.startfile(PathName.resource_path(
                "resources\\help\\AppHelp.chm"))
            AppLogger(
                'AppMenu.open_guide',
                'info',
                f'Открыта справка'
            )
        except Exception as e:
            AppLogger(
                'AppMenu.open_guide',
                'error',
                f'При открытии справки возникло исключение:'
                f'{e}',
                info=True
            )

    @staticmethod
    def watch_log() -> None:
        """
        Метод открытия временного файла лога с расчётами
        """
        try:
            # Считываем данные расчётов из лога
            with open(PathName.resource_path("log/calculation/calc_log.log"),
                      'r', encoding='utf-8') as log_calc:
                temp_data = log_calc.read().split("\n\n")

            # Для каждого расчёта удаляем ненужную пользователю информацию лога
            for i in range(len(temp_data)):
                temp_item = temp_data[i].split('\n')
                if len(temp_item[0]) <= 10:
                    continue
                else:
                    temp_item[0] = (temp_item[0].split('|')[0][0:19:1] + ' |' +
                                    temp_item[0].split('|')[-1])
                    temp_data[i] = "\n".join(temp_item)
            # Записываем расчеты во временный файл в обратном порядке
            with open(PathName.resource_path(
                    "log/calculation/temp_calc_log.txt"), 'w',
                      encoding='utf-8') as temp_log:
                for item in temp_data[-1::-1]:
                    temp_log.write(item)
                    temp_log.write('\n' + '_' * 100 + '\n')
            # Открытие временного файла
            os.startfile(
                PathName.resource_path("log/calculation/temp_calc_log.txt"))
            # Записываем информацию в лог об открытии отчёта
            AppLogger(
                'AppMenu.watch_log',
                'info',
                f'Открыт отчет о расчётах'
            )
        except Exception as e:
            # Записываем ошибку в лог
            AppLogger(
                'AppMenu.watch_log',
                'error',
                f'При открытии отчета о расчётах возникло исключение: {e}',
                info=True
            )

    def add_binds(self) -> None:
        """
        Связывание действий пользователя в интерфейсе приложения с командами
        (фокус в окне - обновление списка).
        """

        self.parent.bind("<FocusIn>", self.update_url_set)


class PersonalCalculateTab(ttk.Frame):
    """
    Класс конфигурации первой вкладки "Частные лица" главного окна приложения.
    На вкладке осуществляется расчет стоимости типовых изделий, а также
    изделий с учетом сложности работы (выставляется весовыми коэффициентами).

    Содержит методы: disable_taxation, settings_update, main_calculation,
    get_ratio_for_calculation, add_new_calc, reset_tab_mian_calculate,
    reset_results, add_tips, add_binds, bind_spins.
    """
    def __init__(self, parent, round_method, destroy_method, settings: tuple):
        """
        Конфигурация и прорисовка первой вкладки основного окна приложения
        "Частные лица".
        :param parent: Экземпляр-родитель Notebook
        :param round_method: Метод округления результата (из класса App)
        :param destroy_method: Метод закрытия приложения (из класса App)
        :param settings: Кортеж: (Настройки программы, Список
        стандартных работ)
        """
        # Инициализация и конфигурация отзывчивости вкладки
        super().__init__(parent)
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=2)
        self.rowconfigure(index=0, weight=4)
        self.rowconfigure(index=1, weight=1)
        self.rowconfigure(index=2, weight=4)

        # Создание метода округления и закрытия программы
        self.round_method = round_method
        self.destroy_method = destroy_method

        # Переменная настроек (конфигурации) программы
        self.main_settings = settings[0]
        self.standard_works_costs = settings[1]

        # Переменные для переключателей выбора типа и сложности расчета
        self.bool_rotation = tk.BooleanVar(value=False)
        self.bool_different = tk.BooleanVar(value=False)
        self.bool_ratio_timing = tk.BooleanVar(value=False)
        self.bool_ratio_packing = tk.BooleanVar(value=False)
        self.bool_ratio_thermal_graving = tk.BooleanVar(value=False)
        self.bool_ratio_oversize = tk.BooleanVar(value=False)
        self.bool_ratio_numbering = tk.BooleanVar(value=False)
        self.bool_ratio_taxation_ao = tk.BooleanVar(value=False)
        self.bool_ratio_attention = tk.BooleanVar(value=False)
        self.bool_ratio_hand_job = tk.BooleanVar(value=False)
        self.bool_ratio_docking = tk.BooleanVar(value=False)
        self.bool_ratio_taxation_ip = tk.BooleanVar(value=False)

        # Переменная выбора типа оборудования
        self.rb_type_of_laser = tk.IntVar(value=1)

        # Переменные коэффициентов сложности и дополнительная стоимость
        self.total_cost = 0
        self.past_cost = 0
        self.past_cost_text = ''
        self.present_cost = 0
        self.cost_design = 0
        self.additional_cost = 0
        self.ratio_laser = 1
        self.ratio_rotation = 1
        self.ratio_different_layouts = 1
        self.ratio_timing = 1
        self.ratio_packing = 1
        self.ratio_thermal_graving = 1
        self.ratio_oversize = 1
        self.ratio_numbering = 1
        self.ratio_taxation_ao = 1
        self.ratio_taxation_ip = 1
        self.ratio_attention = 1
        self.ratio_hand_job = 1
        self.ratio_docking = 1
        self.ratio_many_items = 1
        self.ratio_difficult = 1
        self.ratio_depth = 1
        self.ratio_discount = 1
        self.ratio_taxation = 1
        self.ratio_size = 1
        self.ratio_one_set = 1

        # Переменная для добавления событий
        self.not_use = None

        # Размерность блоков ввода градационных сложностей
        self.gradation_difficult_max = len(
            self.main_settings['GRADATION']['difficult'].split(','))
        self.gradation_depth_max = len(
            self.main_settings['GRADATION']['depth'].split(','))

        # Создание формы для виджетов основного расчета
        self.panel_main_widgets = ttk.Frame(self, padding=(0, 0, 0, 0))
        self.panel_main_widgets.grid(row=0, column=0, padx=10, pady=(10, 0),
                                     sticky="nsew", rowspan=1)

        # Создание формы для переключателей
        self.panel_deep_widgets = ttk.LabelFrame(
            self,
            text="Углубленный расчет",
            padding=10
        )
        self.panel_deep_widgets.grid(row=0, column=1, padx=(10, 20),
                                     pady=(10, 5), sticky="nsew", rowspan=1)

        # Создание формы для вывода результатов
        self.panel_results = ttk.LabelFrame(
            self,
            text="Результаты расчета",
            padding=5
        )
        self.panel_results.grid(row=2, column=0, padx=(10, 20), pady=(10, 20),
                                sticky="nsew", columnspan=2)

        # Конфигурация форм
        self.panel_main_widgets.columnconfigure(index=0, weight=1)
        self.panel_main_widgets.columnconfigure(index=1, weight=2)
        self.panel_main_widgets.rowconfigure(index=0, weight=1)
        self.panel_main_widgets.rowconfigure(index=1, weight=1)
        self.panel_main_widgets.rowconfigure(index=2, weight=1)
        self.panel_main_widgets.rowconfigure(index=3, weight=1)
        self.panel_main_widgets.rowconfigure(index=4, weight=1)
        self.panel_main_widgets.rowconfigure(index=5, weight=1)
        self.panel_main_widgets.rowconfigure(index=6, weight=1)
        self.panel_main_widgets.rowconfigure(index=7, weight=1)
        self.panel_main_widgets.rowconfigure(index=8, weight=1)
        self.panel_main_widgets.rowconfigure(index=9, weight=1)

        self.panel_deep_widgets.columnconfigure(index=0, weight=1)
        self.panel_deep_widgets.columnconfigure(index=1, weight=1)
        self.panel_deep_widgets.rowconfigure(index=0, weight=2)
        self.panel_deep_widgets.rowconfigure(index=1, weight=2)
        self.panel_deep_widgets.rowconfigure(index=2, weight=2)
        self.panel_deep_widgets.rowconfigure(index=3, weight=2)
        self.panel_deep_widgets.rowconfigure(index=4, weight=2)
        self.panel_deep_widgets.rowconfigure(index=5, weight=1)
        self.panel_deep_widgets.rowconfigure(index=6, weight=1)
        self.panel_deep_widgets.rowconfigure(index=7, weight=1)
        self.panel_deep_widgets.rowconfigure(index=8, weight=1)

        self.panel_results.columnconfigure(index=0, weight=1)
        self.panel_results.columnconfigure(index=1, weight=1)
        self.panel_results.rowconfigure(index=0, weight=1)
        self.panel_results.rowconfigure(index=1, weight=1)
        self.panel_results.rowconfigure(index=2, weight=1)
        self.panel_results.rowconfigure(index=3, weight=1)
        self.panel_results.rowconfigure(index=4, weight=1)

        # Создание выпадающего списка стандартных изделий
        ttk.Label(self.panel_main_widgets, text="Стандартное изделие:").grid(
            row=0, column=0, padx=15, pady=0, sticky='ew')
        self.combo_list = list()
        self.combo_list.append('Нет')
        for k, v in self.standard_works_costs['STANDARD'].items():
            self.combo_list.append(k)

        self.combo_products = ttk.Combobox(
            self.panel_main_widgets,
            values=self.combo_list,
            width=20,
            takefocus=False
        )
        self.combo_products.current(0)
        self.combo_products.grid(row=0, column=1, padx=10, pady=0,
                                 sticky="nsew", columnspan=1)

        # Создание переключателей выбора оборудования
        self.rbt_solid = ttk.Radiobutton(
            self.panel_main_widgets,
            text="Твердотельный лазер",
            variable=self.rb_type_of_laser,
            value=1
        )
        self.rbt_solid.grid(row=1, column=0, padx=15, pady=0,
                            sticky="ns")
        self.rbt_co2 = ttk.Radiobutton(
            self.panel_main_widgets,
            text="СО2 лазер",
            variable=self.rb_type_of_laser,
            value=2
        )
        self.rbt_co2.grid(row=1, column=1, padx=15, pady=0,
                          sticky="ns")

        # Поля ввода габаритов изделия
        ttk.Label(self.panel_main_widgets, text='Ширина гравировки, мм:').grid(
            row=3, column=0, padx=15, pady=5, sticky='ew'
        )
        self.ent_width_grav = ttk.Entry(self.panel_main_widgets, width=20)
        self.ent_width_grav.grid(
            row=3, column=1, padx=10, pady=5, sticky='nsew'
        )
        ttk.Label(self.panel_main_widgets, text='Высота гравировки, мм:').grid(
            row=4, column=0, padx=15, pady=5, sticky='ew'
        )
        self.ent_height_grav = ttk.Entry(self.panel_main_widgets, width=20)
        self.ent_height_grav.grid(
            row=4, column=1, padx=10, pady=5, sticky='nsew'
        )

        # Переключатель вращателя/плоскости
        self.switch_rotation = ttk.Checkbutton(
            self.panel_main_widgets,
            text="Гравировка на вращателе",
            variable=self.bool_rotation,
            style="Switch"
        )
        self.switch_rotation.grid(
            row=5, column=0, padx=5, pady=5, sticky="ns")

        # Переключатель -Разные макеты-
        self.chk_different = ttk.Checkbutton(
            self.panel_main_widgets,
            text='Гравировка разных макетов',
            variable=self.bool_different,
            style="Switch"
        )
        self.chk_different.grid(row=5, column=1, padx=5, pady=5, sticky="ns")

        # Переключатель количества изделий
        ttk.Label(self.panel_main_widgets, text='Количество изделий:').grid(
            row=6, column=0, padx=15, pady=5, sticky='ew'
        )
        self.spin_number = ttk.Spinbox(self.panel_main_widgets, from_=1,
                                       to=10000, width=25)
        self.spin_number.insert(0, '1')
        self.spin_number.grid(
            row=6, column=1, padx=5, pady=5, sticky='ns'
        )

        # Переключатель количества прицелов
        ttk.Label(self.panel_main_widgets, text='Количество прицелов:').grid(
            row=7, column=0, padx=15, pady=5, sticky='ew'
        )
        self.spin_aim = ttk.Spinbox(self.panel_main_widgets, from_=1,
                                    to=10000, width=25)
        self.spin_aim.insert(0, '1')
        self.spin_aim.grid(
            row=7, column=1, padx=5, pady=5, sticky='ns'
        )

        # Переключатель количества изделий в одной установке
        ttk.Label(self.panel_main_widgets,
                  text='Количество в установке:').grid(
            row=8, column=0, padx=15, pady=5, sticky='ew')
        self.spin_group = ttk.Spinbox(
            self.panel_main_widgets, from_=1, to=1, width=25)
        self.spin_group.insert(0, '1')
        self.spin_group.grid(
            row=8, column=1, padx=5, pady=5, sticky='ns'
        )

        # Кнопка запуска расчетов
        self.btn_calculate = ttk.Button(
            self.panel_main_widgets,
            text='Рассчитать стоимость',
            command=self.main_calculation,
            style='my.TButton'
        )
        self.btn_calculate.grid(
            row=9, column=0, padx=10, pady=10, sticky='nsew', columnspan=2
        )

        # Создание переключателей в форме углубленного расчета
        self.chk_ratio_timing = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Срочность',
            variable=self.bool_ratio_timing
        )
        self.chk_ratio_timing.grid(row=0, column=0, padx=2, pady=5,
                                   sticky="nsew")

        self.chk_ratio_packing = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Распаковка/Запаковка',
            variable=self.bool_ratio_packing
        )
        self.chk_ratio_packing.grid(row=0, column=1, padx=2, pady=5,
                                    sticky="nsew")

        self.chk_ratio_thermal_graving = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Гравировка термовлиянием',
            variable=self.bool_ratio_thermal_graving
        )
        self.chk_ratio_thermal_graving.grid(row=1, column=0, padx=2, pady=5,
                                            sticky="nsew")

        self.chk_ratio_oversize = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Негабаритное изделие',
            variable=self.bool_ratio_oversize
        )
        self.chk_ratio_oversize.grid(row=1, column=1, padx=2, pady=5,
                                     sticky="nsew")

        self.chk_ratio_numbering = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Счетчик',
            variable=self.bool_ratio_numbering
        )
        self.chk_ratio_numbering.grid(row=2, column=0, padx=2, pady=5,
                                      sticky="nsew")

        self.chk_ratio_taxation_ooo = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Оплата по счету ООО',
            variable=self.bool_ratio_taxation_ao,
            command=self.disable_taxation
        )
        self.chk_ratio_taxation_ooo.grid(row=4, column=0, padx=2, pady=5,
                                         sticky="nsew")

        self.chk_ratio_attention = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Повышенное внимание',
            variable=self.bool_ratio_attention
        )
        self.chk_ratio_attention.grid(row=3, column=0, padx=2, pady=5,
                                      sticky="nsew")

        self.chk_ratio_hand_job = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Ручные работы',
            variable=self.bool_ratio_hand_job
        )
        self.chk_ratio_hand_job.grid(row=3, column=1, padx=2, pady=5,
                                     sticky="nsew")

        self.chk_ratio_docking = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Стыковка элементов',
            variable=self.bool_ratio_docking
        )
        self.chk_ratio_docking.grid(row=2, column=1, padx=2, pady=5,
                                    sticky="nsew")

        self.chk_ratio_taxation_ip = ttk.Checkbutton(
            self.panel_deep_widgets,
            text='Оплата по счету ИП',
            variable=self.bool_ratio_taxation_ip,
            command=self.disable_taxation
        )
        self.chk_ratio_taxation_ip.grid(row=4, column=1, padx=2, pady=5,
                                        sticky="nsew")

        # Переключатель сложности установки
        ttk.Label(self.panel_deep_widgets, text='Сложность установки').grid(
            row=5, column=0, padx=(10, 0), pady=5, sticky='nsew'
        )
        self.spin_difficult = ttk.Spinbox(
            self.panel_deep_widgets, from_=1, to=self.gradation_difficult_max)
        self.spin_difficult.insert(0, '1')
        self.spin_difficult.configure(state='readonly')
        self.spin_difficult.grid(
            row=5, column=1, padx=0, pady=5, sticky='nsew'
        )

        # Переключатель глубины гравировки
        ttk.Label(self.panel_deep_widgets, text='Глубина гравировки').grid(
            row=6, column=0, padx=(10, 0), pady=5, sticky='nsew'
        )
        self.spin_depth = ttk.Spinbox(
            self.panel_deep_widgets, from_=1, to=self.gradation_depth_max)
        self.spin_depth.insert(0, '1')
        self.spin_depth.configure(state='readonly')
        self.spin_depth.grid(
            row=6, column=1, padx=0, pady=5, sticky='nsew'
        )

        # Окно ввода доплаты за макетирование
        ttk.Label(self.panel_deep_widgets, text='Макетирование, руб.').grid(
            row=7, column=0, padx=(10, 0), pady=0, sticky='nsew')
        self.ent_design = ttk.Entry(self.panel_deep_widgets, width=5)
        self.ent_design.grid(row=7, column=1, padx=0, pady=5,
                             sticky='nsew')

        # Окно ввода скидки оператора
        ttk.Label(self.panel_deep_widgets, text='Скидка оператора, %').grid(
            row=8, column=0, padx=(10, 0), pady=0, sticky='nsew')
        self.spin_discount = ttk.Spinbox(self.panel_deep_widgets,
                                         from_=0, to=30)
        self.spin_discount.insert(0, '0')
        self.spin_discount.configure(state='readonly')
        self.spin_discount.grid(
            row=8, column=1, padx=0, pady=5, sticky='nsew'
        )

        # Виджеты вывода результатов расчета
        self.lbl_result_grav = ttk.Label(
            self.panel_results,
            text=f"Стоимость гравировки:"
            f"  {0:.0f}  руб/шт.",
            font='Arial 14',
            foreground='#217346'
        )
        self.lbl_result_grav.grid(row=0, column=0, padx=(10, 10), pady=(10, 0),
                                  sticky="nsew")
        self.lbl_result_design = ttk.Label(
            self.panel_results,
            text=f"Стоимость макетирования:"
                 f"  {0:.0f}  руб.",
            font='Arial 14',
            foreground='#217346'
        )
        self.lbl_result_design.grid(
            row=1, column=0, padx=(10, 10), pady=(2, 10), sticky="nsew")

        ttk.Separator(self.panel_results).grid(row=3, column=0, columnspan=2,
                                               pady=5, sticky='ew')

        self.lbl_result_cost = ttk.Label(
            self.panel_results,
            text=f"ИТОГОВАЯ СТОИМОСТЬ:"
                 f"  {0:.0f}  руб.",
            font='Arial 15 bold',
            foreground='#217346'
        )
        self.lbl_result_cost.grid(row=4, column=0, padx=(10, 10), pady=(0, 10),
                                  sticky="nsew", columnspan=1)

        # Кнопка добавления нового расчета
        self.btn_add_calculate = ttk.Button(
            self.panel_results,
            text='Добавить расчет',
            command=self.add_new_calc
        )
        self.btn_add_calculate.grid(
            row=0, column=1, padx=10, pady=10, sticky='nsew')

        # Кнопка обнуления расчета
        self.btn_reset = ttk.Button(
            self.panel_results,
            text='Сброс',
            command=self.reset_results
        )
        self.btn_reset.grid(
            row=1, column=1, padx=10, pady=10, sticky='nsew')

        # Кнопка выхода
        self.btn_close_window = ttk.Button(
            self.panel_results,
            text='Выход',
            command=self.destroy_method
        )
        self.btn_close_window.grid(
            row=4, column=1, padx=10, pady=10, sticky='nsew')

        # Вывод результатов прошлого и текущего расчета
        self.lbl_present_results = ttk.Label(
            self.panel_results,
            text=f"Текущий расчет = {0:.0f} руб.",
            font='Arial 12',
            foreground='#217346'
        )
        self.lbl_present_results.grid(row=2, column=0, padx=10, pady=10,
                                      sticky="nsew", columnspan=1)

        self.lbl_past_results = ttk.Label(
            self.panel_results,
            text=f"",
            font='Arial 12',
            foreground='#217346'
        )
        self.lbl_past_results.grid(row=2, column=1, padx=10, pady=10,
                                   sticky="ns", columnspan=1)

    def disable_taxation(self) -> None:
        """
        Метод установки зависимости для способов оплаты.
        Если активируется способ оплаты одним методом, то происходит
        деактивация возможности выбора второго.
        """
        # Если выбирается оплата по счету АО
        if self.bool_ratio_taxation_ao.get():
            self.chk_ratio_taxation_ip.config(state='disabled')
        # Если убирается оплата по счету АО
        elif not self.bool_ratio_taxation_ao.get():
            self.chk_ratio_taxation_ip.config(state='enabled')

        # Если выбирается оплата по счету ИП
        if self.bool_ratio_taxation_ip.get():
            self.chk_ratio_taxation_ooo.config(state='disabled')
        # Если убирается оплата по счету ИП
        elif not self.bool_ratio_taxation_ip.get():
            self.chk_ratio_taxation_ooo.config(state='enabled')

    def settings_update(self, event=None) -> None:
        """
        Метод обновления вкладки. Здесь осуществляется обновление
        переменной конфигурации программы. Реализуется после изменения
        настроек приложения.
        :param event: Возвращение фокуса на вкладку после закрытия окна
        предварительной настройки.
        """
        # Обновление переменной конфигурации
        self.main_settings = ConfigSet().config
        self.standard_works_costs = StandardSet().config

        # Обновление данных в таблице
        self.combo_list = list()
        self.combo_list.append('Нет')
        for k, v in self.standard_works_costs['STANDARD'].items():
            self.combo_list.append(k)
        self.combo_products.configure(values=self.combo_list)

        # Устанавливается размерность блоков ввода градационных сложностей
        self.gradation_difficult_max = len(
            self.main_settings['GRADATION']['difficult'].split(','))
        self.gradation_depth_max = len(
            self.main_settings['GRADATION']['depth'].split(','))
        self.spin_difficult.config(to=self.gradation_difficult_max)
        self.spin_depth.config(to=self.gradation_depth_max)

        # Обновление вкладки
        self.not_use = event
        self.update()

    def main_calculation(self) -> None:
        """
        Метод основного и углубленного расчета.

        Формула имеет следующий вид:
            Итоговая цена = (дополнительные прицелы +
            + минимальная стоимость * коэффициенты) * учет НДС * учет скидки *
            * учет количества изделий * учет количества в одной установке
        """
        try:
            # Формирование начальной стоимости
            if self.combo_products.get() == "Нет":  # Если не выбрано изделие
                cost = int(self.main_settings["MAIN"]["min_cost"])
            else:  # Если выбрано стандартное изделие
                cost = int(
                    self.standard_works_costs["STANDARD"][
                        self.combo_products.get()]
                )

            # Получение данных для коэффициентов
            self.get_ratio_for_calculation()

            # Расчет основной стоимости
            main_cost = ((self.additional_cost + (cost * (
                    self.ratio_laser * self.ratio_rotation *
                    self.ratio_different_layouts * self.ratio_timing *
                    self.ratio_packing * self.ratio_thermal_graving *
                    self.ratio_oversize * self.ratio_numbering *
                    self.ratio_attention * self.ratio_hand_job *
                    self.ratio_docking * self.ratio_difficult *
                    self.ratio_depth * self.ratio_size)))
                         * self.ratio_taxation_ao * self.ratio_taxation_ip *
                         self.ratio_many_items * self.ratio_one_set *
                         self.ratio_discount)
            # Вывод результатов стоимости гравировки
            self.lbl_result_grav.config(
                text=f"Стоимость гравировки:"
                f"  {self.round_method(main_cost):_.0f}  руб/шт.".replace(
                    '_', ' ')
            )
            # Вывод результатов стоимости макетирования
            self.lbl_result_design.config(
                text=f"Стоимость макетирования:"
                     f"  {self.cost_design:_.0f}  руб.".replace('_', ' ')
            )

            # Полная стоимость с учетом макетирования
            all_cost = (self.round_method(main_cost) *
                        int(self.spin_number.get()) + self.cost_design)
            # Вывод результатов полной стоимости для текущего расчета
            self.lbl_present_results.config(
                text=f"Текущий расчет = {all_cost:_.0f} руб.".replace(
                    '_', ' ')
            )

            # Сохранение переменной текущий стоимости
            self.present_cost = all_cost

            # Вывод результатов итоговой стоимости
            self.lbl_result_cost.config(
                text=f"ИТОГОВАЯ СТОИМОСТЬ:"
                     f"  {self.total_cost + self.present_cost:_.0f}  "
                     f"руб.".replace('_', ' ')
            )

            # Считываем параметры расчёта, сохраняемые в лог
            temp_params = ['']*4
            temp_params[0] = "Гравировка на плоскости." if (
                    self.ratio_rotation == 1) else "Гравировка на вращателе."
            temp_params[1] = "Тип оборудования: Твердотельный лазер." if (
                    self.ratio_laser == 1) else \
                "Тип оборудования: Газовый лазер."
            temp_params[2] = (f"Количество изделий: {self.spin_number.get()} "
                              f"шт.")
            temp_params[3] = (f"Количество прицелов на изделии:"
                              f" {self.spin_aim.get()} шт.")

            # Сохраняем расчет в лог
            AppLogger(
                "PersonalCalculateTab.main_calculation",
                'calc',
                f'Произведен расчет на вкладке "Частные лица"',
                _=temp_params[0],
                __=temp_params[1],
                ___=temp_params[2],
                ____=temp_params[3],
                _____=self.lbl_result_grav.cget('text'),
                ______=self.lbl_present_results.cget('text'),
                _______=self.lbl_result_design.cget('text'),
                ________=self.lbl_result_cost.cget('text')
            )
        except Exception as e:
            AppLogger(
                "PersonalCalculateTab.main_calculation",
                'error',
                f'Во время расчета вызвано исключение: {e}',
                True
            )

    def get_ratio_for_calculation(self) -> None:
        """
        Метод формирования коэффициентов сложностей на основе получения
        данных из пользовательского интерфейса.
        """
        # Формирование значений коэффициентов
        # Коэффициент ratio_size __Габариты гравировки__
        try:
            size_list = (
                self.main_settings['GRADATION']['area'].split(','))

            if self.rb_type_of_laser.get() == 2:  # Для газового лазера
                size_min = 150 * 100
                size_max = 400 * 680
                ratio_size_max = float(size_list[1])
                temp_area = float(self.ent_height_grav.get()) * float(
                    self.ent_width_grav.get())
                self.ratio_size = RatioArea(
                    size_min, size_max, ratio_size_max).get_polynomial_ratio(
                    temp_area)
            else:  # Для твердотельного лазера
                size_min = 70 * 70
                size_max = 200 * 200
                ratio_size_max = float(size_list[0])
                temp_area = float(self.ent_height_grav.get()) * float(
                    self.ent_width_grav.get())
                self.ratio_size = RatioArea(
                    size_min, size_max, ratio_size_max).get_linear_ratio(
                    temp_area)

        except ValueError as e:
            self.ratio_size = 1
            AppLogger(
                'PersonalCalculateTab.get_ratio_for_calculation',
                'warning',
                f'При считывании габаритов гравировки возникло исключение'
                f' "{e}", размеры указаны неверно, или не указаны вовсе -('
                f'{self.ent_width_grav.get()}, {self.ent_height_grav.get()})'
            )

        # Коэффициент ratio_laser __Тип лазера__
        if self.rb_type_of_laser.get() == 2:  # Если газовый лазер
            self.ratio_laser = float(self.main_settings[
                                    "RATIO_SETTINGS"]["ratio_laser_gas"])
        else:  # Если твердотельный лазер
            self.ratio_laser = 1

        # Коэффициент ratio_rotation __Вращатель__
        if self.bool_rotation.get():  # Если гравировка с вращением
            self.ratio_rotation = float(self.main_settings[
                                       "RATIO_SETTINGS"]["ratio_rotation"])
        else:  # Если гравировка без вращения
            self.ratio_rotation = 1

        # Коэффициент ratio_different_layouts __Разные макеты__
        if self.bool_different.get() and (
                int(self.spin_number.get()) > 1):  # Если разные макеты
            self.ratio_different_layouts = float(
                self.main_settings["RATIO_SETTINGS"][
                    "ratio_different_layouts"])
        else:  # Если один макет
            self.ratio_different_layouts = 1

        # Коэффициент ratio_timing __Срочность__
        if self.bool_ratio_timing.get():
            self.ratio_timing = float(self.main_settings["RATIO_SETTINGS"][
                                     "ratio_timing"])
        else:
            self.ratio_timing = 1

        # Коэффициент ratio_packing __Распаковка/Запаковка__
        if self.bool_ratio_packing.get():
            self.ratio_packing = float(self.main_settings["RATIO_SETTINGS"][
                                      "ratio_packing"])
        else:
            self.ratio_packing = 1

        # Коэффициент ratio_thermal_graving __Гравировка термовлиянием__
        if self.bool_ratio_thermal_graving.get():
            self.ratio_thermal_graving = float(self.main_settings[
                                               "RATIO_SETTINGS"][
                                              "ratio_thermal_graving"])
        else:
            self.ratio_thermal_graving = 1

        # Коэффициент ratio_oversize __Негабаритное изделие__
        if self.bool_ratio_oversize.get():
            self.ratio_oversize = float(self.main_settings["RATIO_SETTINGS"][
                                       "ratio_oversize"])
        else:
            self.ratio_oversize = 1

        # Коэффициент ratio_numbering __Счетчик__
        if self.bool_ratio_numbering.get() and (
                int(self.spin_number.get()) > 1):
            self.ratio_numbering = float(self.main_settings["RATIO_SETTINGS"][
                                        "ratio_numbering"])
        else:
            self.ratio_numbering = 1

        # Коэффициент ratio_taxation_ao __Оплата по счету ООО__
        if self.bool_ratio_taxation_ao.get():
            self.ratio_taxation_ao = float(
                self.main_settings["RATIO_SETTINGS"][
                    "ratio_taxation"].split(',')[0])
        else:
            self.ratio_taxation_ao = 1

        # Коэффициент ratio_attention __Повышенное внимание__
        if self.bool_ratio_attention.get():
            self.ratio_attention = float(self.main_settings["RATIO_SETTINGS"][
                                        "ratio_attention"])
        else:
            self.ratio_attention = 1

        # Коэффициент ratio_hand_job __Ручные работы__
        if self.bool_ratio_hand_job.get():
            self.ratio_hand_job = float(self.main_settings["RATIO_SETTINGS"][
                                       "ratio_hand_job"])
        else:
            self.ratio_hand_job = 1

        # Коэффициент ratio_docking __Стыковка элементов__
        if self.bool_ratio_docking.get() and int(self.spin_aim.get()) > 1:
            self.ratio_docking = float(self.main_settings["RATIO_SETTINGS"][
                                      "ratio_docking"])
        else:
            self.ratio_docking = 1

        # Коэффициент ratio_taxation_ip __Оплата по счету ИП__
        if self.bool_ratio_taxation_ip.get():
            self.ratio_taxation_ip = float(
                self.main_settings["RATIO_SETTINGS"][
                    "ratio_taxation"].split(',')[1])
        else:
            self.ratio_taxation_ip = 1

        # Дополнительная стоимость за количество установок
        if int(self.spin_aim.get()) > 1:
            self.additional_cost = (
                    (int(self.spin_aim.get()) - 1) *
                    int(self.main_settings["MAIN"]["additional_cost"]))
        else:
            self.additional_cost = 0

        # Коэффициент зависимости от количества изделий
        if int(self.spin_number.get()) == 1:  # Если изделие одно
            self.ratio_many_items = 1
        elif 1 < int(self.spin_number.get()) <= 5:  # До 5 изделий
            self.ratio_many_items = 1 - (int(self.spin_number.get())/10)
        else:  # Изделий больше 5
            self.ratio_many_items = 0.85 * (int(self.spin_number.get()) ** (
                -float(self.main_settings["MAIN"]["many_items"])))

        # Коэффициент зависимости от количества изделий в установке
        if int(self.spin_group.get()) == 1:
            self.ratio_one_set = 1
        else:
            self.ratio_one_set = int(self.spin_group.get()) ** (
                -float(self.main_settings["MAIN"]["one_set"]))

        # Коэффициент сложности установки
        difficult_list = (
            self.main_settings['GRADATION']['difficult'].split(','))
        self.ratio_difficult = float(
            difficult_list[int(self.spin_difficult.get()) - 1])

        # Коэффициент глубины гравировки
        depth_list = self.main_settings['GRADATION']['depth'].split(
            ',')
        self.ratio_depth = float(
            depth_list[int(self.spin_depth.get()) - 1])

        # Доплата за макетирование
        try:
            self.cost_design = float(self.ent_design.get())
        except ValueError as e:
            AppLogger(
                'PersonalCalculateTab.get_ratio_for_calculation',
                'warning',
                f'При считывании доплаты за макетирование возникло '
                f'исключение "{e}": Данные не введены, или введены '
                f'некорректно - {self.ent_design.get()}.'
            )
            self.cost_design = 0

        # Скидка оператора
        try:
            self.ratio_discount = 1 - float(self.spin_discount.get()) / 100
        except ValueError as e:
            self.ratio_discount = 1
            AppLogger(
                'PersonalCalculateTab.get_ratio_for_calculation',
                'warning',
                f'При считывании скидки оператора возникло '
                f'исключение "{e}": Данные не введены, или введены '
                f'некорректно - {self.spin_discount.get()}.'
            )

    def add_new_calc(self) -> None:
        """
        Метод добавления нового расчета в рамках одного заказа
        """
        # Сохраняем данные прошлых расчетов
        self.past_cost = self.present_cost
        self.total_cost += self.present_cost
        if self.past_cost_text == "":   # Если добавлений до этого не было
            self.past_cost_text += f'{self.past_cost:.0f}'
        else:
            self.past_cost_text += f' + {self.past_cost:.0f}'
        self.present_cost = 0

        # Добавление новых данных в прошлый и текущий расчет
        temp_past_text = f"Прошлый расчет = {self.past_cost_text} руб."
        if len(temp_past_text) > 60:
            temp_past_text = '\n'.join(wrap(temp_past_text, 60))

        # Вывод результатов
        self.lbl_past_results.config(
            text=temp_past_text
        )
        self.lbl_present_results.config(
            text=f"Текущий расчет = {0:.0f} руб."
        )

        # Обнуление вывода первого расчета
        self.lbl_result_grav.config(
            text=f"Стоимость гравировки:"
                 f"  {0:.0f}  руб/шт."
        )
        self.lbl_result_design.config(
            text=f"Стоимость макетирования:"
                 f"  {0:.0f}  руб.",
        )

        # Обнуление переключателей и окон ввода
        self.reset_tab_mian_calculate()

        AppLogger(
            "PersonalCalculateTab.add_new_calc",
            'info',
            f'Выполнено добавление расчета на вкладке "Частные лица"'
        )

    def reset_tab_mian_calculate(self) -> None:
        """
        Обнуления переключателей и полей
        """
        # Обнуление переключателей
        self.bool_rotation.set(False)
        self.bool_different.set(False)
        self.bool_ratio_timing.set(False)
        self.bool_ratio_packing.set(False)
        self.bool_ratio_thermal_graving.set(False)
        self.bool_ratio_oversize.set(False)
        self.bool_ratio_numbering.set(False)
        self.bool_ratio_taxation_ao.set(False)
        self.bool_ratio_attention.set(False)
        self.bool_ratio_hand_job.set(False)
        self.bool_ratio_docking.set(False)
        self.bool_ratio_taxation_ip.set(False)
        self.rb_type_of_laser.set(1)
        self.chk_ratio_taxation_ip.config(state='enabled')
        self.chk_ratio_taxation_ooo.config(state='enabled')

        # Обнуление окон ввода данных
        self.ent_design.delete(0, tk.END)
        self.ent_height_grav.delete(0, tk.END)
        self.ent_width_grav.delete(0, tk.END)

        self.add_binds()

        # Обнуление выпадающего списка и счетчиков
        self.combo_products.set('Нет')

        self.spin_difficult.configure(state='normal')
        self.spin_difficult.delete(0, tk.END)
        self.spin_difficult.insert(0, '1')
        self.spin_difficult.configure(state='readonly')

        self.spin_depth.configure(state='normal')
        self.spin_depth.delete(0, tk.END)
        self.spin_depth.insert(0, '1')
        self.spin_depth.configure(state='readonly')

        self.spin_number.configure(state='normal')
        self.spin_number.delete(0, tk.END)
        self.spin_number.insert(0, '1')
        self.spin_number.configure(state='readonly')

        self.spin_aim.configure(state='normal')
        self.spin_aim.delete(0, tk.END)
        self.spin_aim.insert(0, '1')
        self.spin_aim.configure(state='readonly')

        self.spin_discount.configure(state='normal')
        self.spin_discount.delete(0, tk.END)
        self.spin_discount.insert(0, '0')
        self.spin_discount.configure(state='readonly')

        self.spin_group.configure(state='normal')
        self.spin_group.delete(0, tk.END)
        self.spin_group.insert(0, '1')
        self.spin_group.configure(state='readonly', to=1)

    def reset_results(self) -> None:
        """
        Метод обнуления результатов расчета, а также обнуление виджетов окна.
        """
        # Обнуление результатов расчета
        self.past_cost = 0
        self.present_cost = 0
        self.total_cost = 0
        self.past_cost_text = ''

        # Обнуление данных в метках вывода результатов расчета
        self.lbl_past_results.config(
            text=f""
        )
        self.lbl_present_results.config(
            text=f"Текущий расчет = {0:.0f} руб."
        )
        self.lbl_result_grav.config(
            text=f"Стоимость гравировки:"
                 f"  {0:.0f}  руб/шт."
        )
        self.lbl_result_design.config(
            text=f"Стоимость макетирования:"
                 f"  {0:.0f}  руб."
        )
        self.lbl_result_cost.config(
            text=f"ИТОГОВАЯ СТОИМОСТЬ:"
                 f"  {0:.0f}  руб."
        )

        # Обнуляем переключатели
        self.reset_tab_mian_calculate()

        AppLogger(
            "PersonalCalculateTab.reset_results",
            'info',
            f'Выполнено обнуления результатов расчета на вкладке "Частные '
            f'лица"'
        )

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса вкладки 'ЧАСТНЫЕ
        ЛИЦА'
        """
        BalloonTips(self.combo_products,
                    text=f'Выбор стандартного типа работы.')
        BalloonTips(self.chk_ratio_timing,
                    text=f'Работа в выходной день\n'
                         f'или работа сверх очереди.')
        BalloonTips(self.chk_ratio_packing,
                    text=f'Большие затраты времени\n'
                         f'на распаковку/запаковку '
                         f'изделий.')
        BalloonTips(self.chk_ratio_thermal_graving,
                    text=f'Гравировка нанесением\n'
                         f'оксидной пленки.')
        BalloonTips(self.chk_ratio_oversize,
                    text=f'Для гравировки требуется\n'
                         f'снятие головы.')
        BalloonTips(self.chk_ratio_numbering,
                    text=f'Гравировка изделий со\n'
                         f'сквозной нумерацией.')
        BalloonTips(self.chk_ratio_docking,
                    text=f'Гравировка со стыковкой\n'
                         f'элементов.')
        BalloonTips(self.chk_ratio_attention,
                    text=f'Гравировка любых ювелирных изделий,\n'
                         f'а также других изделий (материалов),\n'
                         f'требующих особой осторожности.')
        BalloonTips(self.chk_ratio_hand_job,
                    text=f'Шлифовка, снятие краски и др. виды работ,\n'
                         f'требующие больших временных затрат.')
        BalloonTips(self.chk_ratio_taxation_ooo,
                    text=f'Учет НДС при оплате по счету ООО.')
        BalloonTips(self.chk_ratio_taxation_ip,
                    text=f'Учет НДС при оплате через кассу.')
        BalloonTips(self.spin_difficult,
                    text=f'Ступенчатая сложность гравировки:\n'
                         f'{"‾" * 80}\n'
                         f'1 - Привязка к 1 габариту или грани;\n'
                         f'2 - Привязка к координатному расположению,\n'
                         f'рамкам, базовым точкам, попадание по окружности;\n'
                         f'3 - Сложность пространственная: тяжело установить\n'
                         f'или прицелить изделие из-за его габаритов/формы;\n'
                         f'4 - Строгая привязка к параллельности и граням \n'
                         f'(Например, валы Маенкова);\n'
                         f'5 - Очень сложное выставление и привязка\n'
                         f'(Например гравировка на спиральном кольце \n'
                         f'на тонкой грани.')
        BalloonTips(self.spin_depth,
                    text=f'Ступенчатая глубина гравировки:\n'
                         f'{"‾" * 60}\n'
                         f'1 - Типовая гравировка до 25 проходов;\n'
                         f'2 - Гравировка до 50 проходов;\n'
                         f'3 - Гравировка  до 150 проходов;\n'
                         f'4 - Гравировка  до 300 проходов;\n'
                         f'5 - Гравировка  более 300 проходов.')

        BalloonTips(self.btn_add_calculate,
                    text=f'Расчет дополнительного изделия\n'
                         f'к основному.')
        BalloonTips(self.btn_reset,
                    text='Сбросить существующие расчеты.')
        BalloonTips(self.btn_calculate,
                    text=f'Для расчета можно использовать\n'
                         f'клавишу <Enter>.')

    def add_binds(self) -> None:
        """
        Метод установки фонового текста в поля ввода класса вкладки
        'ЧАСТНЫЕ ЛИЦА' и связывание действий пользователя в интерфейсе
        приложения с командами.
        """
        # Установка фонового текста
        BindEntry(self.ent_width_grav, text='Ширина гравировки, мм')
        BindEntry(self.ent_height_grav, text='Высота гравировки, мм')
        BindEntry(self.ent_design)

        # Установка команд
        self.spin_group.bind('<Enter>', self.bind_spins)
        self.bind('<FocusIn>', self.settings_update)

    def bind_spins(self, event=None) -> None:
        """
        Ограничение максимального количества изделий в одной установке.
        Количество изделий в 1 установке не может быть больше, чем общее
        количество изделий в работе.
        :param event: Возвращение фокуса (курсора) на виджет
        """
        self.spin_group.config(
            to=int(self.spin_number.get())
        )
        self.not_use = event


class SheetMaterialsTab(ttk.Frame):
    """
    Класс конфигурации второй вкладки "Листовой материал" главного окна
    приложения. На вкладке осуществляется расчет стоимости изделий
    (партии и поштучно) из выбранного листового материала. Также
    осуществляется расчет расходников и расчет приблизительного количества
    потребного материала.

    Содержит методы: material_calculation, update_base, add_tips, add_binds,
    bind_update_base.
    """
    def __init__(self, parent, round_method):
        """
        Конфигурация и прорисовка второй вкладки основного окна приложения
        "ЛИСТОВОЙ МАТЕРИАЛ"
        :param parent: Экземпляр-родитель Notebook
        :param round_method: Метод округления результата (из класса App)
        """
        # Инициализация и конфигурация отзывчивости вкладки
        super().__init__(parent)
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=2)
        self.rowconfigure(index=1, weight=1)

        # Создание метода округления (наследование от класса App)
        self.round_method = round_method

        # Создание переменной для событий
        self.not_use = None

        # Создание формы для виджетов
        self.panel_sheet_materials_widgets = ttk.Frame(self)
        self.panel_sheet_materials_widgets.grid(
            row=0, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Конфигурация формы виджетов
        self.panel_sheet_materials_widgets.columnconfigure(index=0, weight=1)
        self.panel_sheet_materials_widgets.columnconfigure(index=1, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=0, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=1, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=2, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=3, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=4, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=5, weight=1)
        self.panel_sheet_materials_widgets.rowconfigure(index=6, weight=1)

        # Создание формы для вывода результатов
        self.panel_sheet_materials_result = ttk.LabelFrame(
            self, text='Результаты')
        self.panel_sheet_materials_result.grid(
            row=1, column=0, padx=20, pady=(0, 30), sticky="nsew")

        # Конфигурация формы для вывода результатов
        self.panel_sheet_materials_result.columnconfigure(index=0, weight=1)
        self.panel_sheet_materials_result.columnconfigure(index=1, weight=1)
        self.panel_sheet_materials_result.rowconfigure(index=0, weight=1)
        self.panel_sheet_materials_result.rowconfigure(index=1, weight=1)
        self.panel_sheet_materials_result.rowconfigure(index=2, weight=1)
        self.panel_sheet_materials_result.rowconfigure(index=3, weight=1)
        self.panel_sheet_materials_result.rowconfigure(index=4, weight=1)

        # Виджеты выбора материала
        # Получение материалов
        self.material_list = list()
        for n in Materials().get_mat_price():
            self.material_list.append(n)

        self.combo_mat = ttk.Combobox(
            self.panel_sheet_materials_widgets,
            values=self.material_list,
            takefocus=False
        )
        self.combo_mat.current(0)
        self.combo_mat.grid(
            row=0, column=0, padx=10, pady=5, columnspan=2, sticky='nsew'
        )

        # Виджеты ввода количества изделий
        ttk.Label(self.panel_sheet_materials_widgets,
                  text="Количество изделий, шт:").grid(
            row=1, column=0, padx=15, pady=0, sticky='ew')
        self.ent_num = ttk.Entry(self.panel_sheet_materials_widgets,
                                 width=100, takefocus=False)
        self.ent_num.grid(
            row=1, column=1, padx=10, pady=5, columnspan=1, sticky='nsew')

        # Поля ввода габаритов изделия
        ttk.Label(self.panel_sheet_materials_widgets,
                  text="Ширина изделий, мм:").grid(
            row=2, column=0, padx=15, pady=0, sticky='ew')
        self.ent_width = ttk.Entry(
            self.panel_sheet_materials_widgets, width=100, takefocus=False)
        self.ent_width.grid(
            row=2, column=1, padx=10, pady=5, columnspan=1, sticky='nsew')
        ttk.Label(self.panel_sheet_materials_widgets,
                  text="Высота изделий, мм:").grid(
            row=3, column=0, padx=15, pady=0, sticky='ew')
        self.ent_height = ttk.Entry(
            self.panel_sheet_materials_widgets, width=100, takefocus=False)
        self.ent_height.grid(
            row=3, column=1, padx=10, pady=5, columnspan=1, sticky='nsew')

        # Поле ввода доплаты (макетирование и другое)
        ttk.Label(self.panel_sheet_materials_widgets,
                  text="Доп. плата / Макетирование, руб:").grid(
            row=4, column=0, padx=15, pady=0, sticky='ew')
        self.ent_draw_overprice = ttk.Entry(
            self.panel_sheet_materials_widgets, width=100, takefocus=False)
        self.ent_draw_overprice.grid(
            row=4, column=1, padx=10, pady=5, columnspan=1, sticky='nsew')

        # Переключатель скидки
        ttk.Label(self.panel_sheet_materials_widgets,
                  text="Скидка оператора, %:").grid(
            row=5, column=0, padx=15, pady=0, sticky='ew')
        self.spin_discount_material = ttk.Spinbox(
            self.panel_sheet_materials_widgets, from_=0, to=30, width=100,
            takefocus=False)
        self.spin_discount_material.insert(0, '0')
        self.spin_discount_material.configure(state='readonly')
        self.spin_discount_material.grid(
            row=5, column=1, padx=10, pady=(5, 10), columnspan=1,
            sticky='nsew')

        # Кнопка запуска расчетов
        self.btn_get_cost_materials = ttk.Button(
            self.panel_sheet_materials_widgets,
            width=20,
            text="Рассчитать",
            command=self.material_calculation
        )
        self.btn_get_cost_materials.grid(
            row=6, column=0, padx=10, pady=0, columnspan=2, sticky='nsew'
        )

        # Виджеты результатов расчета
        # Виджет -Себестоимость одного изделия-
        self.lbl_result_1 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Себестоимость одного изделия:"
                 f"  {0:.0f}  руб/шт.",
            font='Arial 12',
        )
        self.lbl_result_1.grid(
            row=0, column=0, padx=10, pady=10, sticky='nsew'
        )

        # Виджет -Себестоимость партии-
        self.lbl_result_2 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Себестоимость партии:"
                 f"  {0:.0f}  руб.",
            font='Arial 12',
        )
        self.lbl_result_2.grid(
            row=1, column=0, padx=10, pady=10, sticky='nsew'
        )

        # Виджет -Количество изделий с одного листа-
        self.lbl_result_3 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Количество изделий с одного листа:"
                 f"  {0:.0f}  шт.",
            font='Arial 12'
        )
        self.lbl_result_3.grid(
            row=0, column=1, padx=10, pady=10, sticky='nsew'
        )

        # Виджет -Количество листов на партию-
        self.lbl_result_4 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Минимальное количество листов на партию:"
                 f"  {0:.0f}  шт.",
            font='Arial 12'
        )
        self.lbl_result_4.grid(
            row=1, column=1, padx=10, pady=10, sticky='nsew'
        )

        # Виджет -Стоимость одного изделия партии-
        self.lbl_result_5 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Стоимость изделия:"
                 f"  {0:.0f}  руб/шт.",
            font='Arial 14 bold',
            foreground='#217346'
        )
        self.lbl_result_5.grid(
            row=2, column=0, padx=10, pady=10, sticky='nsew'
        )

        # Виджет -Макетирование-
        self.lbl_result_7 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"Макетирование:"
                 f"  {0:.0f}  руб.",
            font='Arial 14 bold',
            foreground='#217346'
        )
        self.lbl_result_7.grid(
            row=2, column=1, padx=10, pady=10, sticky='nsew'
        )

        # Разделительная полоса
        ttk.Separator(self.panel_sheet_materials_result).grid(
            row=3, column=0, columnspan=2, pady=0, sticky='ew')

        # Виджет -ИТОГОВАЯ СТОИМОСТЬ ПАРТИИ-
        self.lbl_result_6 = ttk.Label(
            self.panel_sheet_materials_result,
            text=f"ИТОГОВАЯ СТОИМОСТЬ ПАРТИИ:"
                 f"  {0:.0f}  руб.",
            font='Arial 15 bold',
            foreground='#217346'
        )
        self.lbl_result_6.grid(
            row=4, column=0, padx=10, pady=(0, 20), sticky='nsew'
        )

    def material_calculation(self) -> None:
        """
        Расчет себестоимости и стоимости изделий из листового материала.
        """

        # Получение данных с интерфейса
        material_name = self.combo_mat.get()
        number_of_products = self.ent_num.get()
        gab_width = self.ent_width.get()
        gab_height = self.ent_height.get()
        discount = self.spin_discount_material.get()
        design_cost = self.ent_draw_overprice.get()

        try:  # Если поля заполнены корректно, выполняем расчет
            # Проверка и перевод введенных данных
            number_of_products = int(number_of_products)
            gab_width = int(float(gab_width))
            gab_height = int(float(gab_height))
            discount = int(discount)
            try:
                design_cost = int(float(design_cost))
            except (ValueError, TypeError) as e:
                AppLogger(
                    'SheetMaterialsTab.material_calculation',
                    'warning',
                    f'{e}: Поле ввода доплаты за макетирование не заполнено '
                    f'или заполнено неверно: {design_cost}'
                )
                design_cost = 0

            # Подсчет результатов
            # Количество изделий с листа
            total_3 = max(
                ContainerPacking(
                    gab_width, gab_height, material_name).figure_1(),
                ContainerPacking(
                    gab_width, gab_height, material_name).figure_2()
            )

            # Себестоимость одного изделия
            try:
                total_1 = ContainerPacking(gab_width, gab_height,
                                           material_name).get_price() / total_3
            except ZeroDivisionError as e:
                AppLogger(
                    'SheetMaterialsTab.material_calculation',
                    'warning',
                    f'При расчете себестоимости изделия возникло исключение '
                    f'"{e}": Количество изделий с листа равно 0.'
                )
                total_1 = 0.0

            # Себестоимость партии
            total_2 = total_1 * number_of_products

            # Потребное количество листов на партию
            try:
                total_4 = ceil(number_of_products / total_3)
            except ZeroDivisionError as e:
                AppLogger(
                    'SheetMaterialsTab.material_calculation',
                    'warning',
                    f'При расчете потребного количества листов на партию '
                    f'возникло исключение "{e}": Количество изделий '
                    f'с листа равно 0.'
                )
                total_4 = 0.0

            try:
                # Не забываем обнулять расчет при 0 штук изделий
                total_5 = Interpolation(material_name).get_cost(
                    gab_height,
                    gab_width,
                    number_of_products)
                if number_of_products == 0:
                    total_5 = 0
                else:
                    total_5 = self.round_method(
                        total_5 * ((100 - discount) / 100))

                total_6 = total_5 * number_of_products + design_cost

            except (ValueError, ZeroDivisionError) as e:
                AppLogger(
                    'SheetMaterialsTab.material_calculation',
                    'warning',
                    f'При расчете стоимости изделия и стоимости партии '
                    f'возникло исключение "{e}"'
                )
                total_5 = 0.0
                total_6 = 0.0

            # Вывод результатов
            self.lbl_result_1.config(
                text=f"Себестоимость одного изделия:"
                     f"  {total_1:_.0f}  руб/шт.".replace('_', ' ')
            )
            self.lbl_result_2.config(
                text=f"Себестоимость партии:"
                     f"  {total_2:_.0f}  руб.".replace('_', ' ')
            )
            self.lbl_result_3.config(
                text=f"Количество изделий с одного листа:"
                     f"  {total_3:_.0f}  шт.".replace('_', ' ')
            )
            self.lbl_result_4.config(
                text=f"Минимальное количество листов на партию:"
                     f"  {total_4:_.0f}  шт.".replace('_', ' ')
            )

            self.lbl_result_5.config(
                text=f"Стоимость изделия:"
                     f"  {total_5:_.0f}  руб/шт.".replace('_', ' ')
            )

            self.lbl_result_6.config(
                text=f"ИТОГОВАЯ СТОИМОСТЬ ПАРТИИ:"
                     f"  {total_6:_.0f}  руб.".replace('_', ' ')
            )
            self.lbl_result_7.config(
                text=f"Макетирование:"
                     f"  {design_cost:_.0f}  руб.".replace('_', ' ')
            )
            # Формируем параметры для сохранения расчёта в лог
            temp_list = [''] * 3
            temp_list[0] = f"Материал: {material_name}."
            temp_list[1] = f"Количество изделий: {number_of_products} шт."
            temp_list[2] = f"Габариты изделия: {gab_width} x {gab_height} мм."
            # Сохраняем расчёт в лог
            AppLogger(
                'SheetMaterialsTab.material_calculation',
                'calc',
                f'Произведен расчет на вкладке "Листовой материал"',
                _=temp_list[0],
                __=temp_list[1],
                ___=temp_list[2],
                ____=self.lbl_result_5.cget("text"),
                _____=self.lbl_result_7.cget("text"),
                ______=self.lbl_result_6.cget("text")
            )

        except ValueError as e:
            tk.messagebox.showerror(
                'Ошибка ввода данных!',
                'Данные не введены или введены некорректно.'
            )
            AppLogger(
                'SheetMaterialsTab.material_calculation',
                'error',
                f'При попытке расчета на вкладке "Листовой материал"'
                f'возникло исключение "{e}": '
                f'Данные не введены или введены некорректно.',
                info=True
            )

    def update_base(self) -> None:
        """
        Метод обновления списка (базы) листового материала после изменений
        в настройках.
        """
        # Обновление данных
        self.material_list = list()
        for n in Materials().get_mat_price():
            self.material_list.append(n)
        # Обновление выпадающего списка
        self.combo_mat['values'] = self.material_list
        self.update()

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса вкладки 'ЛИСТОВОЙ
        МАТЕРИАЛ'
        """
        BalloonTips(self.btn_get_cost_materials,
                    text=f'Для расчета можно использовать\n'
                         f'клавишу <Enter>.')
        BalloonTips(self.spin_discount_material,
                    text=f'Скидка оператора, %')
        BalloonTips(self.ent_width, text=f'Ширина изделия, мм')
        BalloonTips(self.ent_height, text=f'Высота изделия, мм')
        BalloonTips(self.ent_num, text=f'Количество изделий, шт')
        BalloonTips(self.ent_draw_overprice, text=f'Макетирование или '
                                                  f'стоимость\n'
                                                  f'дополнительных работ, руб')

    def add_binds(self) -> None:
        """
        Метод установки фонового текста в поля ввода класса вкладки
        'ЛИСТОВОЙ МАТЕРИАЛ' и связывание действий пользователя в интерфейсе
        приложения с командами.
        """

        BindEntry(self.ent_draw_overprice, text='Доп. плата / Макетирование, '
                                                'руб')
        BindEntry(self.ent_num, text='Количество изделий, шт')
        BindEntry(self.ent_width, text='Ширина изделия, мм')
        BindEntry(self.ent_height, text='Высота изделия, мм')

        # Обновление списка материалов после редактирования базы
        self.bind("<Enter>", self.bind_update_base)

    def bind_update_base(self, event=None) -> None:
        """
        Метод автономного обновления списка материалов после редактирования
        базы.
        :param event: Возвращение фокуса на вкладку после закрытия окна
        предварительной настройки материала
        """
        self.update_base()
        self.not_use = event


class IndustrialCalculateTab(ttk.Frame):
    """
    Класс конфигурации третьей вкладки "промышленный расчет" главного окна
    приложения. На вкладке осуществляется ориентировочный расчет времени
    работы оборудования, а также расчет стоимости работы от времени.

    Содержит методы: cost_calculation, time_calculation, bmp_calculation,
    add_binds, add_tips, bind_update_time_price, add_bmp_binds
    """
    def __init__(self, parent, round_method, settings):
        """
        Конфигурация и прорисовка третьей вкладки основного окна приложения
        "Промышленный расчет"
        :param parent: Экземпляр-родитель Notebook
        :param round_method: Метод округления результата (из класса App)
        :param settings: Переменная настроек (конфигурации) программы
        """
        # Инициализация и конфигурация отзывчивости вкладки
        super().__init__(parent)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

        # Создание переменной-метода округления результатов
        self.round_method = round_method
        # Создание переменной настроек программы
        self.main_settings = settings

        # Переменная для считывания событий
        self.not_use = None

        # Создание форм вкладки
        self.panel_time_industrial = ttk.LabelFrame(
            self,
            text="Расчет времени работы оборудования",
            padding=0
        )
        self.panel_time_industrial.grid(row=0, column=0, padx=(10, 20),
                                        pady=(10, 20), sticky="nsew")
        # Конфигурация форм вкладки
        self.panel_time_industrial.columnconfigure(index=0, weight=1)
        self.panel_time_industrial.columnconfigure(index=1, weight=2)
        self.panel_time_industrial.columnconfigure(index=2, weight=1)
        self.panel_time_industrial.columnconfigure(index=3, weight=2)
        self.panel_time_industrial.rowconfigure(index=0, weight=1)
        self.panel_time_industrial.rowconfigure(index=1, weight=1)
        self.panel_time_industrial.rowconfigure(index=2, weight=1)
        self.panel_time_industrial.rowconfigure(index=3, weight=1)
        self.panel_time_industrial.rowconfigure(index=4, weight=1)
        self.panel_time_industrial.rowconfigure(index=5, weight=1)
        self.panel_time_industrial.rowconfigure(index=6, weight=1)
        self.panel_time_industrial.rowconfigure(index=7, weight=1)
        self.panel_time_industrial.rowconfigure(index=8, weight=1)
        self.panel_time_industrial.rowconfigure(index=9, weight=1)

        # Виджеты времени работы оборудования
        # Поле ввода времени работы оборудования
        ttk.Label(self.panel_time_industrial, text='Время работы, мин.').grid(
            row=0, column=0, padx=(15, 0), pady=(10, 0), sticky='ew')
        self.ent_time_of_work = ttk.Entry(self.panel_time_industrial, width=35,
                                          takefocus=False)
        self.ent_time_of_work.grid(row=0, column=1, padx=5, pady=(10, 0),
                                   sticky='nsew')

        # Кнопка расчета стоимости работы оборудования
        self.btn_cost_calculate = ttk.Button(
            self.panel_time_industrial,
            text='Расчёт стоимости работы',
            command=self.cost_calculation
        )
        self.btn_cost_calculate.grid(
            row=0, column=2, padx=(10, 15), pady=(10, 0), sticky='nsew',
            columnspan=2)

        # Результат расчета стоимости работы оборудования
        self.lbl_result_cost = ttk.Label(
            self.panel_time_industrial,
            text=f"Итого: {0:.0f}  руб/шт.",
            font='Arial 14',
            foreground='#217346'
        )
        self.lbl_result_cost.grid(row=1, column=0, padx=(15, 0), pady=(5, 0),
                                  columnspan=4, sticky="ew")

        # Разделительная черта
        ttk.Separator(self.panel_time_industrial).grid(
            row=2, column=0, pady=0, columnspan=4, sticky='ew')

        # Виджеты предварительного расчета времени работы оборудования
        # Поле ввода ширины макета
        ttk.Label(self.panel_time_industrial,
                  text='Ширина макета, мм.').grid(
            row=3, column=0, padx=(15, 0), pady=0, sticky='ew')
        self.ent_width_grav = ttk.Entry(self.panel_time_industrial, width=35,
                                        takefocus=False)
        self.ent_width_grav.grid(
            row=3, column=1, padx=10, pady=10, sticky='nsew')

        # Поле ввода высоты макета
        ttk.Label(self.panel_time_industrial,
                  text='Высота макета, мм.').grid(
            row=4, column=0, padx=(15, 0), pady=0, sticky='ew')
        self.ent_height_grav = ttk.Entry(self.panel_time_industrial, width=35,
                                         takefocus=False)
        self.ent_height_grav.grid(
            row=4, column=1, padx=10, pady=10, sticky='nsew')

        # Поле ввода разрешения макета
        ttk.Label(self.panel_time_industrial,
                  text='Разрешение макета, лин/мм.').grid(
            row=5, column=0, padx=(15, 0), pady=0, sticky='ew')
        self.ent_dpi_grav = ttk.Entry(self.panel_time_industrial, width=35,
                                      takefocus=False)
        self.ent_dpi_grav.grid(
            row=5, column=1, padx=10, pady=10, sticky='nsew')

        # Поле ввода скорости гравировки
        ttk.Label(self.panel_time_industrial,
                  text='Скорость гравировки, мм/сек.').grid(
            row=3, column=2, padx=(15, 0), pady=0, sticky='ew')
        self.ent_speed_grav = ttk.Entry(self.panel_time_industrial,
                                        width=35, takefocus=False)
        self.ent_speed_grav.grid(
            row=3, column=3, padx=(10, 15), pady=10, sticky='nsew')

        # Поле ввода количества проходов
        ttk.Label(self.panel_time_industrial,
                  text='Количество проходов, шт.').grid(
            row=4, column=2, padx=(15, 0), pady=0, sticky='ew')
        self.ent_number_grav = ttk.Entry(self.panel_time_industrial,
                                         width=35, takefocus=False)
        self.ent_number_grav.grid(
            row=4, column=3, padx=(10, 15), pady=10, sticky='nsew')

        # Поле ввода количества проходов
        ttk.Label(self.panel_time_industrial,
                  text='Черных пикселей, шт.').grid(
            row=5, column=2, padx=(15, 0), pady=0, sticky='ew')
        self.ent_black_pixel = ttk.Entry(self.panel_time_industrial,
                                         width=35, takefocus=False)
        self.ent_black_pixel.grid(
            row=5, column=3, padx=(10, 15), pady=10, sticky='nsew')

        # Кнопка расчета времени работы оборудования
        self.btn_time_calculate = ttk.Button(
            self.panel_time_industrial,
            text='Расчёт времени работы оборудования',
            command=self.time_calculation
        )
        self.btn_time_calculate.grid(
            row=6, column=0, padx=(10, 15), pady=(10, 0), sticky='nsew',
            columnspan=3)

        # Кнопка расчета времени работы оборудования
        self.btn_ratio_info = ttk.Button(
            self.panel_time_industrial,
            text='Открыть .bmp файл',
            command=self.bmp_calculation
        )
        self.btn_ratio_info.grid(
            row=6, column=3, padx=(10, 15), pady=(10, 0), sticky='nsew',
            columnspan=3)

        # Виджеты вывода результатов расчета времени
        self.lbl_result_time_minimum = ttk.Label(
            self.panel_time_industrial,
            text=f"Ориентировочное время гравировки жирного текста и "
                 f"неплотных рисунков: {0:.2f}  мин.",
            font='Arial 13',
            foreground='#217346'
        )
        self.lbl_result_time_minimum.grid(row=7, column=0, padx=(15, 0),
                                          pady=0, columnspan=4, sticky="ew")

        self.lbl_result_time_text = ttk.Label(
            self.panel_time_industrial,
            text=f"Ориентировочное время гравировки неплотных рисунков и "
                 f"изображений из тонких линий: {0:.2f}  мин.",
            font='Arial 13',
            foreground='#217346'
        )
        self.lbl_result_time_text.grid(row=8, column=0, padx=(15, 0),
                                       pady=0, columnspan=4, sticky="ew")

        self.lbl_result_time_imagine = ttk.Label(
            self.panel_time_industrial,
            text=f"Ориентировочное время гравировки обычного текста и "
                 f"рисунков с большим количеством элементов: {0:.2f}  мин.",
            font='Arial 13',
            foreground='#217346'
        )
        self.lbl_result_time_imagine.grid(row=9, column=0, padx=(15, 0),
                                          pady=(0, 10),
                                          columnspan=4, sticky="ew")

    def cost_calculation(self) -> None:
        """
        Метод, реализующий расчет стоимости от времени работы оборудования.
        """
        try:  # Проверяем на то, что введено корректное число
            cost = (
                float(self.ent_time_of_work.get()) *
                int(self.main_settings['MAIN'][
                        'one_hour_of_work']) / 60

            )
            # Выводим результат
            self.lbl_result_cost.config(
                text=f"Итого:"
                     f"  {self.round_method(cost):_.0f}  руб/шт.".replace(
                          '_', ' ')
            )
            # Записываем расчет в лог
            AppLogger(
                "IndustrialCalculateTab.cost_calculation",
                'calc',
                f'Выполнен расчет стоимости от времени работы оборудования',
                _=f"Время работы оборудования:"
                  f" {self.ent_time_of_work.get()} мин.",
                __=self.lbl_result_cost.cget('text')
            )

        except ValueError as e:  # Если число некорректно
            # Обнуляем вывод результата
            self.lbl_result_cost.config(
                text=f"Итого:"
                     f" {0:.0f}  руб/шт."
            )
            AppLogger(
                "IndustrialCalculateTab.cost_calculation",
                'warning',
                f'При выполнении расчета стоимости от времени работы '
                f'оборудования возникло исключение: {e}'
            )

    def time_calculation(self) -> None:
        """
        Метод предварительного расчета времени работы оборудования.
        Формулы имеют вид:

        Результат = (ширина * высота * плотность * относительное количество
        черных пикселей в макете) / (скорость*60) +
        (ширина * высота * плотность * относительное количество
        белых пикселей в макете) / (скорость холостого хода*60), где:

            Относительное количество черных пикселей в макете = количество
            черных пикселей в макете / общее количество пикселей;
            Относительное количество белых пикселей в макете = количество
            белых пикселей в макете / общее количество пикселей;
            Скорость холостого хода = 4 000 мм/сек для стандартных настроек
            динамики.

        При этом время гравировки рисунка и текста будет разным:
        Время гравировки = Результат / поправочный коэффициент, где

            Поправочный коэффициент = 1.00 для первого случая (без поправки);
            Поправочный коэффициент = 0.75 для второго случая;
            Поправочный коэффициент = 0.65 для третьего случая.

        """
        try:
            # Формирование переменных (считывание данных с интерфейса)
            width_grav = float(self.ent_width_grav.get())
            height_grav = float(self.ent_height_grav.get())
            dpi_grav = float(self.ent_dpi_grav.get())
            speed_grav = float(self.ent_speed_grav.get())
            num_grav = float(self.ent_number_grav.get())
            black_pixels = float(self.ent_black_pixel.get())

            # Если пользователь не ввел количество пикселей, то считаем,
            # что планируется гравировать прямоугольник
            if black_pixels == 0:
                black_pixels = width_grav * height_grav * dpi_grav * dpi_grav
                white_pixels = 0
                flag_rectangle_grav = True
            else:  # Иначе считаем для макета
                flag_rectangle_grav = False
                white_pixels = (width_grav * dpi_grav * height_grav *
                                dpi_grav - black_pixels)
            result = (
                    ((width_grav * height_grav * dpi_grav * num_grav * (
                            black_pixels / (black_pixels + white_pixels)) /
                     speed_grav) / 60) + (
                        (width_grav * height_grav * dpi_grav * num_grav * (
                                white_pixels / (black_pixels +
                                                white_pixels)) / 4000) / 60
                    )
            )
            if flag_rectangle_grav:
                # Уравниваем результаты вывода для прямоугольника
                result_text = result_imagine = result
            else:
                # Считаем второй и третий случаи
                result_text = result / 0.75
                result_imagine = result / 0.65

            # Выводим результаты
            self.lbl_result_time_minimum.config(
                text=f"Ориентировочное время гравировки жирного текста и "
                     f"неплотных рисунков: {result:.2f}  мин."
            )

            self.lbl_result_time_text.config(
                text=f"Ориентировочное время гравировки неплотных рисунков и "
                     f"изображений из тонких линий: {result_text:.2f}  мин."
            )

            self.lbl_result_time_imagine.config(
                text=f"Ориентировочное время гравировки обычного текста и "
                     f"рисунков с большим количеством элементов:"
                     f" {result_imagine:.2f}  мин."
            )

            # Записываем расчеты в лог
            AppLogger(
                "IndustrialCalculateTab.time_calculation",
                'calc',
                f'Выполнен расчет времени работы оборудования',
                _=self.lbl_result_time_minimum.cget('text'),
                __=self.lbl_result_time_text.cget('text'),
                ___=self.lbl_result_time_imagine.cget('text')
            )

        except (ValueError, TypeError, ZeroDivisionError) as e:
            tk.messagebox.showerror(
                'Ошибка ввода данных!',
                'Данные не введены или введены некорректно.'
            )
            # Обнуляем результаты
            self.lbl_result_time_minimum.config(
                text=f"Ориентировочное время гравировки жирного текста и "
                     f"неплотных рисунков: {0:.2f}  мин."
            )

            self.lbl_result_time_text.config(
                text=f"Ориентировочное время гравировки неплотных рисунков и "
                     f"изображений из тонких линий: {0:.2f}  мин."
            )

            self.lbl_result_time_imagine.config(
                text=f"Ориентировочное время гравировки обычного текста и "
                     f"рисунков с большим количеством элементов: {0:.2f}  мин."
            )

            AppLogger(
                "IndustrialCalculateTab.time_calculation",
                'error',
                f'При выполнении расчета времени работы оборудования'
                f' возникло исключение: {e}',
                info=True
            )

    def bmp_calculation(self) -> None:
        """
        Метод открытия .bmp файла для подсчета в нем количества черных
        пикселей, разрешения и габаритов изображения.
        """
        # Открываем файл
        file_type = [("BMP Files", "*.bmp"), ]
        filename = fd.askopenfilename(filetypes=file_type)
        try:
            # Для выбранного файла определяем параметры
            bmp_image = MonochromeBMP(filename)
            _, black = bmp_image.count_pixels()
            width_bmp, height_bmp, dpi_bmp = bmp_image.get_image_info_in_mm()

            # Заполняем поля данными, полученными из БМП изображения
            self.ent_black_pixel.delete(0, tk.END)
            self.ent_width_grav.delete(0, tk.END)
            self.ent_height_grav.delete(0, tk.END)
            self.ent_dpi_grav.delete(0, tk.END)

            self.ent_black_pixel.insert(0, f'{black:.0f}')
            self.ent_width_grav.insert(0, f'{width_bmp:.1f}')
            self.ent_height_grav.insert(0, f'{height_bmp:.1f}')
            self.ent_dpi_grav.insert(0, f'{(dpi_bmp/25.4):.0f}')

            # Записываем данные в лог
            AppLogger(
                'IndustrialCalculateTab.bmp_calculation',
                'bmp',
                f'Выполнен расчет параметров растрового .bmp изображения:'
                f'{filename}:',
                _=f'Черных пикселей: {self.ent_black_pixel.get()}',
                __=f'Ширина макета: {self.ent_width_grav.get()}',
                ___=f'Высота макета: {self.ent_height_grav.get()}',
                ____=f'Разрешение макета: {self.ent_dpi_grav.get()}'
            )

        except (FileNotFoundError, TypeError) as e:
            # Обнуляем поля
            self.ent_black_pixel.delete(0, tk.END)
            self.ent_width_grav.delete(0, tk.END)
            self.ent_height_grav.delete(0, tk.END)
            self.ent_dpi_grav.delete(0, tk.END)

            # Добавляем фоновый текст в поля
            self.add_bmp_binds()

            AppLogger(
                "IndustrialCalculateTab.time_calc",
                'error',
                f'При выполнении расчета параметров растрового'
                f' .bmp изображения: "{filename}" возникло исключение: {e}',
                info=True
            )

    def add_binds(self) -> None:
        """
        Метод установки фонового текста в поля ввода вкладки
        'ПРОМЫШЛЕННЫЙ РАСЧЕТ' и связывание действий пользователя в интерфейсе
        приложения с командами.
        """
        # Добавление фонового текста
        BindEntry(self.ent_time_of_work, text='Время работы, мин')
        BindEntry(self.ent_speed_grav, text='Скорость гравировки, мм/сек')
        BindEntry(self.ent_number_grav, text='Количество проходов, шт')

        # Добавление команд
        self.bind("<Enter>", self.bind_update_time_price)
        self.add_bmp_binds()

    def bind_update_time_price(self, event=None) -> None:
        """
        Метод обновления стоимости времени работы оборудования после
        изменения настроек
        :param event:Возвращение фокуса на вкладку после закрытия окна
        предварительной настройки программы
        """
        self.main_settings = ConfigSet().config
        self.not_use = event

    def add_bmp_binds(self) -> None:
        """
        Метод установки фонового текста в поля ввода параметров изображения
        (макета).
        """
        BindEntry(self.ent_black_pixel, text='0')
        BindEntry(self.ent_width_grav, text='Ширина макета, мм')
        BindEntry(self.ent_height_grav, text='Высота макета, мм')
        BindEntry(self.ent_dpi_grav, text='Разрешение макета, лин/мм')

    def add_tips(self) -> None:
        """
        Метод добавления подсказок к элементам интерфейса вкладки 'ПРОМЫШЛЕННЫЙ
        РАСЧЕТ'
        """
        BalloonTips(self.ent_black_pixel,
                    text=f'Количество черных пикселей макета.')


if __name__ == "__main__":  # Запуск программы
    AppLogger(
        __name__,
        'info',
        f'Запуск программы.'
    )
    try:
        window = App()
        window.run()
    except Exception as exc:
        AppLogger(
            __name__,
            'error',
            f'При запуске программы возникло исключение: {exc}',
            info=True
        )

# Удаляем временный файл, который создается при просмотре расчётов через меню
try:
    if os.path.exists(
            PathName.resource_path("log/calculation/temp_calc_log.txt")):
        os.remove(PathName.resource_path("log/calculation/temp_calc_log.txt"))
except Exception as exc:
    AppLogger(
        __name__,
        'error',
        f'При удалении временного файла просмотра расчетов возникло '
        f'исключение {exc}',
        info=True
    )

AppLogger(
        __name__,
        'info',
        f'Закрытие программы.\n{"-"*100}'
)
