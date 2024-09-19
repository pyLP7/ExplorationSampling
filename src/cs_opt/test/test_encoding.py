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
# import Userinterface



class TestCalc(unittest.TestCase):
    # all the test function within this class have to start with test_
    
    @classmethod
    def setUpClass(cls):
        # might be a right solution if you want to populate a database first
        cls.arg1=10
        cls.arg2=5
        print('setup class method')
    
    def setUp(self):
        self.initInst = Userinterface.programming()
        # might be a right solution if you want to populate a database first


        # self.dsgn = 'LHSM'
        # self.repeat = False
        print('setup class')
    
    # def test_DOE(self):
    #     print('test add')
    #     self.assertEqual(DOE_Class.DOE(self.initInst,3,2), [15,22])
    
    # def test_scaling(self):
    #     print('test add')
    #     self.assertEqual(_sorting_and_scaling.Var(self.initInst,30), [15,22])
        

        
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
    