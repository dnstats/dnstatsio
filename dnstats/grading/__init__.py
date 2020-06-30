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