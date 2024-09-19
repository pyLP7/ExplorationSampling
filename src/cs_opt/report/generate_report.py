# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 11:29:20 2021

@author: lual_pi
"""

import pandas as pd
import pickle, os
from string import Template
import base_latex
from pathlib import Path
import shutil
import subprocess
import tempfile


# %% Load pickle for testing goals

loadDOE_BROKEN = pickle.load(open('DOE_saved_100_edit.p', 'rb'))

DOE, responseData = loadDOE_BROKEN['DOE'], loadDOE_BROKEN['responseData']
inParDict, resNam = loadDOE_BROKEN['inParDict'], loadDOE_BROKEN['resNam']
CompareList, ifconstraintsarefulfilled = loadDOE_BROKEN['CompareList'], loadDOE_BROKEN['ifconstraintsarefulfilled']
resultList, ifterminationworkedwell = loadDOE_BROKEN['ResultList'], loadDOE_BROKEN['ifterminationworkedwell'],

filename = "CS_Opt_Report"

# %% main code

import argparse
import os
import subprocess

design_list = ['000'+str(ii+1) for ii in range(min(9,DOE.shape[0]-1))]
if DOE.shape[0] >=10:
    design_list = design_list+['00'+str(ii) for ii in range(10,min(99,DOE.shape[0])+1)]
if DOE.shape[0] >=100:
    design_list = design_list+['0'+str(ii) for ii in range(100,min(999,DOE.shape[0])+1)]

df_DOE = pd.DataFrame(data=DOE)
df_res = pd.DataFrame(data=responseData)

# get if the DbI are numbers and transform them to integers
for ii, key in enumerate(inParDict):
    if inParDict[key]['value_type']=='ORDINALDISCRETE_INDEX' or inParDict[key]['value_type']=='O_I':
        try: df_DOE[ii]=df_DOE[ii].astype(int)
        except: pass
    

df_DOE['Design \#']=design_list
df_res['Design \#']=design_list
df_DOE=df_DOE.set_index('Design \#')
df_res=df_res.set_index('Design \#')


for ii in range(len(inParDict.keys())):
    df_DOE = df_DOE.rename(columns={ii: r"$x_{"+str(ii+1)+"}$"})
    
res_name=[r'''$\bm{f(x)}$''']
df_res = df_res.rename(columns={0: res_name[0]})

for ii in range(len(resNam.keys())-1):
    res_name.append(r"$\bm{g_{"+str(ii+1)+"}(x)}$")
    df_res = df_res.rename(columns={ii+1: res_name[ii+1]})
    
    
df =pd.concat([df_DOE,df_res],axis=1)

# %% read and edit the Latex template

def create(filename='cs_opt_Autoreport'):
        temp_obj = Template(base_latex.content_latex)
        
        tex_file = (Path(__file__).parent / (filename+'.tex')).resolve() #make the path absolute, resolving any simlinks
        print('pause')
        
        subs={}
        subs['table']=df.to_latex(index=True, longtable=False, escape=False, index_names=False, float_format="%.3f")
        
        # str_out = temp_obj.substitute(table=subs['table'])
        str_out = temp_obj.safe_substitute()
        
        with open(tex_file, "wb") as outfile:
            outfile.write(str_out.encode('utf-8'))
        
        
        cmd = ['pdflatex', '-interaction', 'nonstopmode', filename+'.tex']
        proc = subprocess.Popen(cmd)
        proc.communicate()
        
        retcode = proc.returncode
        if not retcode == 0:
            os.unlink(filename+'.pdf')
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 
            
        # delete some unnecessary files
        os.unlink(filename+'.log')
        os.unlink(filename+'.aux')
        os.unlink(filename+'.out')
        
# %% call functions 
create()

# %% TODO
'''
Main problem to be fixed: 
    1. compiling a .tex file with python and with a text editor (with the same code) lead to different results
    2. longtable has to be hardcoded (so far pylatex has some issues)
    3. handling mathematical expression and the module Template from string
    4. hardcoding of mini latex package 
    5. left-flush alignement of the boundary conditions
    6.further test with more than 20 (features) + 10 (response functions)
 '''





