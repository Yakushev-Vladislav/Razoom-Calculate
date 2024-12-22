"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль содержит класс, отвечающий за установку фонового текста в поля ввода
интерфейса (BindEntry), а также класс установки подсказок к элементам
интерфейса (BalloonTips).

"""


from custom_hovertip import CustomTooltipLabel


class BindEntry:
    """
    Класс реализует установку фонового текста в поля ввода.

    Класс содержит методы to_add_entry_child, erase_entry_child.

    Пример использования:
    BindEntry(entry_widget_name, text='Фоновый текст поля ввода')
    """
    def __init__(self, widget, text: str = '-') -> None:
        """
        Непосредственно установка фонового текста в поля ввода.
        :param widget: Виджет, на который устанавливается фоновый текст.
        :param text: Передаваемый в виджет текст (по умолчанию '-').
        """
        self.text = text
        self.widget = widget
        self.not_use_child = None
        self.to_add_entry_child()

        self.widget.bind('<FocusIn>', self.erase_entry_child)
        self.widget.bind('<FocusOut>', self.to_add_entry_child)

    def to_add_entry_child(self, event=None) -> None:
        """
        Метод заполнения фоновым текстом при пустом поле ввода.
        :param event: Считывает выход из пустого поля ввода
        """
        if self.widget.get() == "":
            self.widget.insert(0, self.text)
            self.widget.config(foreground='grey')
        self.not_use_child = event

    def erase_entry_child(self, event=None) -> None:
        """
        Метод удаления фонового текста и добавления текста, введенного
        пользователем.
        :param event: Считывает выход из заполненного поля ввода
        """
        if self.widget.get() == self.text:
            self.widget.delete(0, 'end')
            self.widget.config(foreground='black')
        self.not_use_child = event


class BalloonTips:
    """
    Класс добавляющий подсказки к элементам интерфейса.

    Пример использования:
    BalloonTips(entry_widget_name, text='Подсказка к виджету')
    """
    def __init__(self, widget, text: str | None = None,
                 delay: int = 350) -> None:
        """
        Добавление всплывающей подсказки к элементам интерфейса.
        :param widget: Виджет, на который устанавливается подсказка.
        :param text: Текст, который выводится при наведении на виджет.
        :param delay: Задержка до появления подсказки (по умолчанию 0.35 сек.)
        """
        CustomTooltipLabel(anchor_widget=widget,
                           text=text,
                           background="white",
                           foreground='grey',
                           relief='flat',
                           hover_delay=delay
                           )
