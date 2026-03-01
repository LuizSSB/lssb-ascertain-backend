import string
from random import shuffle


def random_string(length: int) -> str:
    chars = list(string.ascii_letters + string.digits)
    shuffle(chars)
    return "".join(chars[0:length])
