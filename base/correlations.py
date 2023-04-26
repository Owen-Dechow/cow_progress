import numpy as np
from scipy.linalg import cholesky
from . import models
from random import random


DOMAIN = lambda: random() * 2 - 1


def get_cor_matrix():
    "returns cor_matrix, ordered_traits"
    traits = models.Trait.objects.all()
    cor_matrix = []
    for traitA in traits:
        row = []
        for traitB in traits:
            row.append(
                models.Correlation.objects.get(trait_a=traitA, trait_b=traitB).factor
            )
        cor_matrix.append(row)

    return {"matrix": cor_matrix, "traits": traits}
