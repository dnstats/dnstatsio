import enum


class NumberErrors(enum.Enum):
    VALID = 0
    NOT_A_NUMBER = 1
    OUT_OF_RANGE = 2


def validate_32_bit_int_string(input: str) -> NumberErrors:
    if not input:
        return NumberErrors.NOT_A_NUMBER
    try:
        value = int(input)
    except ValueError:
        return NumberErrors.NOT_A_NUMBER

    if 0 <= value <= 4294967295:
        return NumberErrors.VALID
    else:
        return NumberErrors.OUT_OF_RANGE
