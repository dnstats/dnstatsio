import re

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


def validate_url(url: str) -> bool:
    """
    This regex is based Django's validator for URls.

    
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    :param url:
    :return: if the input is a url
    """
    regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    # No match returns None, seems hacky
    return True if regex.search(url) else False


def validate_fqdn(fqdn: str) -> bool:
    """
    Give a string checks if its a Fully qualified domain name (FQDN).

    This regex is based Django's validator for URls.


    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    :param fqdn:
    :return: bool if input is a FQDN
    """
    regex = re.compile(r'^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                       r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                       r'(?::\d+)?'  # optional port
                       r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    # No match returns None, seems hacky
    return True if regex.search(fqdn) else False


def count_value(value: object, the_list: list):
    count = 0
    for item in the_list:
        if item == value:
            count += 1
    return count