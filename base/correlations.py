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


def get_result(cor_matrix, initial_values: list = None):
    r = np.array(cor_matrix["matrix"])

    if initial_values:
        values = initial_values
    else:
        values = [DOMAIN() for _ in range(len(r))]

    x = np.array(values)

    c = cholesky(r, lower=True)
    y = np.dot(c, x)

    data = {}
    for i in range(len(y)):
        data[cor_matrix["traits"][i]] = float(y[i])

    return data


def convert_data(data: dict):
    new_data = {}
    for key, val in data.items():
        new_data[key.name] = val

    return new_data
