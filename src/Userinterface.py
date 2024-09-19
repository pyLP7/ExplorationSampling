import os
from cs_opt import Opti_Design


def programming():

    # Names of parameters with type, range and ref_value, for continuous variables a jumpsize is needed.
    input_param = {
                        # 't_1': {'range': [-4.5, 4.0], 'ref_value': 1.0,
                        #         'value_type': 'CONTINUOUS', 'jumpsize': 0.01},
                        # 't_2': {'range': [-4.5, 5.0], 'ref_value': 1.0,
                        #         'value_type': 'C', 'jumpsize': 0.01},
                        # 't_3': {'range': [-4.5, 4.0], 'ref_value': 1.0,
                        #         'value_type': 'C', 'jumpsize': 0.01},
                        # 't_4': {'range': [-4.5, 4.0], 'ref_value': 1.0,
                        #         'value_type': 'C', 'jumpsize': 0.001},
                        # 't_5': {'range': [-4.5, 4.0], 'ref_value': 1.0,
                        #         'value_type': 'C', 'jumpsize': 0.001},
                        'M_ID_1': {'range':[2000,2010,2090,5120,5500],'ref_value':5120,
                                      'value_type':'ORDINALDISCRETE_INDEX'},
                        'M_ID_2': {'range':[2000,2010,2090,5120,5500],'ref_value':5120,
                                      'value_type':'O_I'},
                        # 'M_ID_3': {'range':[2000,2010,2090,5120,5500],'ref_value':5120,
                        #             'value_type':'O_I'}
                        }

    # all output function names with the file where the results are stored
    response_fun = {'ObjectiveFunction f(x)': {'Output_File': 'OptiResponses.out'},
                    # 'Sphere g(x)': {'Output_File': 'OptiResponses.out'},
                    # 'f(x) = x1': {'Output_File': 'OptiResponses.out'},
                    # 'f(x) = x2': {'Output_File': 'OptiResponses.out'},
                    
                    # 'Con3':{'Output_File':'OptiResponses.out'},
                    # 'Sin function constraint': {'Output_File': 'OptiResponses.out'},
                           
                     #    'Con4':{'Output_File':'OptiResponses.out'}
                     }
    # specifying the objective function
    objective_fun = {'ObjectiveFunction f(x)': {'goal': 'MIN'}} # MIN, MAX

    # definition of the constraints
    constraint_fun = {
        # 'Sphere g(x)': {'sign': 'LESS', 'value': 9.0}, # GREATER, LESS, EQUAL
        # 'f(x) = x1': {'sign': 'GREATER', 'value': 1.0}, # GREATER, LESS, EQUAL
        # # 'f(x) = x2': {'sign': 'GREATER', 'value': 0.0}, # GREATER, LESS, EQUAL
        # 'Con3':{'sign':'GREATER', 'value':-5.0,},
       # 'Sin function constraint': {'value': 4.0, 'sign': 'LESS'},
    }

    settings = {'DOE': {'DOE_type': 'Sobol',  # LHSM, Sobol, Halton, LHS_light, LHS_opti, MIPT, MqPLHS, FpPLHS, floor_FF
                        'ExistingDOE': {'loadDOE': False,            # If true an existing DOE is loaded
                                        'DOEpickle': 'DOE_saved.p'}, # name of the pickle to be dumped/loaded
                        'BackupSavings': {'pickleBackup': 'backup.p'}},    # File where to save the backup DOES
                # Details on the Designs
                'Designs': {'Dis_Design': {'Name': r'dis_designs/Dis_Design',
                                           'Starting_Number': 20,
                                           'Maximum_Number': 26,
                                           'Final_Design': 'dis_results',
                                           'EndFile': 'Results_dis.txt',
                                           'EndPlot': 'Conver_dis.png'},
                            'Cont_Design': {'Name': r'cont_designs/Cont_Design',
                                            'Starting_Number': 40,
                                            'Maximum_Number': 55,
                                            'Final_Design': 'cont_results',
                                            'EndFile': 'Results_cont.txt',
                                            'EndPlot': 'Conver_cont.png'}},

                'Workspace': {'Python_Executer': r'C:/Anaconda3/python.exe', # solver path (please leave it as reg expression)
                              'Working_dir': r'D:/09-TEST/my_working_dir', #os.getcwd() # path of the InitialDesign folder
                              'Initial_Design': 'Test_InitialDesign',
                              'Input_File': ['TestMaster.key',], # Key file with ref_values
                              'Master_File': 'AckleyDiscrete2_Master.py', # Master file name inside the Initial Design #Discrete_Master, Ackley_2_Master.py
                              'Bat_File': '',
                              'Termination_File': 'OptiResponses.out', # Termination name for checks inside the termination file
                              'Termination_Name': 'Termination check(Error=0; Normal=1)',
                              },
                'metamodels_plot': {'active': False, # shows plots if  two continuous variables and no discrete ones are given
                                    'countour_plot': True,
                                    'resolution': 30,
                                    'X1-Axis': 't_1',
                                    'X2-Axis': 't_2',
                                    'format_type': 'svg', # e.g. png, pdf, svg, eps
                       }
                }

    # %% Display settings

    # plots convergence check plots
    plot_convergence_checks = False

    # decides if a log_file is written or not
    log_file = True
    
    # if set true you get all details of the SCIP optimization
    show_SCIP_Steps = False
    
    # %% Advanced settings
    
    # minimal error for termination
    epsilon = 0.0001

    # maximal number of parallel executable jobs
    parallel_jobs = 4

    # number for cross validation in meta model choice
    cv = 10
    
    # 'r2','explained_variance','neg_mean_squared_error','neg_median_absolute_error','max_error'
    CV_scoring = 'neg_mean_squared_error'

    # maximal time per optimization step
    max_time_SCIP = 20

    max_time_Grad = 10

    # all given options of kernels for Gauss meta models
    model_options = [
        'Gauss_RBF',
        'Gauss_Dot',
        'Gauss_Quad',
        'Gauss_Sum',
        'Gauss_Matern',
        'Gauss_MaternQuad'
        ]

    # different encoding methods
    encoding =  'One-Hot' # 'Label' # 'One-Hot'  # Logarithmic

    # If set true after a full discrete optimization loop another one with fixed discrete parameters is executed
    fine_Tuning_Loop = False

    # defines the modification of different constraints with start value
    modify_constraints = True
    modification_value = 0.5

    # allows to use the described local search heuristic
    use_Localsearch = False

    # uses a random seed for repeatability. If None or False, randomly assigned by time.time()
    random_seed = 445
    


    Design = Opti_Design.Opti_Design(
        settings=settings,
        response_fun=response_fun,
        input_param=input_param,
        constraint_fun=constraint_fun,
        objective_fun=objective_fun,
        epsilon=epsilon,
        parallel_jobs=parallel_jobs,
        cv=cv,
        max_time_SCIP=max_time_SCIP,
        max_time_Grad=max_time_Grad,
        CV_scoring=CV_scoring,
        model_options=model_options,
        encoding=encoding,
        fine_Tuning_Loop=fine_Tuning_Loop,
        show_SCIP_Steps=show_SCIP_Steps,
        modify_constraints=modify_constraints,
        modification_value=modification_value,
        use_Localsearch=use_Localsearch,
        plot_convergence_checks=plot_convergence_checks,
        random_seed=random_seed,
        log_file=log_file)

    Design.design()


if __name__ == "__main__":

    programming()
