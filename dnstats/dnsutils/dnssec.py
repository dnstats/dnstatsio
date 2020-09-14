import enum
import dns

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


class Algorithm(enum.Enum):
    """
    Source: https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions
    """
    RSA_MD5 = 1
    DSA_SHA1 = 3
    RSA_SHA1 = 5
    DSA_NSEC3_SHA1 = 6
    RSASHA1_NSEC3_SHA1 = 7
    RSA_SHA256 = 8
    RSA_SHA512 = 10
    GOST_R_34_10_2001 = 12
    ECDSA_SHA256 = 13
    ECDSA_SHA384 = 14
    ED25519 = 15
    ED448 = 16


ALGORITHM_MUST_NOT = [Algorithm.RSA_MD5, Algorithm, Algorithm.DSA_SHA1, Algorithm.DSA_NSEC3_SHA1,
                      Algorithm.GOST_R_34_10_2001]
ALGORITHM_SHOULD_NOT = [Algorithm.RSA_SHA1, Algorithm.RSA_SHA512]


class Digest(enum.Enum):
    """
    Source: https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions
    """
    SHA1 = 1
    SHA256 = 2
    GOST_R_34_10_2001 = 3
    SHA384 = 4

