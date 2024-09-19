# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 09:17:57 2021

@author: lual_pi
"""

import unittest, os
# import test_DOE


# import the package
import cs_opt
from cs_opt import _DOE_class
# import the antigravity module
# from antigravity import antigravity
# or an object inside the antigravity module
import chaospy, os
os.chdir("..")
# import _DOE_class
import numpy as np


class TestDOE(unittest.TestCase):
    # all the test function within this class have to start with test_
    
    @classmethod
    def setUpClass(cls):
        # might be a right solution if you want to populate a database first
        cls.arg1=10
        cls.arg2=5
        print('setup class method')
    
    def setUp(self):
        self.rs= 42
        self.nn = 10
        self.dd = 2
        print('setup class')
        # might be a right solution if you want to populate a database first
        
    
    # def test_load_opti_DOE(self):
    #     '''testing the function to load the optimal DOE'''
    #     print('test Optimal DOE')        
    #     expected_output = np.array([[0.        , 0.83333333, 0.16666667],
    #                                 [0.16666667, 0.66666667, 0.83333333],
    #                                 [0.33333333, 0.16666667, 0.        ],
    #                                 [0.5       , 0.        , 0.66666667],
    #                                 [0.66666667, 1.        , 0.5       ],
    #                                 [0.83333333, 0.5       , 1.        ],
    #                                 [1.        , 0.33333333, 0.33333333]])
        
    #     print(os.getcwd())
    #     os.chdir("..")
    #     os.chdir("..")
    #     print(os.getcwd())
    #     output = _DOE_class.load_opti_DOE(None,3,7)
    #     np.testing.assert_almost_equal(expected_output, output)
        
    def test_LHSchaospy(self):
        '''testing chaospy LHS'''
        print('test LHS chaospy')  
        foo = type('FooClass', (), {})
        expected_output = np.array([[0.73745, 0.00206, 0.46119],
                                   [0.99507, 0.59699, 0.81395],
                                   [0.5732 , 0.28324, 0.12921],
                                   [0.85987, 0.62123, 0.33664],
                                   [0.3156 , 0.31818, 0.04561],
                                   [0.1156 , 0.71834, 0.57852],
                                   [0.00581, 0.43042, 0.21997],
                                   [0.48662, 0.15248, 0.95142],
                                   [0.66011, 0.84319, 0.75924],
                                   [0.27081, 0.92912, 0.60465]])
        np.random.seed(self.rs)
        output=_DOE_class.DOE_Class.LHSchaospy(foo,3,10)
        np.testing.assert_almost_equal(expected_output, output)
        
    def test_sobol(self):
        '''testing the function to load the optimal DOE'''
        print('test sobol')
        foo = type('FooClass', (), {'response_dict':{}, 'Krun': 7})
        expected_output = np.array([[0.5   , 0.5   , 0.5   , 0.5   ],
                                   [0.75  , 0.25  , 0.75  , 0.25  ],
                                   [0.25  , 0.75  , 0.25  , 0.75  ],
                                   [0.375 , 0.375 , 0.625 , 0.125 ],
                                   [0.875 , 0.875 , 0.125 , 0.625 ],
                                   [0.625 , 0.125 , 0.375 , 0.375 ],
                                   [0.125 , 0.625 , 0.875 , 0.875 ],
                                   [0.1875, 0.3125, 0.3125, 0.6875]])
        
        output = _DOE_class.DOE_Class.sobol(foo,4,8)
        np.testing.assert_almost_equal(expected_output, output)
        
    # def test_check_saved_DOE(self):
    #     '''testing the function to load a previosly saved DOE'''
    #     print('test check saved DOE')
    #     foo = type('FooClass', (), {'settings':{'DOE':{'ExistingDOE':
    #                                 {'DOEpickle':'DOE_saved.p'}}}, 
    #                                 'input_param_dict':{'t_1': {'range': [-4.5, 4.0], 'ref_value': 1.0, 'value_type': 'CONTINUOUS', 'jumpsize': 0.001}, 
    #                                               't_2': {'range': [-4.5, 4.0], 'ref_value': 1.0, 'value_type': 'C', 'jumpsize': 0.001}},
    #                                 'responsenames':{'ObjectiveFunction f(x)': {'Output_File': 'OptiResponses.out'}, 'Sphere g(x)': {'Output_File': 'OptiResponses.out'}},
    #                                 'kind_of_design':{'Starting_Number':20},
    #                                 'Krun': 7})
    #     expected_output = 1
    #     import _cs_log_class
    #     output = _DOE_class.checkSavedDOE(foo)
    #     np.testing.assert_almost_equal(expected_output, output)
        
                
        
if __name__ == '__main__':
    unittest.main()
    