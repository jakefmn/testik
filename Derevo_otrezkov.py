"""
Семестровая работа №2
Тема: дерево отрезков

Идея программы простая:
- создаём 10000 случайных целых чисел;
- добавляем их в дерево отрезков;
- ищем 100 случайно выбранных чисел;
- удаляем 1000 случайно выбранных чисел;
- для каждой операции сохраняем время и количество операций.

В моей работе дерево отрезков хранит частоты чисел.
Например, если число 25 встретилось 3 раза, то в листе для числа 25 будет храниться 3.
Так проще сделать методы add, delete и search для целых чисел.
"""

import csv
import random
import time
from dataclasses import dataclass
from statistics import mean


@dataclass
class OperationResult:
    """Маленький класс, чтобы удобно хранить результат одной операции."""
    operation: str
    number: int
    time_ns: int
    operations_count: int
    success: bool


class SegmentTree:
    """Простое дерево отрезков для хранения целых чисел.

    Мы заранее знаем, что числа будут от 0 до max_value.
    Дерево хранит не сами числа подряд, а количество каждого числа.
    Если число есть в структуре, его частота больше нуля.
    """

    def __init__(self, max_value: int):
        self.max_value = max_value

        # Размер дерева удобнее сделать степенью двойки.
        # Например, для 10000 значений ближайшая степень двойки будет 16384.
        self.size = 1
        while self.size <= max_value:
            self.size *= 2

        # В массиве tree хранятся суммы частот на отрезках.
        # tree[1] — корень, он хранит общее количество добавленных чисел.
        self.tree = [0] * (2 * self.size)

    def add(self, value: int) -> int:
        """Добавляет число в дерево и возвращает количество операций.

        Операцией здесь считаем посещение одной вершины дерева.
        """
        if value < 0 or value > self.max_value:
            return 0
        return self._add(1, 0, self.size - 1, value)

    def _add(self, node: int, left: int, right: int, value: int) -> int:
        # Мы пришли в одну вершину, значит считаем одну операцию.
        operations = 1

        # Если дошли до листа, значит нашли место конкретного числа.
        if left == right:
            self.tree[node] += 1
            return operations

        mid = (left + right) // 2

        # Идём только в ту половину, где находится наше число.
        if value <= mid:
            operations += self._add(node * 2, left, mid, value)
        else:
            operations += self._add(node * 2 + 1, mid + 1, right, value)

        # После изменения листа обновляем сумму в текущей вершине.
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]
        return operations

    def search(self, value: int) -> tuple[bool, int]:
        """Ищет число в дереве.

        Возвращает два значения:
        - найдено ли число;
        - сколько вершин дерева было просмотрено.
        """
        if value < 0 or value > self.max_value:
            return False, 0
        return self._search(1, 0, self.size - 1, value)

    def _search(self, node: int, left: int, right: int, value: int) -> tuple[bool, int]:
        operations = 1

        # Если пришли в лист, проверяем частоту этого числа.
        if left == right:
            return self.tree[node] > 0, operations

        mid = (left + right) // 2

        # Так же, как при добавлении, идём только в нужную половину.
        if value <= mid:
            found, child_operations = self._search(node * 2, left, mid, value)
        else:
            found, child_operations = self._search(node * 2 + 1, mid + 1, right, value)

        operations += child_operations
        return found, operations

    def delete(self, value: int) -> tuple[bool, int]:
        """Удаляет одно вхождение числа из дерева.

        Если число было добавлено несколько раз, удаляется только одно вхождение.
        Если числа нет, дерево не меняется.
        """
        if value < 0 or value > self.max_value:
            return False, 0
        return self._delete(1, 0, self.size - 1, value)

    def _delete(self, node: int, left: int, right: int, value: int) -> tuple[bool, int]:
        operations = 1

        if left == right:
            if self.tree[node] > 0:
                self.tree[node] -= 1
                return True, operations
            return False, operations

        mid = (left + right) // 2

        if value <= mid:
            deleted, child_operations = self._delete(node * 2, left, mid, value)
        else:
            deleted, child_operations = self._delete(node * 2 + 1, mid + 1, right, value)

        operations += child_operations

        # Если удаление получилось, надо обновить сумму в текущей вершине.
        if deleted:
            self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

        return deleted, operations


def measure_add(tree: SegmentTree, number: int) -> OperationResult:
    """Замеряет добавление одного числа."""
    start = time.perf_counter_ns()
    operations_count = tree.add(number)
    finish = time.perf_counter_ns()
    return OperationResult("add", number, finish - start, operations_count, True)


def measure_search(tree: SegmentTree, number: int) -> OperationResult:
    """Замеряет поиск одного числа."""
    start = time.perf_counter_ns()
    found, operations_count = tree.search(number)
    finish = time.perf_counter_ns()
    return OperationResult("search", number, finish - start, operations_count, found)


def measure_delete(tree: SegmentTree, number: int) -> OperationResult:
    """Замеряет удаление одного числа."""
    start = time.perf_counter_ns()
    deleted, operations_count = tree.delete(number)
    finish = time.perf_counter_ns()
    return OperationResult("delete", number, finish - start, operations_count, deleted)


def save_results(filename: str, results: list[OperationResult]) -> None:
    """Сохраняет все замеры в CSV-файл."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["operation", "number", "time_ns", "operations_count", "success"])
        for item in results:
            writer.writerow([
                item.operation,
                item.number,
                item.time_ns,
                item.operations_count,
                item.success,
            ])


def print_average(results: list[OperationResult], operation_name: str) -> None:
    """Печатает среднее время и среднее число операций."""
    selected = [item for item in results if item.operation == operation_name]
    avg_time = mean(item.time_ns for item in selected)
    avg_operations = mean(item.operations_count for item in selected)
    print(f"{operation_name}: среднее время = {avg_time:.2f} нс, среднее число операций = {avg_operations:.2f}")


def main() -> None:
    random.seed(42)  # чтобы при повторном запуске получались одинаковые данные

    numbers_count = 10000
    max_value = 9999

    # Пункт 2: создаём массив из 10000 случайных целых чисел.
    numbers = [random.randint(0, max_value) for _ in range(numbers_count)]

    tree = SegmentTree(max_value)
    results = []

    # Пункт 3: добавляем все числа и замеряем каждое добавление.
    for number in numbers:
        results.append(measure_add(tree, number))

    # Пункт 4: выбираем 100 элементов и ищем их.
    numbers_for_search = random.sample(numbers, 100)
    for number in numbers_for_search:
        results.append(measure_search(tree, number))

    # Пункт 5: выбираем 1000 элементов и удаляем их.
    numbers_for_delete = random.sample(numbers, 1000)
    for number in numbers_for_delete:
        results.append(measure_delete(tree, number))

    # Пункт 6: сохраняем все данные запусков.
    save_results("segment_tree_results.csv", results)

    # Выводим средние значения, чтобы их можно было взять в презентацию.
    print_average(results, "add")
    print_average(results, "search")
    print_average(results, "delete")
    print("Все подробные результаты сохранены в файл segment_tree_results.csv")


if __name__ == "__main__":
    main()
