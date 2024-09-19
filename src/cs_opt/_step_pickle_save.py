import pickle, os
from tabulate import tabulate


def save_tmp(filename, start_DOE_size, wd):
    '''

    Saves the convergence table in case of breakdown for later usage and control.

    Parameters
    ----------
    filename : str
        name of the file in which the pickle should be stored.
    start_DOE_size : int
        size of the Start-DOE. Necessary in order to know what part of the DOE is calculated by the optimization part.

    '''
    pickle_filename = os.path.join(wd, filename)
    conv_filename = os.path.join(wd, 'convergence_check.txt')
    
    loadDOE = pickle.load(open(filename, 'rb'))
    Table = tabulate(
        loadDOE['data'],
        headers=loadDOE['headers'],
        tablefmt="grid")
    
    # save tmp txt file 
    file = open(conv_filename, 'w')
    file.write(Table)
    file.close()
