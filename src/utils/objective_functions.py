import numpy as np
from numba import jit
from scipy.spatial.distance import cdist


def min_intersite_distances(arr, new_points):
    """Find the minimum intersite distance between :param:`arr` and each new point

        Parameters
        ----------
        arr: Numpy Array
            Pre-existing array
        new_points: Numpy Array
            Find minimum intersite distance between each point in this
            array and pre-existing array

        Returns
        -------
        The minimum intersite distance between each new point and every point in arr"""
    num_points, num_dims = arr.shape
    num_new_points, num_dims_new_points = new_points.shape

    if num_dims != num_dims_new_points:
        raise ValueError(f'Number of dimensions in arr ({num_dims}) and new points ({num_dims_new_points}) not equal')

    intersite_distances = cdist(arr, new_points)

    if np.array_equal(arr, new_points):
        np.fill_diagonal(intersite_distances, 1000)

    minimum_intersite_distances = np.min(intersite_distances, axis=0)

    return minimum_intersite_distances


def min_projected_distances(arr, new_points):
    """Calculate the minimum projected distance between :param:`arr` and each new point

        Parameters
        ----------
        arr: Numpy Array
            Pre-existing array
        new_points: Numpy Array
            Find minimum projected distance between each point in this
            array and pre-existing array

        Returns
        -------
        The minimum projected distance between each new point and every point in arr"""
    num_points, num_dims = arr.shape
    num_new_points, num_dims_new_points = new_points.shape

    if num_dims != num_dims_new_points:
        raise ValueError(f'Number of dimensions in arr ({num_dims}) and new points ({num_dims_new_points}) not equal')

    minimum_projected_distances = np.empty(num_new_points)

    is_equal = np.array_equal(arr, new_points)

    for i in range(num_new_points):
        projected_distances = np.abs(arr - new_points[i])

        if is_equal:
            projected_distances = np.delete(projected_distances, i, axis=0)

        minimum_projected_distances[i] = np.min(projected_distances)

    return minimum_projected_distances


def lhs_scores(arr, new_points):
    """Find LHS scores of arr when each new point is added to it

    The LHS score is defined as the sum of the matrix yy (as calculated in
    :meth:`lhs_score_single`) divided by the size of :param:`arr`.

    To allow for vectorisation, the Numpy Arrays are flattened, tiled and
    repeated so that boolean operations can be carried out on 1d arrays with
    no loops.  The intervals are only generated once to save computation time.

    Prepare the LHS so a new point can be added to it with minimal
    operations when looping through each new point.  Return a numpy array
    containing the scores achieved for each new point from this method.

    Parameters
    ----------
    arr: Numpy Array
        Pre-existing array
    new_points: Numpy Array
        Find LHS score of each point in this array when added to
        pre-existing array

    Returns
    -------
    Scores of each new point according to the :meth:`check_if_lhs` method."""
    num_points, num_dims = arr.shape

    num_new_points, num_dims_new_points = new_points.shape

    if num_dims != num_dims_new_points:
        raise ValueError(f'Number of dimensions in arr ({num_dims}) and new points ({num_dims_new_points}) not equal')

    num_points += 1

    interval_start = np.arange(num_points) / num_points
    interval_start = np.repeat(interval_start, num_points * num_dims)

    interval_stop = (np.arange(num_points) + 1) / num_points
    interval_stop = np.repeat(interval_stop, num_points * num_dims)

    is_edge_case = interval_stop == 1

    temp_lhs = np.vstack((arr, np.zeros(num_dims) - 1))

    bool_lhs = np.tile(temp_lhs.T.flatten(), num_points)
    spaces_to_fill = bool_lhs == -1

    new_points_tiled = np.tile(new_points, (1, num_points))

    scores = check_each_point(
        new_points_tiled,
        bool_lhs,
        spaces_to_fill,
        interval_start,
        interval_stop,
        is_edge_case,
        num_points,
        num_dims
    )

    return scores


@jit(nopython=True, fastmath=True)
def check_each_point(new_points_tiled, bool_lhs, spaces_to_fill, interval_start,
                     interval_stop, is_edge_case, num_points, num_dims):
    """Pass each new point through the check_if_lhs function

    Parameters
    ----------
    new_points_tiled: Numpy Array
        Set of new points to be appended and tested with optimised_lhd
    spaces_to_fill: Numpy Array
        Numpy Array mask that tells the function where to fill in the values of
        the new point in the lhs
    bool_lhs: Numpy Array
        Flattened, tiled latin hypercube with new point appended
    interval_start: Numpy Array
        1d array representing the lower bound of the intervals
    interval_stop: Numpy Array
        1d array representing the upper bound of the intervals
    is_edge_case: Numpy Array
        Allows for case where upper boundary is 1 should be included in interval
    num_points: int
        Number of points in bool_lhs
    num_dims: int
        Number of dimensions in bool_lhs

    Returns
    -------
    Numpy Array containing score of each new function"""
    scores = np.empty((new_points_tiled.shape[0]))
    for i, new_point in enumerate(new_points_tiled):
        score = check_if_lhs(
            bool_lhs,
            new_point,
            spaces_to_fill,
            interval_start,
            interval_stop,
            is_edge_case,
            num_points,
            num_dims
        )
        scores[i] = score

    return scores


@jit(nopython=True, parallel=True, fastmath=True)
def check_if_lhs(bool_lhs, new_point, spaces_to_fill, interval_start, interval_stop, is_edge_case, num_points,
                 num_dims):
    """Get the matrix yy, which has values equal to 1 if there exist any i for
    which x_ij lies in the interval q and otherwise set to 0.

    Then get the sum of the matrix yy divided by the dimensions of the matrix.
    This value denotes how well the LHS fits the requirements of an LHS with
    the new point inserted.  (This is the theory applied, put in practice, yy
    is not actually generated, the score goes directly to the sum to save time.
    In order to also return the matrix yy, points will have to be tested one
    by one in check_if_lhs_single, with return_matrix set to True)

    Parameters
    ----------
    bool_lhs: Numpy Array
        Flattened, tiled latin hypercube with new point appended
    new_point: Numpy Array
        Set of new points to be appended and tested with optimised_lhd
    spaces_to_fill: Numpy Array
        Mask that informs the method which values of bool_lhs to fill in
        with new_point values
    interval_start: Numpy Array
        1d array representing the lower bound of the intervals
    interval_stop: Numpy Array
        1d array representing the upper bound of the intervals
    is_edge_case: Numpy Array
        Allows for case where upper boundary is 1 should be included in interval
    num_points: int
        Number of points in bool_lhs
    num_dims: int
        Number of dimensions in bool_lhs

    Returns
    -------
    The sum of the matrix yy, divided by (num_points * num_dimensions)"""
    bool_lhs[spaces_to_fill] = new_point

    is_in_interval = np.logical_and(bool_lhs >= interval_start, bool_lhs < interval_stop)
    is_in_last_interval = np.logical_and(bool_lhs == 1, is_edge_case)

    yy = np.logical_or(is_in_interval, is_in_last_interval)
    yy = yy.reshape(-1, num_points)

    score = 0

    for i in range(num_points * num_dims):
        score += np.any(yy[i, :])

    result = score / (num_points * num_dims)

    return result


def lhs_score_single(arr, return_matrix=False):
    """Generate the matrix yy from the input array and return the corresponding LHS score

    The LHS score is the sum of the matrix yy divided by the size of the
    array yy.

    Given the number of points in the space matrix arr = nn and the number
    of dimensions = dd:
    yy is nn * dd matrix calculated by dividing a normed space into nn
    projected intervals over dd dimensions.  If there is a point in the
    input array in a given interval, the corresponding value of yy will be
    set to 1.  If not, it will be set to 0.

    Parameters
    ----------
    arr: Numpy Array
        Latin hypercube to test the score of
    return_matrix: bool, default=False
        If true, the matrix yy will also be returned

    Returns
    -------
    The sum of the matrix yy, divided by (num_points * num_dimensions)"""
    num_points, num_vars = arr.shape

    interval_start = np.arange(num_points) / num_points
    interval_start = np.repeat(interval_start, num_points * num_vars)

    interval_stop = (np.arange(num_points) + 1) / num_points
    interval_stop = np.repeat(interval_stop, num_points * num_vars)

    bool_lhs = np.tile(arr.T.flatten(), num_points)

    is_in_interval = np.logical_and(bool_lhs >= interval_start, bool_lhs < interval_stop)

    is_edge_case = interval_stop == 1
    is_in_last_interval = np.logical_and(bool_lhs == 1, is_edge_case)

    yy = np.logical_or(is_in_interval, is_in_last_interval)
    yy = yy.reshape(-1, num_points).any(axis=1)
    yy = yy.reshape(arr.shape).astype(np.int32)

    result = np.sum(yy) / (num_points * num_vars)

    if return_matrix:
        return result, yy

    return result
