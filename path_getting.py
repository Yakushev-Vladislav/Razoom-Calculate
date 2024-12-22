"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль содержит класс PathName по работе (получению) абсолютного пути к ресурсу
(файлу), для корректной работы приложения и создания исполняемого файла .exe
"""

import os
import sys


# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
class PathName:
    """
    Класс реализует получение абсолютного пути к ресурсу (файлу),
    для корректной работы приложения и создания исполняемого файла .exe

    Содержит метод: resource_path

    Пример использования:
    patho_to_file = PathName.resource_path(relative_path)
    """
    def __init__(self):
        """
        Get absolute path to resource, works for dev and for PyInstaller
        """
        pass

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and for PyInstaller
        :param relative_path: relative path
        :return: os relative path
        """

        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS2
            base_path = sys._MEIPASS2

        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
