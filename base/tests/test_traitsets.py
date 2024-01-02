from django.test import TestCase
from base.traitinfo.traitsets import TraitSet, register
from .utils import rand_from_sd
import numpy as np
from scipy.linalg import cholesky


class TestClassSystem(TestCase):
    def test_traitsets(self):
        for obj in register:
            traitset = TraitSet(obj[0])
            values = np.array([rand_from_sd(2.34) for _ in range(len(traitset.traits))])

            err: list[tuple[str, Exception, str]] = []
            try:
                cholesky_decomposition = cholesky(
                    traitset.correlation_matrix, lower=True
                )
                np.dot(cholesky_decomposition, values)
            except np.linalg.LinAlgError as e:
                err.append(("Genotype", e, traitset.name))

            try:
                cholesky_decomposition = cholesky(
                    traitset.ph_correlation_matrix, lower=True
                )
                np.dot(cholesky_decomposition, values)
            except np.linalg.LinAlgError as e:
                err.append(("Phenotype", e, traitset.name))

            if err:
                self.fail(
                    "\n & ".join(
                        [
                            f"{x[0]} correlations invalid on traitset {x[2]}: {x[1]}"
                            for x in err
                        ]
                    )
                )
