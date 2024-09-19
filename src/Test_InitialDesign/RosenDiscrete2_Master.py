# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 12:16:55 2019

@author: Dorsch
"""
import os, os.path
import re as re_set
import numpy as np

from scipy.optimize import rosen

number_of_discrete = 2

def Sphere(x):
    value=0
    for ii in range(len(x)):
        value=value+x[ii]**2
    return -0.2*value+10

def Sin(x):
    value=0
    for ii in range(len(x)):
        value=value+np.sin(x[ii])
    return value

def f_x1(x):
    return x[0]

def f_x2(x):
    return x[1]

def con1(x):
    if (x[-2%number_of_discrete])%3 ==0:
        return Sphere(x[:-number_of_discrete])
    
    elif (x[-2%number_of_discrete])%3 ==1:
        return 10
    
    else:
        return 8

def con2(x):
    if (x[-1%number_of_discrete])%3 ==0:
        return Sin(x[:-number_of_discrete])
    
    elif (x[-1%number_of_discrete])%3 ==1:
        return 1
    
    else:
        return 3
    
    
def con3(x):
    if (x[-3%number_of_discrete])%3 ==0:
        return f_x1(x[:-number_of_discrete])
    
    elif (x[-3%number_of_discrete])%3 ==1:
        return 0
    
    else:
        return 3
    
def con4(x):
    z = x[-1%number_of_discrete]+x[-2%number_of_discrete]+x[-3%number_of_discrete]
    if z%3 ==0:
        return f_x2(x[:-number_of_discrete])
    
    elif z%3 ==1:
        return 0
    
    else:
        return 3
    
def obj(x):
    return rosen(x[:-number_of_discrete])+sum(x[-number_of_discrete:])/1000

    
inputParameters = ['t_'+str(ii+1) for ii in range(10) ] + ['M_ID_'+str(ii+1) for ii in range(number_of_discrete)]

path=os.getcwd() 
path1='OptiResponses.out'

x=[]
flag=[]
doit=np.ones(len(inputParameters))
for j in range(len(inputParameters)):
    with open(path +'/TestMaster.key','r') as file:
        lines=[]
        for line in file:
            lines.append(line)
        for ii in range(len(lines)):
            line=lines[ii]
            if line.find(inputParameters[j])!=-1 and doit[j]==1:
                index = line.find(inputParameters[j])
                doit[j]=0
                new_line = line[index + len(inputParameters[j]):]
                regexp = re_set.compile(r'.*?([0-9.-]+)')
                match = regexp.match(new_line)
                flag.append(new_line.find(match.group(1)))
                starting_column = index + len(inputParameters[j]) + flag[-1]
                helpvar= match.group(1)
                helpvar=helpvar.strip()
                length=helpvar.count('')-1
                if line[starting_column+length] == 'e' or line[starting_column+length] == 'E':
                    helpvar=helpvar + line[starting_column + length : starting_column + length + 4]
                x.append(float(helpvar))
                break
       
at=os.getcwd()
file=open(path1,"w")
file.write(format('ObjectiveFunction f(x)','<75') + '=' +  format(str(obj(x)), '>40')+'\n')
file.write('\n')
file.write(format('Sphere g(x)','<75') + '=' +  format(str(con1(x)), '>40')+'\n') 
file.write('\n')
file.write(format('Sin function constraint','<75') + '=' +  format(str(con2(x)), '>40')+'\n')
file.write('\n')
file.write(format('f(x) = x1','<75') + '=' +  format(str(con3(x)), '>40')+'\n')
file.write('\n')
file.write(format('f(x) = x2','<75') + '=' +  format(str(con4(x)), '>40')+'\n')
file.write('\n')
file.write('Termination check(Error=0; Normal=1)     =     1')

file.close()
os.chdir(at)