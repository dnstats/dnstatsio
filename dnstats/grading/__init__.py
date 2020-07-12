from enum import Enum

# Based on https://en.wikipedia.org/wiki/Academic_grading_in_the_United_States
def percent_to_letter(percent: float):
    if percent > 100.0:
        return 'A+'
    elif percent >= 93.0:
        return 'A'
    elif percent >= 90.0:
        return 'A-'
    elif percent >= 87.0:
        return 'B+'
    elif percent >= 83.0:
        return 'B'
    elif percent >= 80.0:
        return 'B-'
    elif percent >= 77.0:
        return 'C+'
    elif percent >= 73.0:
        return 'C'
    elif percent >= 70.0:
        return 'C-'
    elif percent >= 67.0:
        return 'D+'
    elif percent >= 63.0:
        return 'D'
    elif percent >= 60.0:
        return 'D-'
    else:
        return 'F'


class Grade(Enum):
    A_PLUS = 1
    A = 2
    A_MINUS = 3
    B_PLUS = 4
    B = 5
    B_MINUS = 6
    C_PLUS = 7
    C = 8
    C_MINUS = 9
    D_PLUS = 10
    D = 11
    D_MINUS = 12
    F = 13

def half_reduce(grade: Grade) -> Grade:
    if Grade != Grade.F:
        return Grade(grade.value + 1)
    else:
        return Grade.F

def full_reduce(grade: Grade) -> Grade:
    if grade.value < Grade.D_PLUS.value:
        return Grade(grade.value + 3)
    else:
        return Grade.F

def half_raise(grade: Grade) -> Grade:
    if grade != Grade.A_PLUS:
        return Grade(Grade.value - 1)
    else:
        return Grade.A_PLUS

def full_raise(grade: Grade) -> Grade:
    if grade.value > Grade.B_PLUS.value:
        return Grade(grade.value - 3)
    else:
        return Grade.A_PLUS


def update_count_dict(d: dict, key: str):
    if key in d:
        d[key] += 1
    else:
        d[key] = 1
