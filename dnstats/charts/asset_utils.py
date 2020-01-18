import hashlib
import base64


def slugify(input_str: str) -> str:
    return input_str.replace(' ', '_').lower()


def calculate_sri_hash(filename: str) -> str:
    hashing = hashlib.sha384()
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(hashing.block_size)
            hashing.update(chunk)
            if not chunk:
                break
    return str(base64.encodebytes(hashing.digest()), 'utf-8').replace('\n', '')
