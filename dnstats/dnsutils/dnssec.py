def parse_ds(ans: list) -> [int, int]:
    if ans:
        parts = str(ans[0]).split(' ')
        algorithm = parts[1]
        digest_type = parts[2]
        return {'ds_algorithm': algorithm, 'ds_digest_type': digest_type}
    return {'ds_algorithm': -1, 'ds_digest_type': -1}


def parse_dnskey(ans: list):
    if ans:
        parts = ans[0].split(' ')
        return parts[2]
    return -1
