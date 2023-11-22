from . import traits
from .traits import RELPATH, DOMAIN
import numpy as np
from scipy.linalg import cholesky


def get_cor_matrix(traitset):
    matrix = []
    with open(RELPATH / traitset / "correlations.txt") as cor_data:
        for line in cor_data:
            linedata = line.strip().removesuffix("\n").split(" ")
            while "" in linedata:
                linedata.remove("")
            matrix.append(linedata)

    return matrix


def get_result(traitset, initial_values: list = None):
    cor_matrix = get_cor_matrix(traitset)
    traitlist = traits.Trait.get_all(traitset)

    r = np.array(cor_matrix)

    if initial_values:
        values = initial_values
    else:
        values = [DOMAIN() for _ in range(len(r))]

    x = np.array(values)

    c = cholesky(r, lower=True)
    y = np.dot(c, x)

    data = {}
    for i in range(len(y)):
        data[traitlist[i]] = float(y[i])

    return data


def convert_data(data: dict):
    new_data = {}
    for key, val in data.items():
        new_data[key.name] = val

    return new_data
