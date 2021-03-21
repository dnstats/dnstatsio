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


def update_count_dict(dictt: dict, key: str) -> None:
    """
    Given a dict and key add one to the value. Set it to 1 if the key is not found.
    :param dictt: dictt to search
    :param key: key to search for
    :return: None
    """
    if key in dictt:
        dictt[key] += 1
    else:
        dictt[key] = 1


def get_grade(dictt: dict, key: str, default: int) -> int:
    """
    Given key and dict get the value from the dict. If the
    :param dictt: dict to look up in
    :param key: the key to search for
    :param default: the value to return if key is not found
    :return: value from dictt from key, or default
    """
    value = dictt.get(key)
    if not value:
        return default
    else:
        return value


def not_in_penalty(dictt: dict, key: str, penalty: int):
    """
    If the
    :param dictt: dict to search
    :param key: key to search for 
    :param penalty: the value to return if the value is not found
    :return: 0 if k is in dictt, otherwise 
    """
    if dictt.__contains__(key):
        return 0
    else:
        return penalty
