import enum

import ipaddress


class MaxValue(enum.Enum):
    USIXTEEN = 65535
    UTHIRTY_TW0 = 4294967295


def validate_numbers(value: str, invalid_error: enum.Enum, out_of_range_error: enum.Enum, max_value: MaxValue) -> (int, list):
    """
    Validate the value of unsigned ints
    :param value: Bhe int to check
    :param invalid_error: The error to return if the number is in valid
    :param out_of_range_error: The error to return if the value is out of range
    :param max_value: A member of :class:MaxValue that is max value you want to check
    :return:
    """
    errors = list()
    try:
        value_int = int(value)
    except ValueError:
        errors.append(invalid_error)
        return -1, errors

    if value_int > max_value.value or value_int < 0:
        errors.append(out_of_range_error)
    return value_int, errors


def is_an_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True