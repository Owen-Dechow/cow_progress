from random import random
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

RELPATH = settings.BASE_DIR / "base/traitinfo/"
DOMAIN = lambda: random() * 2 - 1


class Trait:
    __str__ = lambda self: self.name

    name: str = ""
    standard_deviation: float = 0
    net_merit_dollars: float = 0

    def __init__(self, name, standard_deviation, net_merit_dollars):
        self.name = str(name.strip())
        self.standard_deviation = float(standard_deviation.strip())
        self.net_merit_dollars = float(net_merit_dollars.strip())

    @classmethod
    def get_all(cls):
        traits = []
        with open(RELPATH / "ptas.txt") as PTAs:
            for line in PTAs.readlines():
                data = line.split(":")
                name = data[0]
                standard_deviation = data[1]
                nmd = data[2]
                traits.append(Trait(name, standard_deviation, nmd))

        return traits

    @classmethod
    def get(cls, name):
        traitslist = cls.get_all()
        for trait in traitslist:
            if trait.name == name:
                return trait

        raise ObjectDoesNotExist(f"The requested trait of type {name} does not exist!")

    @classmethod
    def calculate_net_merit(cls, PTAs):
        traits = cls.get_all()
        nm = 0
        for trait in traits:
            nm += trait.net_merit_dollars * PTAs[trait.name]

        return nm
