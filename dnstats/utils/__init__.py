def chunks(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]

