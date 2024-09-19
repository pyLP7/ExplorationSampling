# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 15:55:33 2018

@author: sturm
"""


import functions

# Solver Call
functions.local_Dyna(input_file = 'Master.key',ncpu = -4, Version = 11.0, Precision = 's', dyna_Memory = '900m')


# Reset Optiresponse Output file
functions.reset()
# Print out last internal energy value
# cs_dyna_post.glstat('Int', 'last', 'OptiResponses.out', 'no', 0)
# cs_dyna_post.glstat('Int', 'last', 'OptiResponses.out', 'yes', 0)
functions.glstat('Int', 'last', 'OptiResponses.out', 'no', 0)
functions.mass_output([1,2,3],'OptiResponses.out',0)

# Print out last normalized internal energy value
# functions.glstat('Int','last', 'OptiResponses.out', 'yes', 0)
# Print Energy plot for controling
# functions.glstat('Int','plt','OptiResponses.out', 'no', 0)
# Print out global mass
# functions.mass_output('all','OptiResponses.out')
# Termination check
functions.termination_check() 