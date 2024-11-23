import copy
import numpy as np
import chaospy as cp

from scipy.spatial import distance_matrix
from scipy.spatial.distance import cdist

from utils.util_functions import get_initial_lhs

import matplotlib.pyplot as plt
plt.close('all')

    
def intersite_distance(X=None, newpoint=None):
    '''
    This function returns the minimum intersite distance given a set of data points X.
    This information is required to define the quality of a design in terms of its space-filling proprieties
    
    **Parameters**
        * **X** (ndarray):  DOE
        * **newpoint** (ndarray):  candidate sample
    **Return**
        * **float** (float): minimum intersite distance between the candidate point and the existing DOE
    '''

    nn_start, dd = X.shape
    
    if type(newpoint) == np.ndarray:
        return np.linalg.norm(abs(X-newpoint), axis = 1).min()
    
    else:   
        inter_dist = []
        for ii in range(len(X)):
            X_np_del = np.delete(X, ii, 0)
            inter_dist.append(np.linalg.norm(abs(X_np_del-X[ii]), axis = 1).min())
            
        return np.array(inter_dist).min()
    
def crowding_distance_metric(X=None, newpoint=None):
    '''
    Crowding Distance Metric (CDM)
    '''

    nn_start, dd = X.shape
    
    if type(newpoint) == np.ndarray:
        return np.linalg.norm(abs(X-newpoint), axis = 1).sum()
    
    else:   
        inter_dist = []
        for ii in range(len(X)):
            X_np_del = np.delete(X, ii, 0)
            inter_dist.append(np.linalg.norm(abs(X_np_del-X[ii]), axis = 1).min())
            
        return np.array(inter_dist).sum()
    
def find_lhs_gaps(lhs):
    nn, dd = lhs.shape
    
    nn_double = 2*nn

    lower_limits = np.arange(0, nn_double)/nn_double
    upper_limits = np.arange(1, nn_double+1)/nn_double
    
    # lower_limits = lower_limits.reshape(nn,1)*np.ones((nn,dd))
    # upper_limits = upper_limits.reshape(nn,1)*np.ones((nn,dd))
    gaps_matrix = np.zeros((len(upper_limits),dd), dtype=bool)
    

    # fill in the gaps matrix with a 1 for every range gap
    for ii in range(dd):
        for jj in range(len(lower_limits)):
            if jj == len(lower_limits)-1: # right end bound included 
                boolean = (lhs[:,ii] >= lower_limits[jj]) & (lhs[:,ii] <= upper_limits[jj])
            else:
                boolean = (lhs[:,ii] >= lower_limits[jj]) & (lhs[:,ii] < upper_limits[jj])
            if not boolean.any(): #Is there at least one True value?
                gaps_matrix[jj,ii] = True
                
    lower_limits = lower_limits.reshape(nn_double,1)*np.ones((nn_double,dd))
    upper_limits = upper_limits.reshape(nn_double,1)*np.ones((nn_double,dd))
        
    lower_limits_slice = np.zeros((nn,dd))
    upper_limits_slice = np.zeros((nn,dd))
    
    for ii in range(dd):
        lower_limits_slice[:,ii] = lower_limits[:,ii][gaps_matrix[:,ii]]
        upper_limits_slice[:,ii] = upper_limits[:,ii][gaps_matrix[:,ii]]
    
    return lower_limits_slice, upper_limits_slice

def uniform_lhs(lower_limits, upper_limits):

    nn, dd = lower_limits.shape
    
    lhs_slice = np.random.uniform(low=lower_limits, high=upper_limits, size=(nn,dd))
    
    # shuffle columnwise
    for ii in range(dd-1):
        np.random.shuffle(lhs_slice[:,ii+1:]) # be carefull that if you use numpy seed it shuffle always the same way
        
    return lhs_slice


def mc_intersite_proj_th_loop(dd=2, nn_start=10,limit_nn=144, repeat=False, verbose=True):
    '''
    This function runs the mc-inter-proj-th algorithm and returns an adaptive generated DOE
    
    **Parameters**
        * **dd** (int):  number of dimension
        * **limit** (int):  maximum number of samples
        * **nn_start** (int):  initial number of samples
        * **alpha** (float):  alpha paramter necessary to calculate the threshold (between inter and proj distance)
    **Return**
        * **X** (ndarray): generated DOE
    '''
    
    X_coarse = get_initial_lhs(None, dd, nn_start)
    
    if type(X_coarse) is not np.ndarray:
        X_coarse = cp.create_latin_hypercube_samples(order=nn_start, dim=dd).T
    X_coarse = cp.create_latin_hypercube_samples(order=nn_start, dim=dd).T # DEL
    nn, dd = X_coarse.shape

    lhs = X_coarse.copy()
    
    while nn < limit_nn:
        
        # 1 - find the spots available for the next slice
        low_lim, upp_lim = find_lhs_gaps(lhs)
        
        # 2 - generate the PLHS slice according to the available free spots
        # lhs_slice = uniform_lhs(low_lim, upp_lim)
        slices = [uniform_lhs(low_lim, upp_lim) for ii in range(10*nn)]
        
        # 2.1 improve the space filling of the slice
        res_slices = []
        for ii in slices:
            lhs_temp = np.vstack((lhs, ii))
            res_slices.append(intersite_distance(lhs_temp))
            
        best_index = np.where(res_slices == np.max(res_slices))
        lhs_slice = slices[best_index[0][0]]
        
        # 3 - consider each point of the slice one-by-one and add the one that guarantees the best space-filling prop
        while len(lhs_slice) >= 1 and nn < limit_nn:
            res = []
            for jj in lhs_slice:
                res.append(intersite_distance(lhs, newpoint=jj)) 
                
            # find the best point (maximize the ObjFunc)
            best_index = np.where(res == np.max(res))
            bestpoint = lhs_slice[best_index]
            
            # add the best one
            lhs = np.vstack((lhs,bestpoint))
            
            # 4 - check that the lhs-degree increases
            # print(round(check_if_lhs(lhs),4))
            lhs_slice = np.delete(lhs_slice, best_index, 0)

            #current grid
            nn, dd = lhs.shape
            if verbose:
                print('Iteration PLHS: '+str(nn))
            # plot_2d(lhs)
            
    return lhs

def main_PLHS_loop(dd, nn_max, num_points_start, seed=False):
    if seed:
        np.random.seed(seed)
    
    # make sure that NOT all the candidates points are rejected
    X_out = mc_intersite_proj_th_loop(dd, num_points_start, nn_max)
    
    return X_out



def plot_2d(X_out):
    mm,dd = X_out.shape
    
    if dd == 2: 
        plt.scatter(X_out[:,0],X_out[:,1], c='r', zorder =10)
        plt.scatter(X_out[:nn_start,0],X_out[:nn_start,1], c='k', zorder =10)
        for ii in X_out:
            plt.axvline(x=ii[0])
            plt.axhline(y=ii[1])
    
# %% Main file
if __name__ == '__main__':
    
    nn_start = 10
    nn_max = 350
    dd = 30
    
    import time
    start = time.perf_counter()
    # call the main loop
    X_out = main_PLHS_loop(dd, nn_start, nn_max)
    print(time.perf_counter()-start)
    
    # plot 2d domains
    plot_2d(X_out)

    
    
