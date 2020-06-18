def parse_ds(ans: list) -> [int, int]:
    if ans:
        parts = str(ans[0]).split(' ')
        algorithm = parts[1]
        digest_type = parts[2]
        return algorithm, digest_type
    return -1, -1


def parse_dnskey(ans: list):
    if ans:
        parts = ans[0].split(' ')
        return parts[2]
    return -1
