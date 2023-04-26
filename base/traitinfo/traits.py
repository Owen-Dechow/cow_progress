from random import random

RELPATH = "base/traitinfo/"
DOMAIN = lambda: random() * 2 - 1


class Trait:
    __str__ = lambda self: self.name

    name: str
    standard_deviation: float

    def __init__(self, name, standard_deviation):
        self.name = name
        self.standard_deviation = standard_deviation

    @classmethod
    def Get_All(cls):
        traits = []
        with open(RELPATH + "ptas.txt") as PTAs:
            for line in PTAs.readlines():
                data = line.split(":")
                name = data[0]
                standard_deviation = data[1]
                traits.append(Trait(name, standard_deviation))

        return traits
