"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль содержит класс OpenUrl для работы со списком дополнительных ресурсов
программы. Методы класса позволяют настраивать конфигурацию ресурсов,
а также открывать выбранный ресурс в веб-браузере.
"""

import os
import shutil
from webbrowser import open as web_open

import configparser

from app_logger import AppLogger
from path_getting import PathName


class OpenUrl:
    """
    Класс работы с файлом конфигурации URL-ссылок, а также открытием
    URL-ссылок в веб браузере.

    Содержит методы: get_url_dict, open_url, add_new_data, get_default.

    Пример использования:
    OpenUrl().open_url(resource_name)
    """

    def __init__(self) -> None:
        """
        Инициализация переменной конфигурации и работы с файлом url_data.ini.
        """

        # Создание/открытие файла конфигурации
        self.url_config = configparser.ConfigParser()
        self.url_config.read(PathName.resource_path(
            'settings\\url_data.ini'), encoding='utf-8')

    def get_url_dict(self) -> dict:
        """
        Метод получения словаря имеющихся в файле конфигурации ссылок с
        наименованиями ресурса.
        :return: Словарь {Название ресурса: ссылка}
        """
        # Создаем словарь
        url_dict = dict()

        try:
            # Заполняем словарь данными из файла конфигурации
            for k, v in self.url_config['MAIN'].items():
                url_dict[k] = v

        except Exception as e:
            AppLogger(
                "OpenUrl.get_url_dict",
                "error",
                f"Во время создания словаря дополнительных ресурсов, возникло "
                f"исключение:"
                f" {e}",
                info=True
            )
        return url_dict

    def open_url(self, name: str) -> None:
        """
        Метод открытия ссылки на ресурс в веб браузере.
        :param name: Название ресурса
        """
        # Получаем словарь ресурсов и их ссылок
        urls = self.get_url_dict()

        try:
            # Открываем ресурс в браузере
            web_open(urls[name])
            AppLogger(
                "OpenUrl.open_url",
                "info",
                f"Открыт ресурс {name}."
            )
        except (KeyError, ValueError) as e:
            AppLogger(
                "OpenUrl.open_url",
                "error",
                f"Во время открытия ресурса {name}, возникло исключение: {e}",
                info=True
            )

    def add_new_data(self, some_new=None) -> None:
        """
        Метод добавления данных в файл конфигурации.
        :param some_new: Переменная конфигурации с новыми данными
        """
        if some_new:
            # Запись новых данных
            with (open(PathName.resource_path('settings\\url_data.ini'),
                       'w', encoding='utf-8') as configfile):
                some_new.write(configfile)
        else:
            with (open(PathName.resource_path('settings\\url_data.ini'),
                       'w', encoding='utf-8') as configfile):
                self.url_config.write(configfile)

    @staticmethod
    def get_default() -> None:
        """
        Метод сброса файла конфигурации до настроек "По-умолчанию".
        """
        # Определяем путь к файлу и файлу с настройками "По-умолчанию"
        destination_path = PathName.resource_path('settings\\url_data.ini')
        source_path = PathName.resource_path('settings\\default\\url_data.ini')

        # Заменяем файл на файл с настройками "По-умолчанию"
        if os.path.exists(destination_path):
            os.remove(destination_path)
        shutil.copy2(source_path, destination_path)
