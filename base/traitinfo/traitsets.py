from pathlib import Path
from django.conf import settings
import numpy as np
from scipy.linalg import cholesky
from random import random, randint
from django.core.exceptions import ObjectDoesNotExist
from math import sqrt


register = [
    ("NM_2021", True),
    ("AN_SC_422", True),
]

TRAITSET_CHOICES = [(item, item) for item, allow in register if allow]

DOMAIN = lambda: random() * 2 - 1


class Trait:
    __str__ = lambda self: self.name

    name: str
    standard_deviation: float
    net_merit_dollars: float
    inbreeding_depression_percentage: float
    heritability: float

    def __init__(
        self, name, sd, heritability, nm_dollars, inbreeding_depression_percentage
    ):
        self.name = str(name).strip()
        self.standard_deviation = float(sd.__str__().strip())
        self.net_merit_dollars = float(nm_dollars.__str__().strip())
        self.inbreeding_depression_percentage = float(
            inbreeding_depression_percentage.__str__().strip()
        )
        self.heritability = float(heritability.__str__().strip())

    def PTA_to_phenotype(self, PTA, inbreeding_coefficient):
        phenotypic_variance = (self.standard_deviation**2) / self.heritability
        residual_variance = phenotypic_variance * (1 - self.heritability)
        residual_standard_deviation = sqrt(residual_variance)
        phenotype = PTA * 2 + np.random.normal(scale=residual_standard_deviation)
        phenotype += (
            inbreeding_coefficient * 100 * self.inbreeding_depression_percentage
        )
        return phenotype

    def get_point_on_mendelian_sample(self, center=0):
        return np.random.normal(loc=center, scale=self.standard_deviation)

    def PTA_mutation(self, sire_PTA, dam_PTA):
        scale = sqrt(2) / 2
        parent_average = (sire_PTA + dam_PTA) / 2
        mendelian_sampling = self.get_point_on_mendelian_sample()

        return parent_average * scale + mendelian_sampling * scale


class Recessive:
    __str__ = lambda self: self.name

    name: str
    fatal: bool
    prominence: float
    extended_name: str

    def __init__(self, name, fatal, prominence, extended_name):
        self.name = str(name).strip()
        self.fatal = bool(fatal)
        self.prominence = float(prominence.__str__().strip())
        self.extended_name = extended_name

    def get_carrier_int_from_prominence(self):
        return 1 if random() <= self.prominence else 0


class TraitSet:
    RELPATH: Path
    correlation_matrix: list[list[float]]
    ph_correlation_matrix: list[list[float]]
    traits = list[Trait]
    recessives = list[Recessive]
    DPR_for_max_gen: Trait

    def __init__(self, traitset_name: str):
        self.RELPATH = settings.BASE_DIR / "base/traitinfo/traitsets" / traitset_name
        self.correlation_matrix = self._get_cor_matrix()
        self.ph_correlation_matrix = self._get_ph_cor_matrix()
        self.traits = self._get_traits_list()
        self.recessives = self._get_recessives()
        self.DPR_for_max_gen = self._get_dpr_trait()

    def _get_cor_matrix(self):
        matrix = []
        with open(self.RELPATH / "gen_corr.txt") as cor_data:
            for line in cor_data:
                linedata = line.strip().removesuffix("\n").split(" ")
                while "" in linedata:
                    linedata.remove("")
                matrix.append(linedata)

        return matrix

    def _get_ph_cor_matrix(self):
        matrix = []
        with open(self.RELPATH / "phen_corr.txt") as cor_data:
            for line in cor_data:
                linedata = line.strip().removesuffix("\n").split(" ")
                while "" in linedata:
                    linedata.remove("")
                matrix.append(linedata)

        return matrix

    def _get_traits_list(self):
        traits = []
        with open(self.RELPATH / "ptas.txt") as PTAs:
            for line in PTAs.readlines():
                data = line.split(":")
                traits.append(Trait(*data))

        return traits

    def _get_recessives(self):
        recessives = []
        with open(self.RELPATH / "recessives.txt") as f:
            for recessive in f.readlines():
                values = recessive.split(":")
                recessives.append(
                    Recessive(values[0], values[1].strip() == "f", *values[2:])
                )

        return recessives

    def _get_result_of_single_recessive_int_val(self, recessive: int):
        if recessive == 0:
            return 0
        elif recessive == 1:
            return randint(0, 1)
        elif recessive == 2:
            return 1

    def _get_dpr_trait(self):
        for x in ["DPR", "Dpr", "dpr"]:
            try:
                return self.get_trait_from_name(x)
            except:
                continue

    def get_correlated_values(
        self, initial_values: dict[str, float] = None, phenotype_corr: bool = False
    ):
        if phenotype_corr:
            scale = 2
            covariance_matrix = np.array(self.ph_correlation_matrix)
        else:
            scale = 1
            covariance_matrix = np.array(self.correlation_matrix)

        values = [
            initial_values[x.name] / (x.standard_deviation * scale) for x in self.traits
        ]

        initial_matrix = np.array(values)

        cholesky_decomposition = cholesky(covariance_matrix, lower=True)
        correlated_values = np.dot(cholesky_decomposition, initial_matrix)

        data = {}
        for idx, val in enumerate(correlated_values):
            data[self.traits[idx]] = val * scale * self.traits[idx].standard_deviation

        return data

    def get_trait_from_name(self, name: str):
        for trait in self.traits:
            if trait.name == name:
                return trait

        raise ObjectDoesNotExist(f"The requested trait of type {name} does not exist!")

    def calculate_net_merit(self, PTAs: dict[str, float]):
        nm = 0
        for trait in self.traits:
            nm += trait.net_merit_dollars * PTAs[trait.name]

        return nm

    def get_result_of_two_recessive_int_vals(self, a, b):
        result = 0
        result += self._get_result_of_single_recessive_int_val(a)
        result += self._get_result_of_single_recessive_int_val(b)
        return result
