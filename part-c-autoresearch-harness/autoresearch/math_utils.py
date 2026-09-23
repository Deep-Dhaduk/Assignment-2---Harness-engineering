"""Small numerical routines used to avoid hiding the experiment in an ML framework."""

from __future__ import annotations


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve Ax=b with Gaussian elimination and partial pivoting."""
    size = len(vector)
    augmented = [list(matrix[row]) + [vector[row]] for row in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) < 1e-12:
            raise ValueError("Singular system; increase ridge regularization")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                augmented[row][index] - factor * augmented[column][index]
                for index in range(size + 1)
            ]
    return [augmented[row][-1] for row in range(size)]


def fit_polynomial(xs: list[float], ys: list[float], degree: int, ridge: float) -> list[float]:
    width = degree + 1
    design = [[x**power for power in range(width)] for x in xs]
    gram = [[sum(row[i] * row[j] for row in design) for j in range(width)] for i in range(width)]
    for index in range(1, width):
        gram[index][index] += ridge
    target = [sum(row[i] * y for row, y in zip(design, ys)) for i in range(width)]
    return solve_linear_system(gram, target)


def predict(coefficients: list[float], x: float) -> float:
    return sum(coefficient * x**power for power, coefficient in enumerate(coefficients))


def mean_squared_error(coefficients: list[float], xs: list[float], ys: list[float]) -> float:
    return sum((predict(coefficients, x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
