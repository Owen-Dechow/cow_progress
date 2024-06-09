from django.test import TestCase
from base.traitinfo.traitsets import TraitSet, register
from .utils import rand_from_sd
import numpy as np
from scipy.linalg import cholesky


class TraitsetError:
    def __init__(self, traitset_name, exception, message):
        self.traitset_name = traitset_name
        self.exception = exception
        self.message = message


class TestTraitsets(TestCase):
    def test_traitsets(self):
        for obj in register:
            errors = []
            self.single_traitset_test(obj, errors)

            if errors:
                self.fail(
                    "\n\t"
                    + "\n\t".join(
                        f"Error on traitset '{x.traitset_name}': {x.message} ({x.exception})"
                        for x in errors
                    )
                )

    def single_traitset_test(self, registed_object, errors):
        try:
            traitset = TraitSet(registed_object[0])
        except Exception as e:
            errors.append(
                TraitsetError(registed_object[0], e, "Traitset loading error")
            )
            return

        try:
            assert len(traitset.correlation_matrix) == len(
                traitset.traits
            ), f"Traits in matrix: {len(traitset.correlation_matrix)} != Traits in set: {len(traitset.traits)}"
        except Exception as e:
            errors.append(
                TraitsetError(
                    registed_object[0],
                    e,
                    "Number of traits in genotype correlation matrix does not match number of traits in traitset.",
                )
            )

        try:
            values = np.array([rand_from_sd(2.34) for _ in range(len(traitset.traits))])
            cholesky_decomposition = cholesky(traitset.correlation_matrix, lower=True)
            np.dot(cholesky_decomposition, values)
        except Exception as e:
            errors.append(
                TraitsetError(traitset.name, e, "Genotype correlation matrix invalid")
            )

        try:
            assert len(traitset.ph_correlation_matrix) == len(
                traitset.traits
            ), f"Traits in matrix: {len(traitset.ph_correlation_matrix)} != Traits in set: {len(traitset.traits)}"
        except Exception as e:
            errors.append(
                TraitsetError(
                    registed_object[0],
                    e,
                    "Number of traits in phenotype correlation matrix does not match number of traits in traitset.",
                )
            )

        try:
            values = np.array([rand_from_sd(2.34) for _ in range(len(traitset.traits))])
            cholesky_decomposition = cholesky(
                traitset.ph_correlation_matrix, lower=True
            )
            np.dot(cholesky_decomposition, values)
        except Exception as e:
            errors.append(
                TraitsetError(traitset.name, e, "Phenotype correlation matrix invalid")
            )
