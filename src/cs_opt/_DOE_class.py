import numpy as np
import chaospy, pickle, sys, os
# from cs_opt import _DOE_class
from utils.util_functions import get_initial_lhs
from utils.objective_functions import min_projected_distances, min_intersite_distances

from utils.FpPLHS import main_PLHS_loop
from utils.MqPLHS import mc_quasi_lhs



class DOE_Class():
    '''
    In this class the necessary functions to generate a proper DOE are implemented
    '''
    
    def __init__(self, dsgn='LHSM', sizeRoughDOE=10, repeat=False):
        self.dsgn = dsgn
        self.nn_start = sizeRoughDOE
        self.repeat = repeat
        
    def Distance(self,lhc):
        '''
        To get a perfect DOE, we first have to define somehow a distance within a LatinHyperCube.
        Therefore we just add all euclidean distances within each sample of this lhc:
            
        **Parameters:**
            * **lhc** (numpy.array): The LatinHyperCube, of which you want to get the distance.
        
        **Return:**
            * **distance** (numpy.array): A list of all distances:
                * Example: 
                    >>>
                    distance= [0.47140452 0.94280904 0.47140452]
                
        '''
        distanceVectLP = (((lhc[:, np.newaxis] - lhc).reshape(-1, lhc.shape[1])**2).sum(axis=1))**0.5

        return np.min(distanceVectLP[distanceVectLP != 0])
        
    def cartesian(self, arrays,  out=None,):
        """
        function used to compute a perfect full-factorial given some arrays in 
        input
        """
        
        arrays = [np.asarray(x) for x in arrays]
        dtype = arrays[0].dtype

        n = np.prod([x.size for x in arrays])
        if out is None:
            out = np.zeros([n, len(arrays)], dtype=dtype)

        mm = int(n / arrays[0].size) 
        out[:,0] = np.repeat(arrays[0], mm)
        if arrays[1:]:
            self.cartesian(arrays[1:], out=out[0:mm, 1:])
            for ii in range(1, arrays[0].size):
                out[ii*mm:(ii+1)*mm, 1:] = out[0:mm, 1:]
        return out

    def floor_full_factorial(self, dd, pp_max,):
        """
        Return a full-factorial sampling. If pp_max is not a perfect hypercube, 
        the number of points will be "floored" to the neared 

        Args:
            pp_max (int):
                Maximum number of samples of the full factorial.
            dd (int):
                The number of dimensions dataset.

        Returns (numpy.ndarray):
            Latin hyper-cube with ``shape == (dim, order)``.
        """
        # finding the closest hypercube (rounding up using np.floor)
        pp = int(np.floor((np.power(pp_max,(1/dd)))))
        arrays = [np.linspace(0,1,pp) for ii in range(dd)]
        
        # get all the possible combinations among these array elements
        return self.cartesian(arrays)
    
    def LHS(self,dd,nn):
        '''
        Standard latinhypercube in [0,1]^dd with nn samples
        
        **Parameters:**
        
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        
        **Return:**
            * **lc** (numpy.array): LatinHypercube 
        
        **Example** : 
            >>>
            LHS(2,3) 
        
            >>> 
            [[0.83333333 0.16666667] [0.5        0.5       ] [0.16666667 0.83333333]]
        
        '''
        randDOE = np.random.random(nn*dd).reshape((dd,nn))
        for dim_item in range(dd):
            perm = np.random.permutation(nn)  # pylint: disable=no-member
            randDOE[dim_item] = (perm + randDOE[dim_item])/nn
        return randDOE.T
    
    def LHSM(self,dd,nn):
        '''
        In this function we just minimze the distance within a latin-hypercube.
        We do this randomly for nn*500 times
        
        **Parameters:**
        
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        
        **Return:**
            * **lhcm** (numpy.array): LatinHypercube 
        
        **Example** : 
            >>>
            LHSM(2,3) 
            
            >>> 
            [[0.83333333 0.16666667] [0.5        0.5       ] [0.16666667 0.83333333]]
        
        '''
        minimaldistance = 0
        for i in range(nn*500):#10000
            LHSMcandidate = self.LHS(dd,nn)
            distance = self.Distance(LHSMcandidate)
            if minimaldistance<distance:
                minimaldistance = distance
                lhcm = LHSMcandidate.copy()
        
        return lhcm
    
    def LHSchaospy(self,dd,nn):
        '''
        In this function we just use the already implemented LHS ChaosPy function for a DOE.
        
        **Parameters:**
        
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        
        **Return:**
            * **ndarray** (ndarray): LHS random DOE
        
        **Example** : 
            >>>
            LHSchaospy(2,3) 
            
            >>> 
            [[0.83333333 0.16666667] [0.5        0.5       ] [0.16666667 0.83333333]]
        
        '''
        return (chaospy.create_latin_hypercube_samples(order=nn, dim=dd).round(5)).T #verify!!
    
    def sobol(self,dd,nn):
        '''
        In this function we just use the already implemented Sobol function for a DOE.
        
        **Parameters:**
        
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        
        **Return:**
            * **ndarray** (ndarray): sobol DOE
        
        **Example** : 
            >>>
            sobol(2,3) 
            
            >>> 
            [[0.83333333 0.16666667] [0.5        0.5       ] [0.16666667 0.83333333]]
        
        '''
        return (chaospy.distributions.sampler.sequences.sobol.create_sobol_samples(order=nn, dim=dd)).T #verify!!
    
    def halton(self,dd,nn):
        '''
        In this function we just use the already implemented Halton function for a DOE.
        
        **Parameters:**
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        **Return:**
            * **ndarray** (ndarray): halton DOE
        
        **Example** : 
            >>>
            halton(2,3) 
            >>> 
            [[0.83333333 0.16666667] [0.5        0.5       ] [0.16666667 0.83333333]]
        '''
        return (chaospy.distributions.sampler.sequences.halton.create_halton_samples(order=nn, dim=dd, burnin=-1, primes=())).T #verify!!
    
        
    def mc_intersite_proj_alpha_th(self, num_dims=0, num_points_start=0, num_points_max=0,
                                   alpha=0.2, n_rand_points=300, seed=False, lhs=None):
        """This function runs the mc-inter-proj-th algorithm and returns an adaptive generated DOE
    
        Parameters
        ----------
        num_points_start: int, default=10
            Number of initial points in the DOE
        num_dims: int, default=2
            Number of dimensions in the DOE
        num_points_max: int, defualt=144
            Number of desired points in the final DOE
        alpha: float, default=0.2
            Alpha paramter necessary to calculate the threshold (between inter and proj distance)
        n_rand_points: int, default=300
            Number of candidate points to be generated per point in initial LHS
        repeat: int, optional, default=False
            Optional parameter that will fix the numpy.random seed for reproducibility purposes
        lhs: Numpy Array, optional, default=None
            Custom DOE that will be used if it is passed in
    
        Returns
        -------
        DOE with :param:`num_points_max` points, generated by the mc-inter-proj-th algorithm"""
        lhs = get_initial_lhs(lhs, num_dims, num_points_start)
    
        num_points, num_dims = lhs.shape
    
        if seed:
            np.random.seed(seed)  # reproducibility of results @@@
    
        # print(f'Attempting to get new LHS points using mc_intersite_proj_alpha_th() with alpha = {alpha} ...')
        while num_points < num_points_max:
            # Generate set of random points to choose optimal one from
            candidate_points = np.random.rand(n_rand_points * num_points, num_dims)#.astype(np.float32)
    
            # Calculate minimum projected distance between each candidate point and lhs
            projected_distances = min_projected_distances(lhs, candidate_points)
    
            # Remove points with projected distance below the projected distance threshold
            projected_distance_threshold = 2 * alpha / num_points
            candidate_points = candidate_points[projected_distances > projected_distance_threshold]
    
            # Calculate intersite distances between each candidate point and lhs
            intersite_distances = min_intersite_distances(lhs, candidate_points)
    
            # Lower value of alpha and continue algorithm
            if np.all(intersite_distances == 0):
                print('ERROR: Only zero elements found in objective function. Reducing alpha and retrying... ###')
                alpha = alpha * 0.95
                return self.mc_intersite_proj_alpha_th(num_points_max=num_points_max, lhs=lhs, alpha=alpha)
    
            # Add point to LHS that maximises objective function
            best_point = candidate_points[np.argmax(intersite_distances)]
            lhs = np.vstack((lhs, best_point))
    
            num_points, num_dims = lhs.shape
            print(f'nn MIPT: {lhs.shape[0]}')
    
        return lhs
    
    def mc_intersite_proj_auto_alpha_th(self, num_dims=0, num_points_max=0, num_points_start=0,
                                   alpha=None, n_rand_points=300, repeat=False, lhs=None, alpha_scale=0.5):
        """This function runs the mc-inter-proj-th algorithm and returns an adaptive generated DOE
    
        Parameters
        ----------
        num_points_start: int, default=10
            Number of initial points in the DOE
        num_dims: int, default=2
            Number of dimensions in the DOE
        num_points_max: int, defualt=144
            Number of desired points in the final DOE
        alpha: float, default=None
            Alpha paramter necessary to calculate the threshold (between inter and proj distance).
            Parameter will be calculated automatically for first new point, then passed into method.
        n_rand_points: int, default=300
            Number of candidate points to be generated per point in initial LHS
        repeat: int, optional, default=False
            Optional parameter that will fix the numpy.random seed for reproducibility purposes
        lhs: Numpy Array, optional, default=None
            Custom DOE that will be used if it is passed in
    
        Returns
        -------
        DOE with :param:`num_points_max` points, generated by the mc-inter-proj-th algorithm"""
        lhs = get_initial_lhs(lhs, num_dims, num_points_start)
    
        num_points, num_dims = lhs.shape
    
        if repeat:
            np.random.seed(repeat)  # reproducibility of results @@@

    
        # if alpha:
        #     print(f'Attempting to get new LHS points using mc_intersite_proj_auto_alpha_th() with alpha = {alpha} ...')
        while num_points < num_points_max:
            # Generate set of random points to choose optimal one from
            candidate_points = np.random.rand(n_rand_points * num_points, num_dims)#.astype(np.float32)
    
            # Calculate minimum projected distance between each candidate point and lhs
            projected_distances = min_projected_distances(lhs, candidate_points)
    
            if not alpha:
                max_projected_distance = np.max(projected_distances)
                alpha = (max_projected_distance / 2 * num_points) * alpha_scale
                print(f'Attempting to get new LHS points using mc_intersite_proj_auto_alpha_th() with alpha = {alpha} ...')
    
            # Remove points with projected distance below the projected distance threshold
            projected_distance_threshold = 2 * alpha / num_points
            candidate_points = candidate_points[projected_distances > projected_distance_threshold]
    
            # Calculate intersite distances between each candidate point and lhs
            intersite_distances = min_intersite_distances(lhs, candidate_points)
    
            # Lower value of alpha and continue algorithm
            if np.all(intersite_distances == 0):
                print('ERROR: Only zero elements found in objective function. Reducing alpha and retrying... ###')
                alpha = alpha * 0.95 #alpha_scale
                return self.mc_intersite_proj_alpha_th(num_points_max=num_points_max, lhs=lhs, alpha=alpha)
    
            # Add point to LHS that maximises objective function
            best_point = candidate_points[np.argmax(intersite_distances)]
            lhs = np.vstack((lhs, best_point))
    
            num_points, num_dims = lhs.shape
            print(f'Point added.  New number of points: {lhs.shape[0]}')
    
        return lhs

    def DOE(self,dd,nn):
        '''
        This function call the requested DOE generating function based on the self.dsgn parameter
        **Parameters**
            * **dd** (int): number of dimensions
            * **nn** (int): number of samples
        **Return**
            * **self.dsgn(dd,nn)** (ndarray): requested DOE in a n-darray bounded in [0,1]^d
        '''
        if self.dsgn=='floor_FF':
            return self.floor_full_factorial(dd, nn)
        elif self.dsgn=='LHS':
            return self.LHS(dd,nn)
        elif self.dsgn=='LHSM':
            return self.LHSM(dd,nn)
        elif self.dsgn=='LHS_light':
            return self.LHSchaospy(dd,nn)
        elif self.dsgn=='LHS_opti':
            return get_initial_lhs(None, dd,nn)    #get_initial_lhs(None, dd,nn)       load_opti_DOE(dd,nn)
        elif self.dsgn=='LHS':
            return self.halton(dd,nn)
        elif self.dsgn=='Sobol':
            return self.sobol(dd,nn)
        elif self.dsgn=='Halton':
            return self.halton(dd,nn)
        elif self.dsgn=='MIPT':
            return self.mc_intersite_proj_auto_alpha_th(dd,nn,num_points_start=self.nn_start)      
        elif self.dsgn=='MqPLHS':
            return mc_quasi_lhs(dd, nn, num_points_start=self.nn_start)
        elif self.dsgn=='FpPLHS':
            return main_PLHS_loop(dd, nn, num_points_start=self.nn_start)
                                     

def checkSavedDOE(self):
    '''
    In this function we need to verify that the DOE the you want to load is consistent
    with the input features declared in the userFile. If this check is passed succesfully,
    then  the DOE is loaded from the pickle
    
    **Parameters:**
        * **self** (class): Opti_Design class including the necessary information about DOE
    
    **Return:**
        * **loadedPickle['DOE']** (ndarray): DOE from pickle
    '''
    
    loadedPickle = pickle.load(open(os.path.join(self.dictn,self.DOE_pickle), "rb" ))
    
    # if the the savedDOE is consistent with the current user interface
    if loadedPickle['inParDict'] == self.input_param and loadedPickle['resNam'] == self.response_fun and len(loadedPickle['DOE']) == self.settings['Designs']['Cont_Design']['Starting_Number']:
        print('DOE pickle loaded successfully')
        return loadedPickle['DOE']
    else:
        print('ERROR - DOE NOT compatible. CS - OPT prematurely terminated')
        self.clog.header()
        self.clog.error('CS - OPT prematurely terminated. Verify the consistence of input param dictionary, responses and DOE size of the pickle with your current UserInterface file')
        # terminate the script
        return sys.exit()
