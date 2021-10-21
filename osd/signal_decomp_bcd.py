""" Block Coordinate Descent (BCD) for signal decomposition

Author: Bennet Meyers
"""

import numpy as np
from time import time
from osd.utilities import calc_obj, progress


def run_bcd(data, components, num_iter=50, use_ix=None, X_init=None,
            stopping_tolerance=1e-6, verbose=True):
    if use_ix is None:
        use_ix = np.ones_like(data, dtype=bool)
    y = data
    T = len(data)
    K = len(components)
    rho = 2 / T
    use_ix = np.ones_like(y, dtype=bool)
    if X_init is None:
        X = np.zeros((K, T))
        X[0, use_ix] = y[use_ix]
    else:
        X = np.copy(X_init)
    X0_next = np.copy(X[0, :])
    obj = []
    # obj.append(calc_obj(y, X, components, use_ix, residual_term=0))
    gradients = np.zeros_like(X)
    norm_dual_residual = []
    ti = time()
    for it in range(num_iter):
        if verbose:
            td = time() - ti
            progress(it, num_iter, '{:.2f} sec'.format(td))
        for k in range(1, K):
            prox = components[k].prox_op
            weight = components[k].weight
            #### Coordinate descent updates
            Xk_next = prox(X[0, :] + X[k, :], weight, rho)
            X0_next[use_ix] = (X[0, :] + X[k, :] - Xk_next)[use_ix]
            gradients[k, :] = rho * (X[0, :] + X[k, :] - Xk_next)
            X[0, :] = X0_next
            X[k, :] = Xk_next
        gradients[0] = X[0] * 2 / y.size
        dual_resid = gradients - X[0] * 2 / y.size
        n_s_k = np.linalg.norm(dual_resid) / np.sqrt(dual_resid.size)
        obj.append(calc_obj(y, X, components, use_ix,
                                residual_term=0))
        norm_dual_residual.append(n_s_k)
        if np.average(norm_dual_residual[-5:]) <= stopping_tolerance:
            break
    if verbose:
        td = time() - ti
        progress(num_iter, num_iter, '{:.2f} sec\n'.format(td))
    out_dict = {
        'X': X,
        'obj_vals': obj,
        'optimality_residual': norm_dual_residual
    }
    return out_dict