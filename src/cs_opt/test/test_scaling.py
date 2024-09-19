# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 09:17:57 2021

@author: lual_pi
"""

import unittest 
# import test_DOE
import cs_opt
from cs_opt import _DOE_class
from cs_opt._DOE_class import DOE_Class
from cs_opt import _sorting_and_scaling
# from Opti_Design import Opti_Design
# import Userinterface
import numpy as np



class TestScaling(unittest.TestCase):
    # all the test function within this class have to start with test_

    
    def setUp(self):
        # self.initInst = Userinterface.programming()
        self.nn=1
        self.response = [1.2,
                         3.5,
                         7.9,
                         -5.4,
                         2.9,
                         -12.3]
        self.outputname='sphere function'
        print('setup class')
    
    
    def test_scaling(self):
        print('test response scaling')
        foo = type('FooClass', (), {'response_dict':{}, 'Krun': 7})
        expected_output = np.array([ 0.23611533,  
                                    0.58275272,  
                                    1.24588513, 
                                    -0.75858329,  
                                    0.49232558,
                                    -1.79849547])
        
        output = _sorting_and_scaling.scale_response(foo,self.response,self.outputname,None)
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
    