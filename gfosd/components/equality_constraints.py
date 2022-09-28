import scipy.sparse as sp
import numpy as np
from gfosd.components.base_graph_class import GraphComponent

class FirstValEqual(GraphComponent):
    def __init__(self, value=0, *args, **kwargs):
        self._first_val = value
        super().__init__(*args, **kwargs)
        # always retain helper variable
        self._has_helpers = True

    def _make_A(self):
        super()._make_A()
        super()._make_B()
        self._A = sp.bmat([
            [self._A.tocsr()[0]],
            [sp.dok_matrix((1, self._A.shape[1]))]
        ])

    def _make_B(self):
        self._B = sp.bmat([
            [self._B.tocsr()[0]],
            [sp.coo_matrix(([1], ([0], [0])), shape=(1, self._B.shape[1]))]
        ])

    def _make_c(self):
        super()._make_c()
        self._c = np.concatenate([np.atleast_1d(self._c[0]),
                                  [self._first_val]])

class AverageEqual(GraphComponent):
    def __init__(self, value=0, period=None, *args, **kwargs):
        self._avg_val = value
        self._period = period
        super().__init__(*args, **kwargs)
        # always retain helper variable
        self._has_helpers = True

    def _set_z_size(self):
        if self._diff == 0:
            self._z_size = 0
        else:
            self._z_size = (self._T - self._diff) * self._p

    def _make_A(self):
        if self._diff == 0:
            if self._period is None:
                sum_len = self.x_size
            else:
                sum_len = self._period
            self._A = sp.csr_matrix(np.ones(sum_len), shape=(1, self.x_size))
        else:
            super()._make_A()
            super()._make_B()
            self._A = sp.bmat([
                [self._A],
                [sp.dok_matrix((1, self._A.shape[1]))]
            ])

    def _make_B(self):
        if self._diff == 0:
            self._B = sp.dok_matrix((1, self.z_size))
        else:
            if self._period is None:
                sum_len = self.z_size
            else:
                sum_len = self._period
            self._B = sp.bmat([
                [self._B],
                [sp.csr_matrix(np.ones(sum_len), shape=(1, self.z_size))]
            ])

    def _make_c(self):
        if self._diff == 0:
            if self._period is None:
                sum_len = self.x_size
            else:
                sum_len = self._period
            self._c = np.atleast_1d(sum_len * self._avg_val)
        else:
            if self._period is None:
                sum_len = self.z_size
            else:
                sum_len = self._period
            self._c = np.concatenate([np.atleast_1d(self._c),
                                      [sum_len * self._avg_val]])