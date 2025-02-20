"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль реализует работу с конфигурацией списка листового материала,
конфигурацией стоимостей изделий из выбранного листового материала,
алгоритмом упаковки в контейнере, а также интерполяцией стоимостей изделий.

Модуль содержит классы:
- Materials - реализует работу с файлом конфигурации списка листового
материала material_data.ini.
- ContainerPacking - реализует алгоритм упаковки в контейнере.
- Interpolation - реализует интерполяционный расчет стоимости изделия из
выбранного материала.
"""

import os
import shutil


import configparser

from app_logger import AppLogger
from path_getting import PathName
from settings_configuration import SettingsFileError


class Materials:
    """
    Класс реализует работу с файлом конфигурации списка листового материала
    material_data.ini. Реализует работу с файлами конфигурации стоимостей
    изделий из имеющихся листовых материалов.

    Содержит методы: get_mat_price, get_gab_width, get_gab_height,
    get_type_of_laser, update_materials, del_matrix_file, add_matrix_file,
    get_default.

    Пример использования:
    material_set = Materials()
    material_price = material_set.get_mat_price[material_name]
    ...
    # Манипуляции с файлом конфигурации (удаление/добавление элементов)
    ...
    # Сброс до настроек "По-умолчанию"
    material_set.get_default()
    """
    def __init__(self):

        """
        Инициализация переменной конфигурации и работы с файлом
        material_data.ini.
        """

        # Создание файла конфигурации
        self.material_config = configparser.ConfigParser()
        self.material_config.read(PathName.resource_path(
            'settings\\material_data.ini'), encoding='utf-8')

        # Проверяем файл настроек на целостность
        if self.material_config.sections() != ['INFO', 'MAIN']:
            raise SettingsFileError(
                f'Файл конфигурации material_data.ini нарушен, возможно он '
                f'был удалён или его структура изменена.',
                location='Materials.__init__'
            )

    def get_mat_price(self) -> dict:
        """
        Метод, возвращает словарь "Название - стоимость листа".
        :return: Словарь "Название - стоимость листа"
        """
        try:
            my_price = dict()
            for k, v in self.material_config['MAIN'].items():
                temp = [x for x in v.split(',')]
                my_price[k] = [float(x) for x in temp[0:3:1]][-1]
            return my_price
        except Exception as e:
            AppLogger(
                'Materials.get_mat_price',
                'error',
                f'При формировании словаря "Название-стоимость" для базы '
                f'материалов возникло исключение: {e}',
                info=True
            )

    def get_gab_width(self) -> dict:
        """
        Метод, возвращающий словарь "название - ширина листа"
        :return: Словарь "название - ширина листа"
        """
        try:
            mat_gab_width = dict()
            for k, v in self.material_config['MAIN'].items():
                temp = [x for x in v.split(',')]
                mat_gab_width[k] = [float(x) for x in temp[0:3:1]][0]
            return mat_gab_width
        except Exception as e:
            AppLogger(
                'Materials.get_gab_width',
                'error',
                f'При формировании словаря "Название-ширина листа" для базы '
                f'материалов возникло исключение: {e}',
                info=True
            )

    def get_gab_height(self) -> dict:
        """
        Метод, возвращающий словарь "название - высота листа"
        :return: Словарь "название - высота листа"
        """
        try:
            mat_gab_height = dict()
            for k, v in self.material_config['MAIN'].items():
                temp = [x for x in v.split(',')]
                mat_gab_height[k] = [float(x) for x in temp[0:3:1]][1]
            return mat_gab_height
        except Exception as e:
            AppLogger(
                'Materials.get_gab_height',
                'error',
                f'При формировании словаря "Название-высота листа" для базы '
                f'материалов возникло исключение: {e}',
                info=True
            )

    def get_type_of_laser(self) -> dict:
        """
        Метод, возвращающий словарь "название - тип оборудования"
        :return: Словарь "название - тип оборудования"
        """
        try:
            mat_type_of_laser = dict()
            for k, v in self.material_config['MAIN'].items():
                mat_type_of_laser[k] = [x for x in v.split(',')][-1]
            return mat_type_of_laser
        except Exception as e:
            AppLogger(
                'Materials.get_type_of_laser',
                'error',
                f'При формировании словаря "Название-тип оборудования" '
                f'для базы материалов возникло исключение: {e}',
                info=True
            )

    def update_materials(self, some_new=None) -> None:
        """
        Метод обновления файла конфигурации.
        :param some_new: Переменная конфигурации с новыми данными
        """
        if some_new:  # Добавление новых данных в файл конфигурации
            with (open(PathName.resource_path('settings\\material_data.ini'),
                       'w', encoding='utf-8') as configfile):
                some_new.write(configfile)
        else:
            with (open(PathName.resource_path('settings\\material_data.ini'),
                       'w', encoding='utf-8') as configfile):
                self.material_config.write(configfile)

    @staticmethod
    def del_matrix_file(material_name: str) -> None:
        """
        Метод удаления файла конфигурации с матрицей стоимости материала.
        :param material_name: Название материала/файла конфигурации.
        """
        try:
            file_path = PathName.resource_path(
                f'settings/materials\\{material_name}.ini')
            if os.path.isfile(file_path):
                os.remove(file_path)
        except FileNotFoundError as e:
            AppLogger(
                'Materials.del_matrix_file',
                'error',
                f'При удалении файла с матрицей стоимости материала'
                f' {material_name} возникло исключение: {e}',
                info=True
            )

    @staticmethod
    def add_matrix_file(material_name: str, laser_type: str) -> None:
        """
        Метод добавления файла конфигурации с матрицей стоимости материала.
        :param material_name: Название материала
        :param laser_type: Тип лазера
        """
        try:
            destination_path = PathName.resource_path(f'settings\\materials')
            file_new_name = PathName.resource_path(
                f'settings\\materials\\{material_name}.ini')

            # Если редактируем имеющийся материал
            if os.path.exists(PathName.resource_path(
                    f'settings\\materials\\{material_name}.ini')):
                pass

            # Если создаем новый материал
            else:
                if laser_type == 'gas':
                    source_path = PathName.resource_path(
                        'settings\\default\\materials\\default_gas.ini')
                    file_old_name = PathName.resource_path(
                        'settings\\materials\\default_gas.ini')
                else:
                    source_path = PathName.resource_path(
                        'settings\\default\\materials\\default_solid.ini')
                    file_old_name = PathName.resource_path(
                        'settings\\materials\\default_solid.ini')

                # Копируем файл в папку назначения
                shutil.copy(
                    source_path,
                    os.path.join(destination_path)
                )

                # Переименовываем файл
                os.rename(file_old_name, file_new_name)
        except Exception as e:
            AppLogger(
                'Materials.add_matrix_file',
                'error',
                f'При создании файла с матрицей стоимостей для нового '
                f'материала "{material_name}" возникло исключение: {e}'
            )

    @staticmethod
    def get_default() -> None:
        """
        Метод сброса файла конфигурации и стоимостей "по-умолчанию"
        """
        try:
            # Сброс основного файла конфигурации со списком материалов
            destination_path = PathName.resource_path(
                'settings\\material_data.ini')
            source_path = PathName.resource_path(
                'settings\\default\\material_data.ini')
            if os.path.exists(destination_path):
                os.remove(destination_path)
            shutil.copy2(source_path, destination_path)

            # Сброс файлов с матрицами стоимостей
            destination_path = PathName.resource_path('settings\\materials\\')
            source_path = PathName.resource_path(
                'settings\\default\\materials\\')
            deleted_files = os.listdir(destination_path)
            new_files = os.listdir(source_path)
            for file in deleted_files:
                os.remove(PathName.resource_path(
                    f'settings\\materials\\{file}'))
            for filename in new_files:
                shutil.copy(
                    PathName.resource_path(
                        f'settings\\default\\materials\\{filename}'),
                    PathName.resource_path(
                        f'settings\\materials\\{filename}')
                )

            # Удаление дефолтных файлов стоимостей для типов лазера
            laser_types = ['default_gas', 'default_solid']
            for item in laser_types:
                file_path = PathName.resource_path(
                    f'settings\\materials\\{item}.ini')
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            AppLogger(
                'Materials.get_default',
                'error',
                f'При сбросе файла конфигурации с базой листового материала '
                f'возникло исключение: {e}'
            )


class ContainerPacking:
    """
    Класс реализует алгоритм упаковки в контейнере.

    Содержит методы: figure_1, figure_2, get_price.

    Пример использования:
    first_packing = ContainerPacking(width, height, material_name).figure_1()
    second_packing = ContainerPacking(width, height, material_name).figure_2()
    max_quantity = max(first_packing, second_packing)
    """
    def __init__(self, width: int, height: int, mat_name: str):
        """
        Инициализация параметров для выбранного материала.
        :param width: Ширина изделия
        :param height: Высота изделия
        :param mat_name: Название материала
        """

        # Создание переменных
        self.figure_per_rows = 0
        self.figure_per_columns = 0
        self.total_1 = 0
        self.total_2 = 0

        # Получение габаритов листа с учетом коэффициента обрезков
        self.w_big = Materials().get_gab_width()[mat_name] * 0.9
        self.h_big = Materials().get_gab_height()[mat_name]
        self.width = width
        self.height = height

        # Получение стоимости выбранного материала (самого листа)
        self.price = Materials().get_mat_price()[mat_name]

    def figure_1(self) -> int:
        """
        Первый метод упаковки.
        :return: Возможное количество размещенных изделий на листе
        """
        try:
            # Проверка максимальной вместимости контейнера в строках и столбцах
            self.figure_per_rows = self.w_big // self.width
            self.figure_per_columns = self.h_big // self.height
            self.total_1 += int(self.figure_per_rows * self.figure_per_columns)

            # После заполнения строк проверяем вместимость оставшейся части
            # листа, при этом переворачиваем изделие и проверяем на вместимость
            if (self.w_big - (
                    self.figure_per_rows * self.width)) >= self.height:
                x_2 = (self.w_big
                       - (self.figure_per_rows * self.width)) // self.height
                y_2 = self.h_big // self.width
                self.total_1 += int(x_2 * y_2)
        except ZeroDivisionError as e:
            AppLogger(
                f'ContainerPacking.figure_1',
                'error',
                f'При упаковке в контейнер первым методом, возникло '
                f'исключение: {e} - возможно изделия не умещаются на листе '
                f'вообще. Либо количество изделий равно нулю.'
            )
            self.total_1 = 0
        # Возвращаем количество изделий с листа первым методом
        return self.total_1

    def figure_2(self) -> int:
        """
        Второй метод упаковки. Здесь заменены высота и ширина изделия друг
        на друга. Соответственно упаковываем повернутое на 90 градусов изделие
        :return: Возможное количество размещенных изделий на листе
        """
        try:
            # Проверка максимальной вместимости контейнера в строках и столбцах
            self.figure_per_rows = self.w_big // self.height
            self.figure_per_columns = self.h_big // self.width
            self.total_2 += int(self.figure_per_rows * self.figure_per_columns)

            # После заполнения строк проверяем вместимость оставшейся части
            # листа, при этом переворачиваем изделие и проверяем на вместимость
            if (self.w_big - (
                    self.figure_per_rows * self.height)) >= self.width:
                x_2 = (self.h_big
                       - (self.figure_per_rows * self.height)) // self.width
                y_2 = self.h_big // self.height
                self.total_2 += int(x_2 * y_2)

        except ZeroDivisionError as e:
            AppLogger(
                f'ContainerPacking.figure_2',
                'error',
                f'При упаковке в контейнер вторым методом, возникло '
                f'исключение: {e} - возможно изделия не умещаются на листе '
                f'вообще. Либо количество изделий равно нулю.'
            )
            self.total_2 = 0
        # Возвращаем количество изделий с листа вторым методом
        return self.total_2

    def get_price(self) -> int | float:
        """
        Интерфейсный метод возвращения себестоимости материала
        :return: Себестоимость материала
        """
        return self.price


class Interpolation:
    """
    Класс реализующий интерполяционный расчет стоимости изделия из
    выбранного листового материала.

    Содержит методы: get_laser_type, get_cost, get_keys, get_interpolation,
    update_matrix, get_default.

    Пример использования:
    total_cost = Interpolation(material_name).get_cost(height, width, number)

    """
    def __init__(self, file_name: str):
        """
        Инициализация переменной конфигурации и работы с файлом выбранного
        материала {file_name}.ini.
        :param file_name: Название материала (файла стоимостей)
        """
        self.matrix_config = configparser.ConfigParser()
        self.matrix_config.read(PathName.resource_path(
            f'settings\\materials\\{file_name}.ini'), encoding='utf-8')
        self.name = str(file_name)

        # Проверяем файл конфигурации на целостность
        if self.matrix_config.sections() != ['INFO', 'COSTS']:
            raise SettingsFileError(
                f'Файл конфигурации {file_name}.ini нарушен, возможно он '
                f'был удалён или его структура изменена.',
                location='Interpolation.__init__'
            )

    def get_laser_type(self) -> str:
        """
        Метод возвращает строковое значение типа лазера.
        :return: Тип лазера.
        """
        try:  # Корректны ли данные материала в файле конфигурации
            name = self.name
            laser_type_config = configparser.ConfigParser()
            laser_type_config.read(PathName.resource_path(
                'settings\\material_data.ini'), encoding='utf-8')
            laser_type = laser_type_config['MAIN'][str(name)].split(', ')[-1]
            del laser_type_config
            return laser_type
        except Exception as e:
            AppLogger(
                'Interpolation.get_laser_type',
                'error',
                f'При получении типа лазера для материала "{self.name}" '
                f'возникло исключение: {e}',
                info=True
            )

    def get_cost(self, height: int | float, width: int | float, num: int) ->\
            float:
        """
        Метод получения стоимости изделия.
        :param height: Высота изделия
        :param width: Ширина изделия
        :param num: Количество изделий
        :return: Стоимость одного изделия
        """
        temp_cost_config = self.matrix_config['COSTS']

        # Список хранящий количество изделий в партии
        numbering_list = [1, 5, 15, 50, 150, 500, 1000]

        # Получаем граничные строки для нашего изделия
        lower_and_bigger_key = self.get_keys(height, width)

        # Определяем границы количества изделий
        lower_index = 0
        bigger_index = -1
        for item in numbering_list:
            if numbering_list[lower_index] <= item <= num:
                lower_index = numbering_list.index(item)
            if numbering_list[bigger_index] >= item >= num:
                bigger_index = numbering_list.index(item)

        # Если попали в точку, либо вне строк (супер маленькое/большое изделие)
        if type(lower_and_bigger_key) is not list:
            # Список цен для выбранного габарита (и негабаритного изделия)
            cost_list = [int(x) for x in temp_cost_config[
                lower_and_bigger_key].split(', ')]

            return self.get_interpolation(
                num,
                [numbering_list[lower_index], cost_list[lower_index]],
                [numbering_list[bigger_index], cost_list[bigger_index]]
            )

        # Если наша точка между имеющимися габаритами
        else:
            # Создаем списки цен для большей и меньшей строк (габаритов)
            cost_lower_list = [int(x) for x in temp_cost_config[
                lower_and_bigger_key[0]].split(', ')]
            cost_bigger_list = [int(x) for x in temp_cost_config[
                lower_and_bigger_key[-1]].split(', ')]
            # Для списка получаем цену изделия с учетом нужного количества
            lower_cost = self.get_interpolation(
                num,
                [numbering_list[lower_index], cost_lower_list[lower_index]],
                [numbering_list[bigger_index], cost_lower_list[bigger_index]]
            )
            bigger_cost = self.get_interpolation(
                num,
                [numbering_list[lower_index], cost_bigger_list[lower_index]],
                [numbering_list[bigger_index], cost_bigger_list[bigger_index]]
            )
            # Интерполируем между строками (габаритами)
            lower_area = (int(lower_and_bigger_key[0].split(', ')[1]) * int(
                lower_and_bigger_key[0].split(', ')[-1]))
            bigger_area = (int(lower_and_bigger_key[1].split(', ')[1]) * int(
                lower_and_bigger_key[1].split(', ')[-1]))
            return self.get_interpolation(
                width*height,
                [lower_area, lower_cost],
                [bigger_area, bigger_cost]
            )

    def get_keys(self, width: int | float, height: int | float) -> str | list:
        """
        Метод получения строк-ключей для ближайшего большего и меньшего
        габаритов.
        :param width: Ширина изделия
        :param height: Высота изделия
        :return: Список строк (ключей) для ближайшего большего и меньшего
        габаритов.
        """

        temp_matrix = self.matrix_config['COSTS']

        # Начальные значения верхней и нижней границ
        lower_key = ['', '1_000_000', '1_000_000']
        bigger_key = ['', '0', '0']

        # Принимаем из файла значения верхней и нижней границы для материала
        for key in temp_matrix.keys():
            temp_key = key.split(', ')
            if float(temp_key[1]) * float(temp_key[2]) <= (
                    float(lower_key[1]) * float(lower_key[2])):
                lower_key = key.split(', ')
            if float(temp_key[1]) * float(temp_key[2]) >= (
                    float(bigger_key[1]) * float(bigger_key[2])):
                bigger_key = key.split(', ')

        # Считаем площадь
        area = width * height
        key_get_point = False

        # Получаем для наших габаритов нижнюю и верхнюю границу:
        for k, v in temp_matrix.items():
            temp = k.split(', ')

            # Если попали в точку
            if int(temp[1]) * int(temp[2]) == area:
                key_get_point = True
                lower_key = k.split(', ')
                break

            # Нижняя точка
            if int(temp[1]) * int(temp[2]) < area and (
                    (int(temp[1]) * int(temp[2])) >= (int(lower_key[1]) * int(
                    lower_key[2]))):
                lower_key = k.split(', ')
            # Верхняя точка
            if int(temp[1]) * int(temp[2]) >= area and (
                    (int(temp[1]) * int(temp[2])) <= (int(bigger_key[1]) * int(
                    bigger_key[2]))):
                bigger_key = k.split(', ')

        # Если попали в точку
        if key_get_point:
            return ', '.join(lower_key)

        # Если за границами точек
        elif lower_key == bigger_key:
            AppLogger(
                'Interpolation.get_keys',
                'info',
                f'Изделие с габаритами: {(width, height)} вне расчетных '
                f'габаритов, поэтому для расчета были приняты габариты: '
                f'{(", ".join(lower_key[1::]))}.'
            )
            return ', '.join(lower_key)

        # Если в границах точек
        else:
            return [', '.join(lower_key), ', '.join(bigger_key)]

    @staticmethod
    def get_interpolation(point: int | float,
                          lower_point: list,
                          bigger_point: list) -> float | int:
        """
        Метод интерполяции значений между двумя точками.
        Формула интерполяции имеет вид:
            result = (|p-x_2|/|x_2-x_1|)*y_1 + (|p-x_1|/|x_2-x_1|)*y_2,

            где (x_1, y_1) - нижняя точка и ее значение;
                (x_2, y_2) - верхняя точка и ее значение;
                p - искомая точка.
        :param point: Передаваемая искомая точка
        :param lower_point: Ближайшая нижняя точка и ее значение;
        :param bigger_point: Ближайшая верхняя точка и ее значение;
        :return: Значение (цены, размера и др.) для искомой точки.
        """
        try:
            # Если границы равны (точка)
            if lower_point == bigger_point:
                result = lower_point[1]
            else:  # Иначе - диапазон
                lower_diff = abs(
                    int(point) - int(lower_point[0])
                ) / abs((int(bigger_point[0]) - int(lower_point[0])))
                bigger_diff = abs(
                    int(point) - int(bigger_point[0])
                ) / abs((int(bigger_point[0]) - int(lower_point[0])))

                result = (
                    lower_diff * bigger_point[1] + bigger_diff * lower_point[1]
                )
        except ValueError as e:
            AppLogger(
                'Interpolation.get_interpolation',
                'error',
                f'При интерполяции значений возникло исключение: {e} - '
                f'вероятно, переданы неправильные значения"'
                f'\n{lower_point}\n{bigger_point}',
                info=True
            )
            result = 0

        return result

    def update_matrix(self, some_new=None) -> None:
        """
        Метод обновления файла конфигурации стоимостей изделий из выбранного
        листового материала.
        :param some_new: Переменная конфигурации с новыми данными
        """
        if some_new:  # Обновляем файл конфигурации
            with (open(PathName.resource_path(
                    f'settings\\materials\\{self.name}.ini'), 'w',
                       encoding='utf-8') as configfile):
                some_new.write(configfile)
        else:
            with (open(PathName.resource_path(
                    f'settings\\materials\\{self.name}.ini'), 'w',
                       encoding='utf-8') as configfile):
                self.matrix_config.write(configfile)

    def get_default(self) -> None:
        """
        Метод сброса матрицы стоимости до настроек "по-умолчанию".
        """
        try:
            # Сохраняем в переменные путь к файлам конфигурации
            destination_path = PathName.resource_path(
                f'settings\\materials\\{self.name}.ini')
            source_path = PathName.resource_path(
                f'settings\\default\\materials\\{self.name}.ini')

            # Удаляем действующий файл конфигурации
            if os.path.exists(destination_path):
                os.remove(destination_path)

            # Если изделие стандартное
            if os.path.exists(source_path):
                shutil.copy2(source_path, destination_path)

            # Если изделие нестандартное, то меняем путь к файлу по-умолчанию
            else:
                destination_path = PathName.resource_path(
                    f'settings\\materials')
                file_new_name = PathName.resource_path(
                    f'settings\\materials\\{self.name}.ini')
                if self.get_laser_type() == 'gas':
                    source_path = PathName.resource_path(
                        'settings\\default\\materials\\default_gas.ini')
                    file_old_name = PathName.resource_path(
                        'settings\\materials\\default_gas.ini')
                else:
                    source_path = PathName.resource_path(
                        'settings\\default\\materials\\default_solid.ini')
                    file_old_name = PathName.resource_path(
                        'settings\\materials\\default_solid.ini')

                # Копируем файл в папку назначения
                shutil.copy(
                    source_path,
                    os.path.join(destination_path)
                )

                # Переименовываем файл
                os.rename(file_old_name, file_new_name)

        except Exception as e:
            AppLogger(
                'Interpolation.get_default',
                'error',
                f'При сбросе матрицы стоимостей материала "{self.name}" до '
                f'настроек "По-умолчанию" возникло исключение: {e}',
                info=True
            )
