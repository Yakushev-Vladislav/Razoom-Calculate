"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль содержит базовый класс организации работы с файлами конфигурации
программы. Файлы конфигурации имеют формат .ini и работа с ними организована с
помощью библиотеки configparser. Также в модуле находятся дочерние классы,
инициализирующие работу с определенными файлами конфигурации программы.

Также модуль содержит класс-исключение SettingsFileError для обозначения
ошибки при работе с файлом конфигурации в случае, когда нарушена его структура.

Классы модуля:
- Configuration - класс родитель, функционал которого наследуют классы:
    > ConfigSet - реализует работу с файлом конфигурации предварительной
    настройки программы.
    > StandardSet - реализует работу с файлом конфигурации списка стандартных
    работ.
    > DepthSet - реализует работу с файлом конфигурации расчетов глубокой
    гравировки.

- SettingsFileError - класс-исключение.
"""

import os
import shutil

import configparser

from app_logger import AppLogger
from path_getting import PathName


class SettingsFileError(Exception):
    """
    Класс-исключение SettingsFileError для обозначения ошибки при работе с
    файлом конфигурации в случае, когда нарушена его структура.
    Пример использования:
    raise SettingsFileError(message=text; location:method_name)
    """

    def __init__(self, message: str, location: str) -> None:
        """
        Инициализация исключения
        :param message: Текст ошибки
        """
        super().__init__(message)

        # Записываем ошибку в лог приложения
        AppLogger(
            location,
            'error',
            message
        )


class Configuration:
    """
    Класс-родитель, реализующий работу с файлом конфигурации настроек
    программы .ini формата.

    Содержит методы добавления (обновления данных), а также сброса файла
    конфигурации до базовых настроек: update_settings, default_settings.

    При инициализации класса в классе-наследнике, необходимо передать имя
    файла, с которым класс-наследник работает.

    Например, для класса работы с файлом hello_world.ini инициализатор такой:
    def __init__(self):
        super().__init__(file_name='hello_world')
    """
    def __init__(self, file_name: str) -> None:
        """
        Инициализация переменной конфигурации и работы с файлом file_name.ini.
        """
        # Определение переменной имени файла
        self.file_name = file_name

        # Чтение файла конфигурации
        self.config = configparser.ConfigParser()
        self.config.read(
            PathName.resource_path(f'settings\\{self.file_name}.ini'),
            encoding='utf-8')

    def update_settings(self, some_new=None) -> None:
        """
        Обновления файла конфигурации и внесение в него изменений (при их
        наличии)
        :param some_new: Измененные данные для сохранения. При отсутствии
        изменений, файл остается нетронутым.
        """
        if some_new:  # Запись новых данных
            with (open(PathName.resource_path(
                    f'settings\\{self.file_name}.ini'), 'w',
                    encoding='utf-8') as configfile):
                some_new.write(configfile)
        else:
            with (open(PathName.resource_path(
                    f'settings\\{self.file_name}.ini'), 'w',
                    encoding='utf-8') as configfile):
                self.config.write(configfile)

    def default_settings(self) -> None:
        """
        Метод сброса настроек программы (файла конфигурации) до базовых
        (Сброс "По-умолчанию")
        """
        destination_path = PathName.resource_path(
            f'settings\\{self.file_name}.ini')
        source_path = PathName.resource_path(
            f'settings\\default\\{self.file_name}.ini')
        if os.path.exists(destination_path):
            os.remove(destination_path)
        shutil.copy2(source_path, destination_path)


class ConfigSet(Configuration):
    """
    Класс-наследник, реализующий работу с файлом конфигурации предварительной
    настройки программы settings.ini.

    Наследует методы базового класса: update_settings, default_settings.

    Пример использования:
    main_settings = ConfigSet()
    main_settings.update_settings(some_new=data)
    main_settings.default_settings()
    """
    def __init__(self) -> None:
        """
        Инициализация переменной конфигурации и работы с файлом settings.ini.
        """
        super().__init__(file_name="settings")
        if (self.config.sections() !=
                ['INFO', 'MAIN', 'RATIO_SETTINGS', 'GRADATION']):
            raise SettingsFileError(
                f'Файл конфигурации settings.ini нарушен, возможно он '
                f'был удалён или его структура изменена.',
                location='ConfigSet.__init__'
            )


class StandardSet(Configuration):
    """
    Класс-наследник, реализующий работу с файлом конфигурации списка
    стандартных работ standard.ini.

    Наследует методы базового класса: update_settings, default_settings.

    Пример использования:
    standard_settings = StandardSet()
    standard_settings.update_settings(some_new=data)
    standard_settings.default_settings()
    """
    def __init__(self) -> None:
        """
        Инициализация переменной конфигурации и работы с файлом standard.ini.
        """
        # Чтение файла конфигурации
        super().__init__(file_name="standard")

        # Проверка файла на целостность структуры
        if (self.config.sections() !=
                ['INFO', 'STANDARD']):
            raise SettingsFileError(
                f'Файл конфигурации standard.ini нарушен, возможно он '
                f'был удалён или его структура изменена.',
                location='StandardSet.__init__'
            )


class DepthSet(Configuration):
    """
    Класс-наследник, реализующий работу с файлом конфигурации расчетов глубокой
    гравировки deep_engraving.ini

    Наследует методы базового класса: update_settings, default_settings.
    Содержит собственный метод: get_materials_list.

    Пример использования:
    depth_settings = DepthSet()
    depth_settings.update_settings(some_new=data)
    depth_settings.default_settings()
    """
    def __init__(self):
        """
        Инициализация переменной конфигурации и работы с файлом
        deep_engraving.ini.
        """
        # Создание файла конфигурации
        super().__init__(file_name="deep_engraving")

        # Проверка файла на целостность структуры
        if (self.config.sections() !=
                ['INFO', 'MAIN']):
            raise SettingsFileError(
                f'Файл конфигурации deep_engraving.ini нарушен, возможно он '
                f'был удалён или его структура изменена.',
                location='DepthSet.__init__'
            )

    def get_materials_list(self) -> list:
        """
        Метод получения списка материалов из файла конфигурации.
        :return: Список с названиями материалов.
        """
        materials_list = list()
        try:
            for key in self.config['MAIN'].keys():
                materials_list.append(key)
        except (KeyError, ValueError, FileNotFoundError) as e:
            AppLogger(
                'DepthSet.get_materials_list',
                'error',
                f'При получении списка материалов для расчета глубокой '
                f'гравировки возникло исключение {e}',
                info=True
            )
        return materials_list
