import numpy as np

# %% test functions used for evaluation

def ackley_1d(X):
    return -20 * np.exp(-0.2 * np.sqrt(X*X)) -np.exp((np.cos(2*np.pi*X))) + 20 + np.exp(1)

def ackley(X, Y=None):
    X = np.atleast_2d(X)

    pp,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 1:
        res = -20 * np.exp(-0.2*np.sqrt(X*X)) -np.exp((np.cos(2*np.pi*X))) + 20 + np.exp(1)
        
    elif Y_bool:
    
        sum_sq_term = -20 * np.exp(-0.2 * np.sqrt((X*X + Y*Y) / 2))
        cos_term = -np.exp((np.cos(2*np.pi*X) + np.cos(2*np.pi*Y)) / 2)
        res = 20 + np.exp(1) + sum_sq_term + cos_term
    
    else:
        sum_sq_term = -20 * np.exp(-0.2 * np.sqrt(1/dd*(X**2).sum(axis=1)))
        cos_term = -np.exp(1/dd*(np.cos(2*np.pi*X).sum(axis=1)))
        res = (20 + np.exp(1) + sum_sq_term + cos_term)
    return res

def beale(X):
    X = np.atleast_2d(X)
    res = (1.5 - X[:,0] + X[:,0]*X[:,1])**2 + (2.25 - X[:,0] + X[:,0]*X[:,1]**2)**2 + (2.625 - X[:,0] + X[:,0]*X[:,1]**3)**2
    return res

def damped_oscillation(X):
    return np.cos(2 * np.pi * X*1.5) * np.exp(-X)

def drop_wave(X,Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 2 and not Y_bool:
        frac1 = 1 + np.cos(12*np.sqrt(X[:,0]**2+X[:,1]**2))
        frac2 = 0.5*(X[:,0]**2+X[:,1]**2) + 2

    elif Y_bool:
        frac1 = 1 + np.cos(12*np.sqrt(X**2+Y**2))
        frac2 = 0.5*(X**2+Y**2) + 2
        
    res = -frac1/frac2
    return res


def easom(X, Y=None):
    X = np.atleast_2d(X)
    Y_bool = type(Y) is np.ndarray
    if not Y_bool: 
        res = -1.0*np.cos(X[:,0])*np.cos(X[:,1])*np.exp(-(np.power(X[:,0]-np.pi,2)+np.power(X[:,1]-np.pi,2)))
    else:
        res = -1.0*np.cos(X)*np.cos(Y)*np.exp(-(np.power(X-np.pi,2)+np.power(Y-np.pi,2)))
    return res

def goldstein_price(X,Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 2 and not Y_bool:
        fact1a = (X[:,0] + X[:,1] + 1)**2
        fact1b = 19 - 14*X[:,0] + 3*X[:,0]**2 - 14*X[:,1] + 6*X[:,0]*X[:,1] + 3*X[:,1]**2
        fact1 = 1 + fact1a*fact1b
        
        fact2a = (2*X[:,0] - 3*X[:,1])**2
        fact2b = 18 - 32*X[:,0] + 12*X[:,0]**2 + 48*X[:,1] - 36*X[:,0]*X[:,1] + 27*X[:,1]**2
    
    elif Y_bool:
        fact1a = (X + Y + 1)**2
        fact1b = 19 - 14*X + 3*X**2 - 14*Y + 6*X*Y + 3*Y**2
        fact1 = 1 + fact1a*fact1b
        
        fact2a = (2*X - 3*Y)**2
        fact2b = 18 - 32*X + 12*X**2 + 48*Y - 36*X*Y + 27*Y**2
        
    fact2 = 30 + fact2a*fact2b
    res=fact1*fact2
    return res

def ishigami(X,Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 2 and not Y_bool:
        term1 = np.sin(X[:,0]);
        term2 = 7 * (np.sin(2*np.pi))**2; # reduction to a 2D function
        term3 = 0.1 * X[:,1]**4 *np.sin(X[:,0])
    elif Y_bool:
        term1 = np.sin(X)
        term2 = 7 * (np.sin(2*np.pi))**2 # reduction to a 2D function
        term3 = 0.1 * Y**4 *np.sin(X)
    return term1 + term2 + term3

def michalewicz(X,Y=None ):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 2 and not Y_bool:
        summation = np.sin(X[:,0])*(np.sin(1*X[:,0]**2/np.pi))**(2*10) + np.sin(X[:,1])*(np.sin(2*X[:,1]**2/np.pi))**(2*10)
    elif Y_bool:
        summation = np.sin(X)*(np.sin(1*X**2/np.pi))**(2*10) + np.sin(Y)*(np.sin(2*Y**2/np.pi))**(2*10)
        
    res = -summation
    return res

def peaks(X, Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    
    if dd == 1:
        res = 3*(1-X**2)*np.exp(-X**2-1) - (2*X-10*X**3)*np.exp(-X**2)
    elif dd == 2 and not Y_bool:
        res = 3*(1-X[:,0])**2*np.exp(-(X[:,0]**2) - (X[:,1]+1)**2)- 10*(X[:,0]/5 - X[:,0]**3 
         - X[:,1]**5)*np.exp(-X[:,0]**2-X[:,1]**2)- 1/3*np.exp(-(X[:,0]+1)**2 - X[:,1]**2)
    elif Y_bool:
        res = 3*(1-X)**2*np.exp(-(X**2) - (Y+1)**2)- 10*(X/5 - X**3 
         - Y**5)*np.exp(-X**2-Y**2)- 1/3*np.exp(-(X+1)**2 - Y**2)
    else:
        print('1 or 2-D array accepted')
    return res

def rosenbrock(X, Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    res = 0
    if dd == 2 and not Y_bool:
        for ii in range(dd-1):
            res += 100*np.power(X[:,ii+1]-np.power(X[:,ii],2),2)+np.power(X[:,ii]-1,2)
    elif Y_bool:
        res = (1.-X)**2 + 100.*(Y-X*X)**2
    return res


def shubert(X, Y=None):
    X = np.atleast_2d(X)
    n = 5
    tmp1 = 0
    tmp2 = 0
    Y_bool = type(Y) is np.ndarray
    if not Y_bool:
        for ii in range(n):
            tmp1 += (ii+1)*np.cos((ii+1)+(ii+2)*X[:,0])
            tmp2 += (ii+1)*np.cos((ii+1)+(ii+2)*X[:,1])
    else:
        for ii in range(n):
            tmp1 += (ii+1)*np.cos((ii+1)+(ii+2)*X)
            tmp2 += (ii+1)*np.cos((ii+1)+(ii+2)*Y)
    return tmp1*tmp2

def sphere(X, Y=None):
    X = np.atleast_2d(X)
    nn,dd = X.shape
    Y_bool = type(Y) is np.ndarray
    if dd == 2 and Y_bool:
        res = X**2 + Y**2
    else:
        res = sum([X[:,ii] ** 2 for ii in range(dd)])
    return res