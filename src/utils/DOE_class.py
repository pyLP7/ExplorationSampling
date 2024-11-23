import numpy as np
import chaospy
from utils.util_functions import get_initial_lhs
from utils.objective_functions import min_projected_distances, min_intersite_distances

from utils.FpPLHS import main_PLHS_loop
from utils.MqPLHS import mc_quasi_lhs


class DOE_Class():
    '''
    This class includes the necessary functions to generate sequantial Design of Experiments (DOE).
    '''

    def __init__(self, dsgn='LHSM', sizeOneStage=10, repeat=False, verbose=True):
        self.dsgn = dsgn
        self.nn_start = sizeOneStage
        self.repeat = repeat
        self.verbose = verbose

    def Distance(self, lhc):
        '''
        Computes the minimum Euclidean distance within a Latin Hypercube.

        Parameters
        ----------
        lhc : numpy.ndarray
            The Latin Hypercube for which you want to compute the distance.

        Returns
        -------
        float
            The minimum non-zero Euclidean distance within the Latin Hypercube.
        '''
        distanceVectLP = (((lhc[:, np.newaxis] - lhc).reshape(-1, lhc.shape[1])**2).sum(axis=1))**0.5

        return np.min(distanceVectLP[distanceVectLP != 0])

    def cartesian(self, arrays, out=None):
        '''
        Computes a Cartesian product of input arrays, used to generate a full-factorial design.

        Parameters
        ----------
        arrays : list of numpy.ndarray
            Arrays to compute the Cartesian product from.
        out : numpy.ndarray, optional
            Array to store the output.

        Returns
        -------
        numpy.ndarray
            Cartesian product of the input arrays.
        '''
        arrays = [np.asarray(x) for x in arrays]
        dtype = arrays[0].dtype

        n = np.prod([x.size for x in arrays])
        if out is None:
            out = np.zeros([n, len(arrays)], dtype=dtype)

        mm = int(n / arrays[0].size)
        out[:, 0] = np.repeat(arrays[0], mm)
        if arrays[1:]:
            self.cartesian(arrays[1:], out=out[0:mm, 1:])
            for ii in range(1, arrays[0].size):
                out[ii*mm:(ii+1)*mm, 1:] = out[0:mm, 1:]
        return out

    def floor_full_factorial(self, dd, pp_max):
        '''
        Returns a full-factorial sampling. If pp_max is not a perfect hypercube, the number of points will be floored to the nearest value.

        Parameters
        ----------
        dd : int
            Number of dimensions of the dataset.
        pp_max : int
            Maximum number of samples for the full factorial design.

        Returns
        -------
        numpy.ndarray
            Latin hypercube with shape (number of points, dimensions).
        '''
        pp = int(np.floor((np.power(pp_max, (1/dd)))))
        arrays = [np.linspace(0, 1, pp) for _ in range(dd)]

        return self.cartesian(arrays)


    def LHSchaospy(self, dd, nn):
        '''
        Uses the ChaosPy library to generate a Latin Hypercube.

        Parameters
        ----------
        dd : int
            Number of dimensions.
        nn : int
            Number of samples.

        Returns
        -------
        numpy.ndarray
            Latin Hypercube generated using ChaosPy.
        '''
        return (chaospy.create_latin_hypercube_samples(order=nn, dim=dd).round(5)).T

    def sobol(self, dd, nn):
        '''
        Uses the ChaosPy library to generate a Sobol sequence DOE.

        Parameters
        ----------
        dd : int
            Number of dimensions.
        nn : int
            Number of samples.

        Returns
        -------
        numpy.ndarray
            Sobol sequence DOE.
        '''
        return (chaospy.distributions.sampler.sequences.sobol.create_sobol_samples(order=nn, dim=dd)).T

    def halton(self, dd, nn):
        '''
        Uses the ChaosPy library to generate a Halton sequence DOE.

        Parameters
        ----------
        dd : int
            Number of dimensions.
        nn : int
            Number of samples.

        Returns
        -------
        numpy.ndarray
            Halton sequence DOE.
        '''
        return (chaospy.distributions.sampler.sequences.halton.create_halton_samples(order=nn, dim=dd, burnin=-1, primes=())).T

    def mc_intersite_proj_alpha_th(self, num_dims=0, num_points_start=0, num_points_max=0,
                                   alpha=0.2, n_rand_points=300, seed=False, lhs=None):
        '''
        Runs the MC inter-projection threshold algorithm and returns an adaptively generated DOE.

        Parameters
        ----------
        num_dims : int, default=0
            Number of dimensions in the DOE.
        num_points_start : int, default=0
            Number of initial points in the DOE.
        num_points_max : int, default=0
            Number of desired points in the final DOE.
        alpha : float, default=0.2
            Alpha parameter necessary to calculate the threshold (between intersite and projected distances).
        n_rand_points : int, default=300
            Number of candidate points to be generated per point in the initial Latin Hypercube.
        seed : bool, default=False
            If True, sets the numpy random seed for reproducibility.
        lhs : numpy.ndarray, optional
            Custom DOE to be used if provided.

        Returns
        -------
        numpy.ndarray
            DOE with num_points_max points, generated by the MC inter-projection threshold algorithm.
        '''
        lhs = get_initial_lhs(lhs, num_dims, num_points_start)

        num_points, num_dims = lhs.shape

        if seed:
            np.random.seed(seed)

        while num_points < num_points_max:
            candidate_points = np.random.rand(n_rand_points * num_points, num_dims)

            projected_distances = min_projected_distances(lhs, candidate_points)

            projected_distance_threshold = 2 * alpha / num_points
            candidate_points = candidate_points[projected_distances > projected_distance_threshold]

            intersite_distances = min_intersite_distances(lhs, candidate_points)

            if np.all(intersite_distances == 0):
                print('ERROR: Only zero elements found in objective function. Reducing alpha and retrying...')
                alpha = alpha * 0.95
                return self.mc_intersite_proj_alpha_th(num_points_max=num_points_max, lhs=lhs, alpha=alpha)

            best_point = candidate_points[np.argmax(intersite_distances)]
            lhs = np.vstack((lhs, best_point))

            num_points, num_dims = lhs.shape
            if self.verbose:
                print(f'nn MIPT: {lhs.shape[0]}')

        return lhs

    def mc_intersite_proj_auto_alpha_th(self, num_dims=0, num_points_max=0, num_points_start=0,
                                        alpha=None, n_rand_points=300, repeat=False, lhs=None, alpha_scale=0.5):
        '''
        Runs the MC inter-projection threshold algorithm with automatic alpha calculation.

        Parameters
        ----------
        num_dims : int, default=0
            Number of dimensions in the DOE.
        num_points_max : int, default=0
            Number of desired points in the final DOE.
        num_points_start : int, default=0
            Number of initial points in the DOE.
        alpha : float, optional
            Alpha parameter necessary to calculate the threshold. Calculated automatically if not provided.
        n_rand_points : int, default=300
            Number of candidate points to be generated per point in the initial Latin Hypercube.
        repeat : int, optional, default=False
            Optional parameter that will fix the numpy random seed for reproducibility.
        lhs : numpy.ndarray, optional
            Custom DOE to be used if provided.
        alpha_scale : float, default=0.5
            Scaling factor for alpha calculation.

        Returns
        -------
        numpy.ndarray
            DOE with num_points_max points, generated by the MC inter-projection threshold algorithm.
        '''
        lhs = get_initial_lhs(lhs, num_dims, num_points_start)

        num_points, num_dims = lhs.shape

        if repeat:
            np.random.seed(repeat)

        while num_points < num_points_max:
            candidate_points = np.random.rand(n_rand_points * num_points, num_dims)

            projected_distances = min_projected_distances(lhs, candidate_points)

            if not alpha:
                max_projected_distance = np.max(projected_distances)
                alpha = (max_projected_distance / 2 * num_points) * alpha_scale
                if self.verbose:
                    print(f'Attempting to get new LHS points using mc_intersite_proj_auto_alpha_th() with alpha = {alpha} ...')

            projected_distance_threshold = 2 * alpha / num_points
            candidate_points = candidate_points[projected_distances > projected_distance_threshold]

            intersite_distances = min_intersite_distances(lhs, candidate_points)

            if np.all(intersite_distances == 0):
                if self.verbose:
                    print('ERROR: Only zero elements found in objective function. Reducing alpha and retrying...')
                alpha = alpha * 0.95
                return self.mc_intersite_proj_alpha_th(num_points_max=num_points_max, lhs=lhs, alpha=alpha)

            best_point = candidate_points[np.argmax(intersite_distances)]
            lhs = np.vstack((lhs, best_point))

            num_points, num_dims = lhs.shape
            if self.verbose:
                print(f'Point added. New number of points: {lhs.shape[0]}')

        return lhs

    def DOE(self, dd, nn):
        '''
        Generates a DOE using the requested method based on the self.dsgn parameter.

        Parameters
        ----------
        dd : int
            Number of dimensions.
        nn : int
            Number of samples.

        Returns
        -------
        numpy.ndarray
            The generated DOE in an n-dimensional array bounded in [0,1]^d.
        '''
        if self.dsgn == 'floor_FF':
            return self.floor_full_factorial(dd, nn)
        elif self.dsgn == 'LHS_light':
            return self.LHSchaospy(dd, nn)
        elif self.dsgn == 'LHS_opti':
            return get_initial_lhs(None, dd, nn)
        elif self.dsgn == 'sobol':
            return self.sobol(dd, nn)
        elif self.dsgn == 'halton':
            return self.halton(dd, nn)
        elif self.dsgn == 'MIPT':
            return self.mc_intersite_proj_auto_alpha_th(dd, nn, num_points_start=self.nn_start)
        elif self.dsgn == 'MqPLHS':
            return mc_quasi_lhs(dd, nn, num_points_start=self.nn_start)
        elif self.dsgn == 'FpPLHS':
            return main_PLHS_loop(dd, nn, num_points_start=self.nn_start)
