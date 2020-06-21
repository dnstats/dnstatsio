"""run_migrations_online
Source: https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
"""


def chunks(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]
