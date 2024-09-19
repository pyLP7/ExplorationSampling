# -*- coding: utf-8 -*-
"""
CS - DYNA -Postprocessor 

Author  Ralf Sturm

Version V1.0
"""
#
import os, subprocess
import matplotlib.pyplot as plt
import shutil;
import glob;
import sys
import time
import numpy as np
start_time = time.time()
#
# Function to check for a file
def exists(filename = 'OptiResponses.out' ): 
  actualPath = os.getcwd()
  if os.path.isfile(actualPath + '/'+filename) == True:  
    return 1 
  else: 
    return 0 

def reset(filename = 'OptiResponses.out'):
    """
    Resets the outputfile by recreating the file \n
    """
    fobj = open(filename,'w')
    fobj.close()  	
	
# Function to check for a file
def output_create(name,variable): 
    """
    Generates an defined output line for the output Opti-Response-file \n
    """
    
    input_line = []
    input_line.append(format(name,'<75') + '=' +  format(str(variable), '>40')+'\n') 
    input_line.append('\n')     
    return(input_line)

# returns the line input between two definied positions
def return_value(line_list,linenumber,pos1,pos2,add_lines=0): 
    """
    Returns the line fragment of a line in a list of lines regarding position in line (between pos1 and pos2)
    The add_lines adds and substracts the linenumber from the given linenumber to read lines above and below
    
    """
    s=line_list[linenumber+add_lines]
    value=s.rstrip()[pos1:pos2]
    return(value)

# returns the line input regarding with positions number reagrding white space  
def return_value_2(line_list,linenumber,pos,add_lines=0): 
    """
    Returns the line fragment of a line in a list of lines regarding the position in line devided by white spaces
    The add_lines adds and substracts the linenumber from the given linenumber to read lines above and below
    
    """
    s=line_list[linenumber+add_lines]
    value=s.split()[pos]
    return(value)     

def function_pos_flag_return(function,mode ='no'):
    """
    Returns the position of the requested output value or the position of complete function values. Mode = 'yes' activiates  
    the normalized input if requested
    """
    if  function == 'max':
            pos_flag = 1  # pos_flag endspricht Position in Output liste
    elif  function == 'min':
            pos_flag = 2
    elif function == 'average':
            pos_flag = 3
    elif  function == 'init':
            pos_flag = 4
    elif  function == 'last':
            pos_flag = 5
    elif  function == 'curve' or function == 'plt' or  function == 'crv+plt':
            pos_flag = 0
    else:
            print('function output mode is not existent./n Please use min,max,average,init,last,curve,plt,crv+plt')
        

    if mode == 'yes': 
    # Changing position to normilized Output (if exists)
            pos_flag = pos_flag + 9
    
    return(pos_flag)
    
def function_create(name,variable):
    """
    Generates an defined output line for the curve output file \n
    """
    input_line = []
    input_line.append(format(name,'<75') + '=' +  format(str(variable), '>40')+'\n')     
    return(input_line)
    
def plot_function(time,list1,list2 = 'ne' ,list3 = 'ne',list4 = 'ne',x_axis='Time [s]',y_axis = 'Energy',name1 = 'curve out',name2 = 'curve out 2',name3 = 'curve out 3',name4 = 'curve out 4'):   
    """
    Generates a png-plot of the requested curve information     \n
    """    
    font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 16,
        }
    plt.plot(time, list1, label=name1,linestyle='-',linewidth=2,color='k')
    if list2 != 'ne':
        plt.plot(time, list2, label=name2,linestyle='-',linewidth=2,color='r')
    if list3 != 'ne':
        plt.plot(time, list3, label=name3,linestyle='-',linewidth=2,color='g')
    if list4 != 'ne':
        plt.plot(time, list4, label=name4,linestyle='-',linewidth=2,color='b')

    plt.legend(loc='best', shadow=True, prop={'size':12})
    plt.xlabel(x_axis, fontdict=font)
    plt.ylabel(y_axis, fontdict=font)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize = 14)          
    #legend = pad_inches=20 
    plt.grid() 

    plt.savefig(fname=name1, bbox_inches="tight")
              
def get_mass(part='0',output='list'):
    """
    Returns the mass of the requested parts \n
    
    Output selection over part parameter:\n
    
    '0','total'    = return total mass\n
    'Part_ID'      = returns the mass of Part with 'Part_id'\n
    'all'          = return the masses of all parts\n
    ['1','2','5'] = returns the sum of masses defined in the P_id list [list definition]\n
       
    Output-Definition:
        
    'list' = Returns the List with all requested parts and name
    'value'= Returns only the requestes mass value 
   
    """ 
    try:
        dict_mass
    except:
            get_mass_list()
    # prüfen ob liste oder nur ein Wert angegeben
    if isinstance(part, list): 
        mass=0
        name = '['
        for ii in range(len(part)):
           part_id = part[ii]
           #print(dict_mass[part][1]) 
           mass = mass + float(dict_mass[part_id][1])
           name = name + str(part[ii])+'+'
        name= name[:-1]
        dict_mass[name]=[]
        dict_mass[name].append('- Sum of part masses]')
        dict_mass[name].append(mass)
        part = 'sum'
           
    # Die Totale Masse soll geschrieben werden
    if part == 'total'or part == '0':
          part = '0'
          number = part
          part=[]
          part.append(number)
    # Alle Parts sollen geschrieben werden
    elif part == 'all':
          part=[]
          for key, value in dict_mass.items():
              part.append(key)
    # only one part
    elif part in dict_mass.keys():
         number = part 
         part=[]
         part.append(number)
    # Calculation of the summ of the parts
    elif part == 'sum':
         part=[]
         part.append(name)
    
    # Return of mass list or mass value
    if output == 'value':         
        mass = dict_mass[0][1]
        return(mass)
    else:
        return(part)
    return(mass)
     

#===============================================================================
# Auslesen der Massenwert und Partname
#===============================================================================
# Auslesen der Massen aus dem d3hsp File und Ausgabe einer Dictionary mit allen  
# Ausgaben
#    
def get_mass_list():
    actualPath = os.getcwd()
    fobj = open(actualPath + '/'+'d3hsp')
    f = fobj.readlines()
    fobj.close()
    i=0
    global dict_mass 
    dict_mass = {}
    
    
    
    for line in f: # Auslesen PART ID und Name
        i = i + 1
        if line.find('part     id') != -1:
    
                part_id= int(line.split()[3])
                part_name = f[i-3]
                part_name  = part_name .rstrip() and part_name .strip()
                dict_mass[part_id]=[]
                dict_mass[part_id].append(part_name)                        

        if line.find(' t o t a l  m a s s          =') != -1:
    
                part_id= '0'
                part_name  = 'TOTAL MASS'
                dict_mass[part_id]=[]
                dict_mass[part_id].append(part_name)
                mass=f[i-1]
                mass = mass.split()[10]
                dict_mass[part_id].append(mass)

        if line.startswith(str('  m a s s   p r o p e r t i e s   o f   p a r t #'))  or line.startswith(str('  m a s s   p r o p e r t i e s  o f  rigid body material #')) or line.find('becomes part of rigid body') != -1 :
            ii = i
            ff=f
            del ff[:ii-1]
            break
        
     
    ii=0
    for line in ff:
        ii = ii + 1 
        if line.startswith(str('  m a s s   p r o p e r t i e s   o f   p a r t #')):
                key = int((line[49:57]))
                mass= float(ff[ii][34:49])               
                dict_mass[key].append(mass) 
                                                                                            
        if line.startswith(str('  m a s s   p r o p e r t i e s  o f  rigid body material #')):
                key = int((line[59:67]))
                mass= float(ff[ii][34:49])                 
                dict_mass[key].append(mass) 
            
        if line.find(' becomes part of rigid body') != -1:
                key=int(line.strip().split()[2])
                #key = int((line[18:27]))
                dict_mass[key].append(0)
                 
    return dict_mass
    
#===============================================================================
#--------------------- Begin of Post - Output - function ---------------------- 
#===============================================================================
#
#===============================================================================
# 
#   


def mass_output(part = '0',filename = 'Opti_Responses.out', response = 0):
    """
    Mass extraction from mass dictionary for mass ouput \n
    
    Output defintion over part parameter\n
    
    '0','total'    = writes total mass\n
    'Part_ID'      = writes the mass of Part with 'Part_id'\n
    'all'          = writes the masses of all parts\n
    ['1','2','5']  = writes the mass information of the summ of all parts defined in the P_id list [list definition]\n
       
    if response = 1, function returns are dictionary with all part names and the corrsponding masses (no mass
    information is added to the output file) [default response = 0 / no response]

    """
    part = get_mass(part,'list')   
      
    if response == 0:
        actualPath = os.getcwd()
                     
        if os.path.isfile(actualPath + '/'+filename) == True:
            fobj = open(filename,'a')
        else:
            fobj = open(filename,'w')    
        
        
        # Über alle Anfragen Abfrage -Eintrag der Masse in Output File
        for ii in range(len(part)):
            part_id = part[ii]
            mass = dict_mass[part_id][1]
            name = dict_mass[part_id][0]
            name = 'Mass Part ID '+str(part_id)+' '+str(name)
            fobj.writelines(output_create(name,str(mass)))
    
        fobj.close()
    else:
        return(dict_mass)
    
    
#
#===============================================================================
# Allgemeine Prüfung der Simulation
#===============================================================================    
#
def termination_check(filename = 'OptiResponses.out', response = 0):
    """
    Function to checks the final status of the simulation\n
    
    Writes in the outputfile 
    
    termination = 1 for N o r m a l    t e r m i n a t i o n 
    termination = 0 for E r r o r  t e r m i n a t i o n 
       
    if function 'reponse' is aktivated, the function returns '1' for '0'
    for further use. If the function is used as a response function no
    termination flag ist added to the Opti-Response file
    
    if response = 0, termination flag is added to the reponse file and no 
    function values 
    
    """
    actualPath = os.getcwd()
    
    if os.path.isfile(actualPath + '/'+'d3hsp') == True:
        
        if 'N o r m a l    t e r m i n a t i o n' in open(actualPath + '/'+'d3hsp').read():
            flag=1
        else:
            flag=0    
    else:
        print('d3hsp file is missing for termination check')       
        flag = 0 # Could not be found ->

     
    if response == 1: # Used as a response function
    
            if flag == 1: # Normal Termination
                
                return(1)
                
            else: # Error Termination
                
                return(0)
                
    else:# Response is written to outputfile
                                    
            if exists() == 1:
                fobj = open(filename,'a')
            else:
                fobj = open(filename,'w')        
                
            name = 'Termination check(Error=0; Normal=1)'

            fobj.writelines(output_create(name,str(flag))) 
#
#===============================================================================
# Auslesen der Energiewerte - GLSTAT
#===============================================================================
            
def glstat(Energy_type = 'Int',function = 'max', filename = 'OptiResponses.out', normalize = 'no', response = 0 ):
    """
    
    Glstat global Energy Output Extraction after Simulation from glstat to file 
   
    Energy_type to be extracted:  

    'Int'    = Global Internal Energy Output       
    'Kin'    = Final Global Kinetic Energy Output    
    'Total'  = Final Total global Energy Output      
    'Ex_Work'= Final External Work  Output               
    'Hour'   =  Final Hourglass  Output                
    weitere  = 'glob_x_vel', 'glob_y_vel','glob_z_vel','time step'
             = 'spring_damp_en'
    
    'function': Definition of the function value to be extracted:
    'min','max','average','init','last','curve','plt','crv+plt'
    
    normalize flag: 'yes' or 'no' (no = default):
    By activating the normalization flags all energy outputs are normalized by  
    the total model mass
    
    """
    actualPath = os.getcwd()

    try:
      dict_mass
    except:
      get_mass_list()
      
    global glstat_dic
    glstat_dic={}
    
    

    energyout =['time','time step','kinetic energy','internal energy',
                'spring and damper energy','hourglass energy ','total energy',
                'global x velocity','global y velocity','global z velocity']

    corresp_marker =['time','time step','Kin','Int',
                'spring_damp_en','Hour','Total',
                'glob_x_vel','glob_y_vel','glob_z_vel']

        
    if exists('glstat.') == 1:  
        fobj = open("glstat.")
        f = fobj.readlines()
        fobj.close()
        a=[]
        # Invertieren des Inputs um von hinten einzulesen
        for line in f: 
            a.append(line)
        
        for ii in range(len(energyout)):           
           marker = ' ' + str(energyout[ii]) + '....' 
           funct_values = []
        
           for line in a:
                #
                if line.startswith(str(marker)):
                    value=line.rstrip()[34:46]
                    funct_values.append(float(value))
           glstat_dic[energyout[ii]]=[]

           glstat_dic[energyout[ii]].append(funct_values)

           glstat_dic[energyout[ii]].append(max(funct_values))

           glstat_dic[energyout[ii]].append(min(funct_values))

           glstat_dic[energyout[ii]].append(sum(funct_values)/float(len(funct_values))) 

           glstat_dic[energyout[ii]].append(funct_values[0])   

           glstat_dic[energyout[ii]].append(funct_values[-1])  



        if function == 'min':
            func_type = 2      
        elif function == 'average':  
            func_type =  3    
        elif function == 'init':  
            func_type =  4      
        elif function == 'last':
            func_type =  5 
        elif function ==  'curve': 
            func_type =  0    
        elif function ==  'plt':
            func_type =  0       
        elif function ==  'crv+plt':
            func_type =  0             
        else: 
            func_type =  1           
        

        
        for ii in range(len(corresp_marker)):
            if corresp_marker[ii] == Energy_type: 
                break

        name = energyout[ii] + ' global ['+ str(function)+']'
        value = glstat_dic[energyout[ii]][func_type]
        
        if response == 0: 
        
            if func_type < 6 and func_type > 0:
                    
                if exists() == 1:
                    fobj = open(filename ,'a')
                else:
                    fobj = open(filename ,'w')    
                
               
                if normalize == 'yes':
                    if Energy_type == 'Int' or Energy_type =='Kin' or Energy_type =='Hour'or Energy_type =='Total':
    
                        name = 'Normalized '+ name
                        
                        value = value / float(dict_mass['0'][1])
                
                    fobj.writelines(output_create(name,str(value)))
                else:
                    fobj.writelines(output_create(name,str(value))) 
                    
                    
                fobj.close()
                
            if function  == 'curve' or function  == 'crv+plt':           
    
    
                if normalize == 'yes'and Energy_type == 'int' or Energy_type =='Kin' or Energy_type =='Hour' or Energy_type =='Total':
                               
                   
                    filename = 'glstat_normalized_'+ energyout[ii] +'.crv'
                    fobj = open(filename,'w') 
                    
                    for tt in range(len(glstat_dic[energyout[ii]][0])): 
                        
                        value = glstat_dic[energyout[ii]][0][tt] / float(dict_mass['0'][1])
                        fobj.writelines(function_create(glstat_dic['time'][0][tt],value)) 
                    fobj.close()           
                else: 
                    filename = 'glstat_'+energyout[ii]+'.crv'
                    fobj = open(filename,'w') 
                    
                    for tt in range(len(glstat_dic[energyout[ii]][0])): 
                        fobj.writelines(function_create(glstat_dic['time'][0][tt],glstat_dic[energyout[ii]][0][tt])) 
                    fobj.close()
                
            if function  == 'plt' or function  == 'crv+plt':                     
               if Energy_type == 'Int' or Energy_type == 'Kin' or Energy_type == 'Total' or Energy_type == 'Hour':

                   
                   if normalize == 'yes':
                       list_1_norm=[]
                       list_2_norm=[]
                       list_3_norm=[]
                       list_4_norm=[]
                       for tt in range(len(glstat_dic['total energy'][0])):
                           list_1_norm.append(glstat_dic['total energy'][0][tt]/float(dict_mass['0'][1]))
                           list_2_norm.append(glstat_dic['kinetic energy'][0][tt]/float(dict_mass['0'][1]))
                           list_3_norm.append(glstat_dic['hourglass energy '][0][tt]/float(dict_mass['0'][1]))
                           list_4_norm.append(glstat_dic['internal energy'][0][tt]/float(dict_mass['0'][1]))                   
                  
                       plot_function(time=glstat_dic['time'][0] ,list1=list_1_norm,name1='norm. total energy',\
                                     list2=list_2_norm,name2='norm. kinetic energy',\
                                     list3=list_3_norm,name3='norm. hourglass energy',\
                                     list4=list_4_norm,name4='norm. internal energy',\
                                     y_axis = 'Normalized Energy')
                   else:
                       
                       plot_function(time=glstat_dic['time'][0] ,list1=glstat_dic['total energy'][0],name1='total energy',\
                                     list2=glstat_dic['kinetic energy'][0],name2='kinetic energy',\
                                     list3=glstat_dic['hourglass energy '][0],name3='hourglass energy',\
                                     list4=glstat_dic['internal energy'][0],name4='internal energy')
               else:
                   plot_function(time=glstat_dic['time'][0] ,list1=glstat_dic[energyout[ii]][0],name1=energyout[ii])

        else:
            if normalize == 'yes':
               return(value/float(dict_mass['0'][1]))
               name = 'Normalized '+ name
               print(name)
            else:
               return(value)  
               print(name)                
          

#==============================================================================
#
#==============================================================================
#              Function to intiate an local Dyna Sumalation
#==============================================================================
#
#==============================================================================
    
def local_Dyna(input_file = 'Master.key',ncpu = 3, Version = 10.1, Precision = 's', dyna_Memory = '900m'):
    """ Funktion zum Ausführen eines lokalen Dyna -Jobs

        local_Dyna(input_file = 'Master.key',ncpu = 24, Version = 9.1,Precision = 's', dyna_Memory = '100m'):
            
        Version   = LS - Dyna Version (vorhanden 7.1, 8.1, 9.1, 10.1)  (Default = 10.1) 
        input_file = Definition des Inputfiles (Default = 'Master.key')
        precision = Genauigkeit single = 's'<-> double = 'd' (Default = 's') 
        ncpu = Anzahl CPUs (Default = 3)
        dyna_Memory = Festlegung der Speichergröße (Default = '900m') 
    """
    
    actualPath = os.getcwd()
    print(actualPath)
	# Konstante Parameter wie Dyna-Pfad
    dyna_solver_path               = "C:/Program Files (x86)/Dynamore/LS-DYNA\program/" 
    #===============================================================================
    # Ausführen der Berechnung
    #===============================================================================
    # Version - Selektion
    if Precision == 'd':
        if Version == 9.1:
            dyna_solver                    = 'ls-dyna_smp_d_R901_winx64_ifort131.exe'
        elif Version == 7.1:
            dyna_solver                    = 'ls-dyna_smp_d_R711_winx64_ifort131.exe'
        elif Version == 8.1:
            dyna_solver                    = 'ls-dyna_smp_d_R810_winx64_ifort131.exe'
        elif Version == 10.1:
            dyna_solver                    = 'ls-dyna_smp_d_R101_winx64_ifort131.exe'
        elif Version == 11.0:
            dyna_solver                    = 'ls-dyna_smp_d_R11_0_winx64_ifort131.exe'			
    else: 
        if Version == 9.1:
            dyna_solver                    = 'ls-dyna_smp_s_R901_winx64_ifort131.exe'
        elif Version == 7.1:
            dyna_solver                    = 'ls-dyna_smp_s_R711_winx64_ifort131.exe'
        elif Version == 8.1:
            dyna_solver                    = 'ls-dyna_smp_s_R810_winx64_ifort131.exe' 
        elif Version == 10.1:
            dyna_solver                    = 'ls-dyna_smp_s_R101_winx64_ifort131.exe'
        elif Version == 11.0:
            dyna_solver                    = 'ls-dyna_smp_s_R11_0_winx64_ifort131.exe'
    #
    # Starten der Rechnung
    #
    subprocess.call('"'+ dyna_solver_path + dyna_solver +'" i= '+ actualPath +'/'+ input_file  + ' ncpu=' + str(ncpu) +' memory=' + str(dyna_Memory), shell=True)    

   