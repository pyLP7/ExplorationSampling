import os
import pickle

import numpy as np
import chaospy as cp

def load_optimal_doe(dd, nn, pickle_name=None):
    """Load optimized LHS from https://spacefillingdesigns.nl/ database:

    The following LHS are available:
        - LHS with 2 up to 4 variables with 2 up to 200 samples
        - LHS with 5 up to 10 variables with 2 up to 100 samples
        - LHS with 11 up to 13 variables with 4 up to 6 samples
        - LHS with 14 up to 20 variables with 4 up to 5 samples

    Parameters
    ----------
    dd: Numpy Array
        dimension of the problem
    nn: Numpy Array
        number of samples
    pickle_name: str, default=None
        Pickle file to take DOE from. If None, the design will be taken from
        ../opti_LHS_database.p

    Returns
    -------
    Numpy Array containing optimised DOE

    """
    
    # Load Pickle
    if not pickle_name:
        pickle_name = os.getcwd() + '/utils/DOE/opti_LHS_database.p'

    with open(pickle_name, 'rb') as f:
        lhs_indexes = pickle.load(f)

    try:
        optimal_lhs_index = lhs_indexes[f'dd{dd}_nn{nn}']

        xxx = np.linspace(0, 1, nn)
        doe_list = []

        # Build DOE using optimal LHS indexes
        for ii in range(dd):
            doe_list.append(xxx[optimal_lhs_index[:, ii]])

        # pack all together
        return np.vstack(doe_list).T

    except KeyError:
        print(f'WARNING: optimal LHS with dd={dd} and nn={nn} NOT available from https://spacefillingdesigns.nl/!')
        return None


def get_initial_lhs(lhs,  num_dims, num_points_start, verbose=True):
    """If lhs is none, attempt to get LHS from https://spacefillingdesigns.nl/

    If this is not possible, generate the LHS using create_latin_hypercube_samples"""
    if type(lhs) is not np.ndarray:
        lhs = load_optimal_doe(num_dims, num_points_start)
        # lhs = cp.create_latin_hypercube_samples(order=num_points_start, dim=num_dims).T #DEL

    if type(lhs) is not np.ndarray:
        lhs = cp.create_latin_hypercube_samples(order=num_points_start, dim=num_dims).T
        
    if verbose:
        print(f'LHS with {lhs.shape[0]} points and {lhs.shape[1]} dimensions retrieved.')
    
    return lhs
