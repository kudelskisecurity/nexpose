from typing import Any, Tuple

Element = Any  # unable to retrieve real type from lxml
IP = Tuple[int, int, int, int]


def str_to_IP(ip: str) -> IP:
    s = ip.split('.')
    if len(s) != 4:
        raise ValueError(s)

    return int(s[0]), int(s[1]), int(s[2]), int(s[3])
