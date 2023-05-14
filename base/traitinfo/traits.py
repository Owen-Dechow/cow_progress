from random import random
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

RELPATH = settings.BASE_DIR / "base/traitinfo/"
DOMAIN = lambda: random() * 2 - 1


class Trait:
    __str__ = lambda self: self.name

    name: str = ""
    standard_deviation: float = 0

    def __init__(self, name, standard_deviation):
        self.name = str(name)
        self.standard_deviation = float(standard_deviation)

    @classmethod
    def Get_All(cls):
        traits = []
        with open(RELPATH / "ptas.txt") as PTAs:
            for line in PTAs.readlines():
                data = line.split(":")
                name = data[0]
                standard_deviation = data[1]
                traits.append(Trait(name, standard_deviation))

        return traits

    @classmethod
    def get(cls, name):
        traitslist = cls.Get_All()
        for trait in traitslist:
            if trait.name == name:
                return trait

        raise ObjectDoesNotExist(f"The requested trait of type {name} does not exist!")
