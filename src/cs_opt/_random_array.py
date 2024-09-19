import numpy as np

def sum_func(x,y):
    """add function"""
    return x+y

def np_array(nn=10, dd=2, rs=42):
    """"""
    np.random.seed(rs)
    return np.random.rand(nn,dd)
