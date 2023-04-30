from random import randint
from .traits import RELPATH


def get_recessives():
    with open(RELPATH + "recessives.txt") as f:
        recessives = [x.removesuffix("\n") for x in f.readlines()]

    return recessives


def get_result_of_two(a, b):
    result = 0

    if a == 0:
        result += 0
    elif a == 1:
        result += randint(0, 1)
    elif a == 3:
        result += 1

    if b == 0:
        result += 0
    elif b == 1:
        result += randint(0, 1)
    elif b == 3:
        result += 1

    return result
