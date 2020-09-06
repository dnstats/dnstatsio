import hashlib
import base64


def slugify(input_str: str) -> str:
    """
    Given an input will slugify the input. This doesn't do any url decoding. It just replaces spaces with
    underscores.

    :param input_str: string with spaces to slugify
    :return: the input with the replaces removed and converted to lower case
    """
    return input_str.replace(' ', '_').lower()


def calculate_sri_hash(filename: str) -> str:
    """
    Calculate the SRI hash for the given file path.

    :param filename: file path for the calcaute the SRI hash
    :return: the sha384 hash base64 encoding of the given file
    """
    hashing = hashlib.sha384()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(hashing.block_size)
            hashing.update(chunk)
            if not chunk:
                break
    return str(base64.encodebytes(hashing.digest()), 'utf-8').replace('\n', '')
