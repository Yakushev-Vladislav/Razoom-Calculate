"""
All files in this repository are licensed under the Apache License, Version
2.0. See the LICENSE and NOTICE file for details.
_______________________________________________________________________________
Модуль содержит классы:

- RatioArea - реализация линейной и квадратичной зависимости для расчета
коэффициента увеличения стоимости в зависимости от размеров гравировки;
- DeepEngraving - работа с параметрами глубокой гравировки.
"""

from app_logger import AppLogger
from settings_configuration import DepthSet


class RatioArea:
    """
    Класс реализует линейную и квадратичную зависимость для расчета
    коэффициента увеличения стоимости в зависимости от размеров гравировки.

    Содержит методы:get_linear_ratio, get_polynomial_ratio.

    Примеры использования:
    RatioArea(area_min, area_max, ratio_max).get_linear_ratio(current_area)
    RatioArea(area_min, area_max, ratio_max).get_polynomial(current_area)
    """
    def __init__(self, area_min: int | float, area_max: int | float,
                 ratio_max: int | float, ratio_min: int | float = 1) -> None:
        """
        Инициализация переменных.
        :param area_min: Максимальная площадь без доплаты
        :param area_max: Максимальная площадь полного поля станка
        :param ratio_max: Максимальный коэффициент для полного поля
        :param ratio_min: Минимальный коэффициент стандартной работы
        """
        self.area_min = area_min
        self.area_max = area_max
        self.ratio_max = ratio_max
        self.ratio_min = ratio_min

    def get_linear_ratio(self, area: int | float) -> float:
        """
        Метод реализации линейной зависимости по каноническому уравнению прямой
        :param area: Площадь гравировки
        :return: Коэффициент доплаты
        """
        try:
            # Если площадь меньше, чем нижний порог
            if area <= self.area_min:
                return float(self.ratio_min)
            # Если площадь больше, чем верхний порог
            elif area >= self.area_max:
                return float(self.ratio_max)
            else:  # Если площадь входит в диапазон
                return float(
                    (((area - self.area_min) * abs(
                        self.ratio_max-self.ratio_min)) / (
                        self.area_max - self.area_min)) + self.ratio_min
                )
        except (ValueError, TypeError) as e:
            AppLogger(
                'RatioArea.get_linear_ratio',
                'error',
                f'При подсчете реализации линейной зависимости, для расчета '
                f'коэффициента увеличения стоимости от размеров гравировки, '
                f'возникло исключение: {e}',
                info=True
            )
            return 1.0

    def get_polynomial_ratio(self, area: int | float) -> float:
        """
        Метод реализации квадратичной зависимости.
        :param area: Площадь гравировки
        :return: Коэффициент доплаты
        """
        try:
            # Если площадь меньше, чем нижний порог
            if area <= self.area_min:
                return float(self.ratio_min)
            # Если площадь больше, чем верхний порог
            elif area >= self.area_max:
                return float(self.ratio_max)
            else:  # Если площадь входит в диапазон
                return float(
                    ((self.ratio_max - self.ratio_min) / (
                            (self.area_max - self.area_min) ** 2)) * (
                        (area - self.area_min) ** 2) + self.ratio_min
                )
        except (ValueError, TypeError) as e:
            AppLogger(
                'RatioArea.get_polynomial_ratio',
                'error',
                f'При подсчете реализации квадратичной зависимости, '
                f'для расчета коэффициента увеличения стоимости от размеров'
                f' гравировки, возникло исключение: {e}',
                info=True
            )


class DeepEngraving:
    """
    Класс обеспечивает расчет параметров глубокой гравировки для выбранного
    материала.

    Содержит методы:depth_calculate.

    Пример использования:
    powers = DeepEngraving(material_name).depth_calculate(depth=required_depth)

    """
    def __init__(self, material_name: str = None) -> None:
        """
        Создание переменной конфигурации глубокой гравировки.
        :param material_name: Название материала.
        """
        self.material_name = material_name
        self.config = DepthSet().config

    def depth_calculate(self, depth: float | int) -> list:
        """
        Метод возвращает количество проходов для выбранного материала с
        указанной глубиной гравировки.
        УРПОЩЕННАЯ ФОРМУЛА:
            y = (x/a)*b,
        где y - итоговое количество проходов, шт.;
            x - потребная глубина гравировки, мм;
            а - заданная стандартная глубина (выбранный шаг для материала), мм;
            b - количество проходов [шт.], при котором достигается глубина а.
        :param depth: Потребная глубина гравировки.
        :return: Количество проходов.
        """
        try:  # Существует ли такой материл / корректны ли данные
            set_depth = [
                float(x) for x in self.config['MAIN'][
                    self.material_name].split(", ")
            ]
            depth = float(depth)

        except (KeyError, TypeError, ValueError) as e:
            AppLogger(
                'DeepEngraving.depth_calculate',
                'error',
                f'При подсчете количества проходов глубокой гравировки для '
                f'материала "{self.material_name}" возникло исключение {e}',
                info=True
            )
        else:
            if depth <= set_depth[0]:  # Если смена фокуса не требуется
                result = int((depth / set_depth[0]) * set_depth[1])
                comment = 'Смена фокуса не требуется!'
                power_list = []

            else:
                # Количество смен фокуса
                count_changes = int(depth // set_depth[0])
                if (remnant := depth % set_depth[0]) == 0:
                    # Глубина кратна стандартной => смены фокуса в конце нет
                    result = ((count_changes * set_depth[1]) +
                              int((remnant / set_depth[0]) * set_depth[1]))
                    count_changes -= 1
                    ending = int(set_depth[1])
                else:
                    result = ((count_changes * set_depth[1]) +
                              int((remnant / set_depth[0]) * set_depth[1]))
                    ending = int((remnant / set_depth[0]) * set_depth[1])

                # Формирование комментария по алгоритму гравировки
                comment = "Требуется смена фокуса!"
                power_list = [count_changes,
                              set_depth[1],
                              set_depth[0],
                              ending]

            return [comment, result, power_list]
