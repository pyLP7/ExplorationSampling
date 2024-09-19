# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 09:17:57 2021

@author: lual_pi
"""

import unittest 
# import test_DOE
# import random_array
import cs_opt
import chaospy
from cs_opt import _sorting_and_scaling
from cs_opt import _DOE_class
from cs_opt import _random_array
import numpy as np


class TestCalc(unittest.TestCase):
    # all the test function within this class have to start with test_
    
    @classmethod
    def setUpClass(cls):
        # might be a right solution if you want to populate a database first
        cls.arg1=10
        cls.arg2=5
        print('setup class method')
    
    def setUp(self):
        self.var1=7
        self.var2=2
        self.rs= 42
        self.nn = 10
        self.dd = 2
        print('setup class')
        # might be a right solution if you want to populate a database first
        
    def test_sum_func(self):
        print('test sum')
        self.assertEqual(_random_array.sum_func(self.var1,self.var2), 9)

    
    def test_random_array(self):
        print('test numpy array')
        target_array = np.array([[0.37454012, 0.95071431],
                                [0.73199394, 0.59865848],
                                [0.15601864, 0.15599452],
                                [0.05808361, 0.86617615],
                                [0.60111501, 0.70807258],
                                [0.02058449, 0.96990985],
                                [0.83244264, 0.21233911],
                                [0.18182497, 0.18340451],
                                [0.30424224, 0.52475643],
                                [0.43194502, 0.29122914]])
        # self.assertEqual(calc.np_array(self.nn,self.dd, self.rs), target_array)
        np.testing.assert_almost_equal(target_array, _random_array.np_array(self.nn,self.dd, self.rs))
    
    # def test_scaling(self):
    #     print('test add')
    #     self.assertEqual(self._sorting_and_scaling.scale_response(response, output), [15,22])
            
        
    def test_scale_response_none(self):
        '''test the 0-mean & 1-sd function to scale response values'''
        print('test scaling')
        foo = type('FooClass', (), {'response_dict':{}, 'Krun': 7})
        response = [-1,2,
                    -2.3,
                    -5.0,
                    -4.2,
                    7.1,
                    2.8,
                    7.9,
                    2.7,
                    -9.3]
        expected_output = [-0.22946586,
                           0.523469, 
                           -0.55573764, 
                           -1.23337902, 
                           -1.03259639,
                            1.80345828,
                            0.72425163,
                            2.00424091,
                            0.69915381,
                            -2.31258566]
        output = _sorting_and_scaling.scale_response(foo, response, None)
        np.testing.assert_almost_equal(expected_output, output)
        
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
        
    #     output = _DOE_class.load_opti_DOE(None,3,7)
    #     np.testing.assert_almost_equal(expected_output, output)
        
    def test_LHSchaospy(self):
        '''testing the chaospy LHS'''
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
                
        
        
    # def test_div(self):
    #     print('test divide')
    #     self.assertEqual(calc.divide(10,5), 2)
    #     self.assertEqual(calc.divide(13,3), 4.333333333333333)
        
    #     with self.assertRaises(ValueError):
    #         calc.divide(10,0)
        
        
    # def test_add(self):
    #     self.assertEqual(calc.add(10,5), 15)
        
if __name__ == '__main__':
    unittest.main()
    