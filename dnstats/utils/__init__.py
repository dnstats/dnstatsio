"""
Source: https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
"""


def chunks(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]

def get_int_or_null(input: str):
    value = None
    try:
        value = int(input)
    except ValueError:
        return None
    return value
