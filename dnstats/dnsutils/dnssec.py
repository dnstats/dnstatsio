def parse_ds(ans: list) -> [int, int]:
    if ans:
        if len(ans) != 1:
            return None, None
        parts = ans[0].split(' ')
        if len(parts) != 4:
            return None, None
        algorithm = parts[1]
        digest_type = parts[2]
        return algorithm, digest_type
    return None, None


def parse_dnskey(ans: list):
    if ans:
        if len(ans) != 1:
            return None
        parts = ans[0].split(' ')
        if len(parts) != 4:
            return None
        return parts[2]
