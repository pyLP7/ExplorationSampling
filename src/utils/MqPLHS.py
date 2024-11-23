import chaospy as cp
import matplotlib.pyplot as plt
import numpy as np

from utils.util_functions import get_initial_lhs


def intersite_distance(X=None, newpoint=None):
    """This function returns the minimum intersite distance given a set of data points X.
    This information is required to define the quality of a design in terms of its space-filling proprieties
    
    Parameters
    ----------
    X: Numpy Array
        DOE
    newpoint: Numpy Array
        Candidate sample

    Returns
    -------
    Minimum intersite distance between the candidate point and the existing DOE
    """

    nn, dd = X.shape
    
    if type(newpoint) == np.ndarray:
        
        return np.linalg.norm(abs(X-newpoint), axis=1).min()
    
    else:   
        inter_dist = []
        for ii in range(len(X)):
            X_np_del = np.delete(X, ii, 0)
            inter_dist.append(np.linalg.norm(abs(X_np_del-X[ii]), axis = 1).min())
            
        return np.array(inter_dist).min()


def test_new_lhs_points(optimised_lhs, new_points):
    """Test a set of points to see how effectively they are in being added to a LHS

    Divide the normed space into equal intervals and test to see if there is a
    point in each interval.  If there is a point in an interval, set that
    value to 1.

    To allow for vectorisation, the Numpy Arrays are flattened, tiled and
    repeated so that boolean operations can be carried out on 1d arrays with
    no loops.  The intervals are only generated once to save computation time.

    Add each new point to the LHS and pass the LHS with the point appended
    through the :meth:`check_if_lhs` method.  Return a numpy array containing
    the scores achieved for each new point from this method.

    Parameters
    ----------
    optimised_lhs: Numpy Array
        Optimised Latin Hypercube to add new points to one by one
    new_points: Numpy Array
        Set of new points to be appended and tested with optimised_lhd

    Returns
    -------
    Scores of each new point according to the :meth:`check_if_lhs` method."""
    scores = np.empty((new_points.shape[0]))
    num_points, num_vars = optimised_lhs.shape

    num_points += 1

    interval_start = np.arange(num_points) / num_points
    interval_start = np.repeat(interval_start, num_points*num_vars)

    interval_stop = (np.arange(num_points) + 1) / num_points
    interval_stop = np.repeat(interval_stop, num_points*num_vars)

    is_edge_case = interval_stop == 1

    for i, point in enumerate(new_points):
        temp_lhs = np.vstack((optimised_lhs, point))
        bool_lhs = np.tile(temp_lhs.T.flatten(), num_points)
        score = check_if_lhs(bool_lhs, interval_start, interval_stop, is_edge_case, num_points, num_vars)
        scores[i] = score

    return scores


def check_if_lhs_single(lhs, return_matrix=False):
    """Get the matrix yy given only LHS as input.

    This function performs the same operation as test_new_lhs_points,
    but only tests one point at a time (which should be appended to the LHS
    before passing it into this function.

    Parameters
    ----------
    lhs: Numpy Array
        Latin hypercube to test the score of
    return_matrix: bool, default=False
        If true, the matrix yy will also be returned

    Returns
    -------
    The sum of the matrix yy, divided by (num_points * num_dimensions)"""
    num_points, num_vars = lhs.shape

    interval_start = np.arange(num_points) / num_points
    interval_start = np.repeat(interval_start, num_points*num_vars)

    interval_stop = (np.arange(num_points) + 1) / num_points
    interval_stop = np.repeat(interval_stop, num_points*num_vars)

    bool_lhs = np.tile(lhs.T.flatten(), num_points)

    is_in_interval = np.logical_and(bool_lhs >= interval_start, bool_lhs < interval_stop)

    is_edge_case = interval_stop == 1
    is_in_last_interval = np.logical_and(bool_lhs == 1, is_edge_case)

    yy = np.logical_or(is_in_interval, is_in_last_interval)
    yy = yy.reshape(-1, num_points).any(axis=1)
    yy = yy.reshape(lhs.shape).astype(np.int32)

    result = np.sum(yy)/(num_points*num_vars)

    if return_matrix:
        return result, yy

    return result


def check_if_lhs(bool_lhs, interval_start, interval_stop, is_edge_case, num_points, num_dims, return_matrix=False):
    """Get the matrix yy, which has values equal to 1 if there exist any i for
    which x_ij lies in the interval q and otherwise set to 0.

    Then get the sum of the matrix yy divided by the dimensions of the matrix.
    This value denotes how well the LHS fits the requirements of an LHS with
    the new point inserted.

    Parameters
    ----------
    bool_lhs: Numpy Array
        Flattened, tiled latin hypercube with new point appended
    interval_start: Numpy Array
        1d array representing the lower bound of the intervals
    interval_stop: Numpy Array
        1d array representing the upper bound of the intervals
    is_edge_case: Numpy Array
        Allows for case where upper boundary is 1 should be included in interval
    num_dims: int
        Number of points in bool_lhs
    num_dims: int
        Number of dimensions in bool_lhs
    return_matrix: bool, default=False
        If true, the matrix yy is also returned

    Returns
    -------
    The sum of the matrix yy, divided by (num_points * num_dimensions)"""
    is_in_interval = np.logical_and(bool_lhs >= interval_start, bool_lhs < interval_stop)
    is_in_last_interval = np.logical_and(bool_lhs == 1, is_edge_case)

    yy = np.logical_or(is_in_interval, is_in_last_interval)
    yy = yy.reshape(-1, num_points).any(axis=1)
    yy = yy.reshape((num_points, num_dims)).astype(np.int32)

    result = np.sum(yy)/(num_points*num_dims)

    if return_matrix:
        return result, yy

    return result


def mc_quasi_lhs( num_dims, num_points_max, num_points_start, n_rand_points=100, verbose=True):
    """Find the best selection of points to add a latin hypercube to maintain
    its qualities and raise the number of poitns to num_points_max.

    Generate a set of random points and test each point to see how well
    they fit in a latin hypercube.  Select the best candidate points from this
    random set and get the intersite distance between the LHS and each point.

    Select the point with the best intersite distance.  Repeat this process
    until there are a total of num_points_max points in the LHS.

    Parameters
    ----------
    num_points_start: int
        Initial number of points in latin hypercube
    num_dims: int
        Number of dimensions in latin hypercube
    num_points_max: int
        Desired number of points in latin hypercube
    n_rand_points: int, default=100
        Number of random points to be generated per point in the initial latin
        hypercube

    Returns
    -------
    Latin hypercube with num_points_max points
    """
    lhs = get_initial_lhs(None, num_dims, num_points_start)

    if type(lhs) is not np.ndarray:
        lhs = cp.create_latin_hypercube_samples(order=num_points_start, dim=num_dims).T
    lhs = cp.create_latin_hypercube_samples(order=num_points_start, dim=num_dims).T # DEL

    for i in range(num_points_max - num_points_start):
        # Generate a random set of candidate points to be added to the LHS
        candidate_points = np.random.rand(num_points_start*n_rand_points, num_dims)

        # Find how well each candidate point fits into the lhs
        res = test_new_lhs_points(lhs, candidate_points)

        # Get the indexes that maximise the objective funtions
        indices = np.where(res == res.max())[0]

        # Get the reduced array
        red_candidates = candidate_points[indices]
        
        # Set the current best value to 0
        best_obj = 0
        
        for point in red_candidates:
            # Objective function
            obj = intersite_distance(lhs, point)

            if obj > best_obj:
                best_obj = obj
                best_cand = point
        
        # collect the final candidate
        lhs = np.vstack((lhs, best_cand))
        
        if verbose:
            print(f'nn qLHS: {num_points_start + i + 1}')

    return lhs
            

if __name__ == '__main__':
    nn = [10, 15, 20, 30, 50, 100]
    num_dims = 2

    for num_points in nn:
        lhs = get_initial_lhs(None, num_dims, num_points)
        score = check_if_lhs_single(lhs)
        print(f'Score for LHS with {num_points} points: {score}')

    num_points_start = 150
    num_points_max = 200
    num_dims = 3
    
    lhs = mc_quasi_lhs(num_points_start, num_dims, num_points_max)

