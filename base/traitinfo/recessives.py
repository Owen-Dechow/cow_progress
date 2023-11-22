from random import randint
from .traits import RELPATH


def get_recessives(traitset):
    with open(RELPATH / traitset / "recessives.txt") as f:
        recessives = [x.split(":")[0].strip() for x in f.readlines()]

    return recessives


def get_recessives_fatal(traitset):
    with open(RELPATH / traitset / "recessives.txt") as f:
        recessives = [
            [y.strip() for y in x.removesuffix("\n").split(":")] for x in f.readlines()
        ]

    for x in recessives:
        x[1] = "f" in x[1]
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
