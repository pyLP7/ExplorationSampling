import warnings
import numpy as np
import sys
import select
from tabulate import tabulate
import os
import shutil
import time
import copy
import pickle
import random
from cs_opt import _cs_log_class, _DOE_class, _sorting_and_scaling, _post_process_class, _write_and_read, _pre_process, _new_design, _parallel_job
import matplotlib.pyplot as plt
from itertools import chain

plt.close('all')

plt.ioff()

warnings.filterwarnings("ignore")


class Opti_Design():

    def __init__(
            self,
            response_fun,
            constraint_fun,
            objective_fun,
            input_param,
            settings,
            epsilon,
            parallel_jobs,
            cv,
            max_time_SCIP,
            max_time_Grad,
            CV_scoring,
            model_options,
            encoding,
            fine_Tuning_Loop,
            show_SCIP_Steps,
            modify_constraints,
            modification_value,
            use_Localsearch,
            plot_convergence_checks,
            random_seed,
            log_file):
        '''
        Initialization of the whole algorithmic procedure.

        Parameters
        ----------
        response_fun : dict
            containing all occuring responses with their outpur files.
        constraint_fun : dict
            containing all occuring constraint values as well as the kind of constraint.
        objective_fun : dict
            containing the objective respones and the optimization sense (MIN vs maximize).
        input_param : dict
            containing all variables inlcuding type, values and reference value in the key-file.
        settings : dict
            containing all DOE specifics as well as solver and key-file details.
        epsilon : float
            describing the convergence criterion.
        parallel_jobs : int
            describing the number of parallel jobs.
        cv : int
            describing the number of cross validations executed for choosing the meta models.
        max_time_SCIP : float
            describing the maximal time for an optimization carried out by SCIP.
        max_time_Grad : float
            describing the maximal time for an optimization carried out by GRAD.
        CV_scoring : str
            describing the score used for choosing the meta models.
        model_options : list of str
            containing all options available for meta modeling.
        scale_response : bool
            deciding if the responses should be scaled before meta modeling.
        encoding : str
            deciding which encoding subroutine should be used.
        show_metamodels : bool
            deciding if meta models should be plotted in every step or not.
        fine_Tuning_Loop : bool
            deciding if for mixed problems a second run is executed with fixed integer variables.
        show_SCIP_Steps : bool
            deciding if SCIP shows all calculation steps.
        stop_if_feasible_solution_is_found : bool
            deciding if SCIp stops as soon as a feasible solution is found. Useful if a problem is rather complicated
        SCIP_gap : float
            describing how accurate SCIP must get to terminate. Default is set to 0 and leads to global convergence. The bigger this GAP the less accurate SCIP.
        modify_constraints : bool
            deciding if constraint modification heuristic should be used.
        modification_value : float
            start value for the heuristic modification.
        use_Localsearch : bool
            deciding if Local Search should be used.
        plot_convergence_checks : bool
            deciding if in every adaption step a prognostic convergence is plotted.
        random_seed : int
            describing the used random seeds.
        log_file : bool
            deciding if a log-file is used


        '''

        self.settings = settings
        self.epsilon = epsilon
        self.parallel_jobs = parallel_jobs
        self.cv = cv
        self.max_time_SCIP = max_time_SCIP
        self.max_time_Grad = max_time_Grad
        self.CV_scoring = CV_scoring
        self.model_options = model_options
        self.scale_response = True
        self.encoding = encoding
        self.fine_Tuning_Loop = fine_Tuning_Loop
        self.show_SCIP_Steps = show_SCIP_Steps
        self.stop_if_feasible_solution_is_found = False
        self.SCIP_gap = 0
        self.modify_constraints = modify_constraints
        self.modification_value = modification_value
        self.use_Localsearch = use_Localsearch
        self.convexstep = 0.1
        self.LocalSearch = True
        self.plot_convergence_checks = plot_convergence_checks
        self.show_every_step_pickle = True
        
        if random_seed is None or random_seed is False:
            self.random_seed = int(time.time())
        else:
            self.random_seed = random_seed
            
        random.seed(self.random_seed)
        self.log_file = log_file
        self.parallel = _parallel_job.parallel_processing() #self
        self.mini = next(iter(objective_fun))
        self.mimax = objective_fun[self.mini]['goal']
        self.response_fun = response_fun
        self.constraint_fun = constraint_fun
        self.input_param = input_param
        self.dsgn = _DOE_class.DOE_Class(self.settings['DOE']['DOE_type'],
                                         repeat=self.random_seed).DOE
        
        del_var = _DOE_class.DOE_Class('MIPT', repeat=self.random_seed, sizeRoughDOE=50).DOE
        # %% fix the folder path
        self.dictn = self.settings['Workspace']['Working_dir']     # path for working dir 
        self.src = self.dictn + '\\' + \
            self.settings['Workspace']['Initial_Design']           # path for initial design
        self.DOE_pickle = self.settings['DOE']['ExistingDOE']['DOEpickle']
        self.backup_pickle = self.settings['DOE']['BackupSavings']['pickleBackup']
        self.src_files = os.listdir(self.src)
        self.post_proc = _post_process_class.postProcessing(self)

        self.mydata = []
        self.headers = []
        
        self.plot = {} # $$$
        
        if self.log_file:
            self.clog = _cs_log_class.CS_log(self.dictn)
            self.clog.header()

    def prepare_newfiles(self, number_of_folder, start_number, point_list):
        '''
        
        Here a given number of folders is made for points declared in the point list.
        In those folders the key.files are adapted in order to show the belonging point. 
        Then the solver responses for this key.file are saved.
        Since this should not be done more than necessary, the start_number tells 
        for which points this was already done before.

        Parameters
        ----------
        number_of_files : int
            number of folder which should be prepared.
        start_number : int
            index for the first folder.
        point_list : list of arrays
            list of all corresponding calculated points for which the file is prepared.


        '''

        for i in range(number_of_folder):
            self.define_path(i + start_number)
            
            self.cd = os.path.join(self.dictn,self.path1)

            if os.path.exists(self.cd):
                shutil.rmtree(os.path.join(self.cd))

            os.makedirs(os.path.join(self.cd))
            self.PATH = os.getcwd()
            os.chdir(self.cd)

            for file_name in self.src_files:
                full_file_name = os.path.join(self.src, file_name)
                if (os.path.isfile(full_file_name)):
                    shutil.copy(full_file_name, self.dictn + '\\' + self.path1)

            _write_and_read.write_key_and_solver(self, point_list, i)
            

    def define_path(self, number_of_design):
        '''
        Defining a path where the next design is calculated and the simulations are solved.

        Parameters
        ----------
        number_of_design : int
            number of the prepared design-file.



        '''

        if number_of_design < 9:
            self.path1 = self.KindofDesignsname + \
                '000' + str(number_of_design + 1)
        elif number_of_design < 99:
            self.path1 = self.KindofDesignsname + \
                '00' + str(number_of_design + 1)
        else:
            self.path1 = self.KindofDesignsname + \
                '0' + str(number_of_design + 1)

    def build_table(self):
        '''
        Builds a summarizing table for supervision containing headers and the Data.

        '''

        self.build_header()
        self.build_data()

        self.TABLE = tabulate(
            self.mydata,
            headers=self.headers,
            tablefmt="grid")

    def build_header(self):

        '''
         
        Building the headers for the final table used for documentation.
        
        '''
        self.headers = ['Designs', 'g(x) fulfilled', 'Terminationcheck']

        for i in range(len(self.names)):
            self.headers.append(self.names[i])

        self.headers.append(self.mini)

        for responsename in self.constraint_fun:
            self.headers.append(responsename)

        self.headers.append('CVs f(x)')

        self.headers.append('Kernel f(x)')

        for ik in self.constraint_fun:
            self.headers.append('CVs ' + ik)

        for ik in self.constraint_fun:
            self.headers.append('Kernel ' + ik)

    def build_data(self):
        
        '''
        
        Building the data of all optimization steps containing the meta models,
        the cross validation values, the objective and constraint values etc.
        
        '''

        if self.save_data == []:
            self.mydata = [[] for k in range(len(self.newdesignlist))]
            
        else:
            self.mydata = self.save_data + [[] for k in range(len(self.newdesignlist))]
        
        z = len(self.ResultList) - len(self.newdesignlist)

        for k in range(len(self.save_data),len(self.save_data)+len(self.newdesignlist)):
            self.mydata[k].append(str(k + 1 - len(self.save_data)))
            self.mydata[k].append(self.ifconstraintsarefulfilled[k-len(self.save_data)+z])
            self.mydata[k].append(self.ifterminationworkedwell[k-len(self.save_data)+z])

            for i in range(len(self.newdesignlist[k-len(self.save_data)])):
                self.mydata[k].append(self.newdesignlist[k-len(self.save_data)][i])

            self.mydata[k].append(self.ResultList[k-len(self.save_data) + z][self.mini])

            for responsename in self.constraint_fun:
                self.mydata[k].append(self.ResultList[k + z-len(self.save_data)][responsename])

        for k in range(len(self.save_data),len(self.save_data)+self.Krun):
            self.mydata[k].append('Start-DOE')

        if self.constraint_fun:
            self.cross_CV_GX = np.array(
                self.cross_CV_GX).reshape(-1, len(self.response_fun) - 1)

        for kk in range(len(self.save_data),len(self.save_data)+len(self.CROSSvaluelist)):
            if len(self.newdesignlist) > self.Krun + kk:
                self.mydata[self.Krun + kk].append(self.CROSSvaluelist[kk-len(self.save_data)])
                self.mydata[self.Krun + kk].append(self.HYPERHISTORY_obj[kk-len(self.save_data)])

                for ik in range(len(self.response_fun) - 1):
                    self.mydata[self.Krun +
                                kk].append(self.cross_CV_GX[kk-len(self.save_data), ik])
                    self.mydata[self.Krun +
                                kk].append(self.HYPERHISTORY_con[kk-len(self.save_data)][ik])

    def inner_loop(self, kmax, ResultList=[]):
        '''

        Main optimization loop. Desribed in detail in the Master Thesis.

        Parameters
        ----------
        kmax : int
            maximal number of yet calculatable new designs .
        ResultList : list, optional
            List containing the results from the first loop. 
            Only necessary if this loop is called as a fine tuning loop.
            For the first optimization loop now results are given. 
            Hence the default is [].
        '''

        self.HYPERHISTORY_obj = []
        self.HYPERHISTORY_con = []
        self.numberofdimensions = len(self.names)
        self.newdesignlist = copy.deepcopy(self.begindesign)
        # %% C %% I would suggest to make a copy of the cheap design as well
        # >> self.newdesignlist_c = copy.deepcopy(self.begindesign_c)
        # %% C %%
        self.krun = copy.deepcopy(self.Krun)
        self.CompareList = []
        self.CROSSvaluelist = []
        self.cross_CV_GX = []
        self.process_list = [[None] for i in range(self.krun)]

        if self.settings['DOE']['ExistingDOE']['loadDOE']:
            loadDOE = pickle.load(
                open(os.path.join(self.dictn, self.DOE_pickle),
                    'rb'))
            self.CompareList, self.ifconstraintsarefulfilled = loadDOE[
                'CompareList'], loadDOE['ifconstraintsarefulfilled']
            self.ResultList, self.ifterminationworkedwell = loadDOE[
                'ResultList'], loadDOE['ifterminationworkedwell'],

        else:
            # prepare files 
            self.prepare_newfiles(self.krun, 0, self.newdesignlist)
            # exectue high fidelity simulations 
            self.parallel.set_parallel_jobs(
                self.process_list, self.parallel_jobs)
            
            # %% C %% here we should prepare new files for the cheap simulations as well
            # >> self.prepare_newfiles_c(self.krun, 0, self.newdesignlist) # prepare cheap
            
            # the self process list for low fidelity modesl has to be returned as well
            # exectue low fidelity simulations (LS-DYNA)
            # >> self.parallel.set_parallel_jobs(self.process_list, self.parallel_jobs)
            # %% C %%
          
            os.chdir(self.PATH)

            for i in range(0, self.krun):
                self.check_DOE_file(i)
            # %% C %% also here we should read our simulations results for the low-fidelity model as in the two lines above
            # >> for i in range(0, self.krun): #
            # >>     self.check_DOE_file(i)
            # %% C %%
            
        self.save_in_pickle()

        self.Fulfil = False

        self.Converged = False

        while self.Fulfil is not True and self.Converged is not True and self.krun < kmax:
            _new_design.new_design(self)

            # print( r"If you want to pause the algorithm, please enter 'STOP'.")
            # read_in, read_out, read_exit = select.select( [sys.stdin], [], [],10)
            
            # if (i):
            #    if sys.stdin.readline().strip()=="STOP":
            #        sys.exit()

        self.build_table()

        if self.mimax == 'MIN':
            index = self.CompareList.index(min(self.CompareList))
        else:
            index = self.CompareList.index(max(self.CompareList))

        self.disbyindex = list(
            map(lambda v: [v], self.newdesignlist[index][-self.ndbi:]))

    def check_DOE_file(self, number_of_design):
        '''

        Checks for the results of a solver simulation in the belonging file.
        Adds these result to the belonging lists etc.

        Parameters
        ----------
        number_of_design : int
            indicating which file/design is considered.


        '''
        self.define_path(number_of_design)

        flag = []
        respones_dict = {}

        for responsename in self.response_fun:
            with open(self.dictn + '/' + self.path1 + '/' + self.response_fun[responsename]['Output_File'], 'r') as file:
                response_dict = _write_and_read.read_responses(
                    self, responsename, respones_dict, flag, file)

            if responsename == self.mini:
                self.CompareList.append(response_dict[responsename])

        self.ResultList.append(response_dict)

        _write_and_read.checking_constraints(self, response_dict)

        os.chdir(self.PATH)

    def save_in_pickle(self):
        '''

        Saves the DOE in a pickle file.

        '''
        if self.settings['DOE']['ExistingDOE']['loadDOE']:
            pass

        else:
            responseData = np.zeros(
                (len(
                    self.ResultList), len(
                    self.response_fun)))
            for ii in range(len(self.ResultList)):
                jj = 0
                for response in self.response_fun:
                    responseData[ii][jj] = self.ResultList[ii][response]
                    jj += 1

            pickle.dump({'DOE': self.storebegindesign,
                         'responseData': responseData,
                         'ifconstraintsarefulfilled': self.ifconstraintsarefulfilled,
                         'ifterminationworkedwell': self.ifterminationworkedwell,
                         'CompareList': self.CompareList,
                         'ResultList': self.ResultList,
                         'inParDict': self.input_param,
                         'resNam': self.response_fun},
                        open(os.path.join(self.dictn, self.DOE_pickle),
                             "wb"))
            _cs_log_class.out_print(
                self, 'DOE response values saved succesfully')

    def remove_old_files(self):
        '''

        Removes files from the last optimization that might be disturbing.

        '''

        for design_type in self.settings['Designs']:
            self.KindofDesignsname = self.settings['Designs'][design_type]['Name']
            for i in range(0, 999):
                self.define_path(i)
                if os.path.exists(self.path1):
                    shutil.rmtree(os.path.join(self.path1))

            pathres = self.settings['Designs'][design_type]['Final_Design']

            if os.path.exists(pathres):
                shutil.rmtree(os.path.join(pathres))

        for filename in os.listdir(os.getcwd()):
            if filename.startswith("Plot of "):
                os.remove(filename)

    def design(self):
        '''

        Main function calling the different loops and preparing the post processing.

        '''

        self.fix_indices = [0]
        self.remove_old_files()

        self.begindesign = []
        self.ResultList = []
        self.ifconstraintsarefulfilled = []
        self.ifterminationworkedwell = []
        
        self.save_data = []

        self.response_dict = {}

        _pre_process.prepare(self)

        self.Optimizer = 'Gradient'

        # Only relevant if mixed integer problem:
        if self.disbyindex != []:

            self.call_discrete_loop()

            if self.disbyval != [] or self.spaceconjum != [] and self.fine_Tuning_Loop:

                self.call_continuous_loop()

        else:
            self.call_continuous_loop()

        os.chdir(self.dictn)

    def call_continuous_loop(self):
        '''

        Continuous Loop preperation. Always using the Gradient based approach.

        '''
        
        self.Optimization = 'Continuous'

        self.kind_of_design = self.settings['Designs']['Cont_Design']

        _cs_log_class.out_print(self, 'Continuous Loop is called. \n')

        self.loop()

    def call_discrete_loop(self):
        '''

        Discrete Loop preperation and set up for potential fine tuning.

        '''

        self.Optimization = 'Discrete'

        self.kind_of_design = self.settings['Designs']['Dis_Design']

        _cs_log_class.out_print(self, 'Discrete Loop is called. \n')

        self.loop()

        self.fix_indices = (np.array(self.newdesignlist)[:, -self.ndbi:] == list(chain(*self.disbyindex))).all(axis=1)

        self.Krun = self.Krun + sum(self.fix_indices)

        self.begindesign = np.array(self.newdesignlist[self.fix_indices])
        self.ResultList = list(np.array(self.ResultList)[self.fix_indices])

        self.ifconstraintsarefulfilled = list(
            np.array(self.ifconstraintsarefulfilled)[self.fix_indices])
        self.ifterminationworkedwell = list(
            np.array(self.ifterminationworkedwell)[self.fix_indices])
        
        self.save_data = self.mydata

    def loop(self):
        '''

        Loop function for both discrete and continuous optimization.

        '''

        start = time.perf_counter()

        if self.settings['DOE']['ExistingDOE']['loadDOE']:
            self.begindesign = list(self.begindesign) + \
                list(_DOE_class.checkSavedDOE(self))

        else:
            self.begindesign = list(self.begindesign) + list(_sorting_and_scaling.Var(self, int(self.kind_of_design['Starting_Number'])))
            # %% C %% low fidelity DOE
            # >> self.begindesign_c = list(_sorting_and_scaling.Var(self, int(30))) # the number of samples of the low fidelity DOE should be defined upfront
            # %% C %%
            
            
            self.storebegindesign = self.begindesign.copy()
            pickle.dump({'DOE': self.begindesign,
                         'inParDict': self.input_param,
                         'resNam': self.response_fun},
                        open(os.path.join(self.dictn,self.DOE_pickle),
                             "wb"))
            _cs_log_class.out_print(
                self, 'DOE input variables saved successfully')

        self.KindofDesignsname = self.kind_of_design['Name']

        self.Krun = self.kind_of_design['Starting_Number']

        self.inner_loop(self.kind_of_design['Maximum_Number'], self.ResultList)

        total_time = str(round(time.perf_counter() - start, 5))

        self.post_proc.storePlotResults(total_time)

        _cs_log_class.out_print(self,'Total Optimization time: ' + total_time + ' s')

        plt.show()
