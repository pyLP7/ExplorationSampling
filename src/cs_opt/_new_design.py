from cs_opt import _sorting_and_scaling, _write_and_read, _make_meta_model, _step_pickle_save
from cs_opt import  _optimization_algorithms_gradient, _plotting, _cs_log_class
import numpy as np
import copy
import os
import random


def new_design(self):
    '''

    Calculation of a new point and the belonging simulation responses.
    Termination and Constraint checks.
    
    First the new point is calculated by several subroutines. 
    Then the belonging folder is made and in the end the responses are 
    calculated and added to this folder. Several checks are made and 
    documentation is written.

    '''

    self.failvalue = np.Inf

    if self.Optimization == 'Discrete':
        self.used_designs = np.array(self.newdesignlist)
        new_optimal_point(self)

    else:
        if self.ndbi != 0:
            self.used_designs = np.array(self.newdesignlist)[:, :-self.ndbi]
            new_optimal_point(self)
            self.newpoint = list(self.newpoint) + \
                list(self.newdesignlist[0][-self.ndbi:])
        else:
            self.used_designs = np.array(self.newdesignlist)
            # %% C %% simply convert your cheap DOE from list to array 
            # >> self.used_designs_c = np.array(self.newdesignlist_c)
            # %% C %%
            new_optimal_point(self)
            self.newpoint = list(self.newpoint)

    if self.use_Localsearch:
        if self.newpoint in np.array(self.newdesignlist):
            Local_Update(self, None)

    self.process_list = [[]]

    self.prepare_newfiles(
        number_of_folder=1,
        start_number=self.krun,
        point_list=[self.newpoint])
    
    # %% C %% prepare the files for the newpoint_c (new cheap simulation)
    # >> self.prepare_newfiles(number_of_folder=1,start_number=self.krun,point_list=[self.newpoint_c])
    # %% C %%
    
    # save the metamodels as PDF in the design folder 
    if self.settings['metamodels_plot']['active']:
        for jj in self.plot.keys():
            self.plot[jj][0].get_figure().savefig(os.path.join(self.dictn, self.path1, self.plot[jj][1]))

    self.parallel.set_parallel_jobs(self.process_list, self.parallel_jobs, 1)
    # %% C %% run the simulation of the new cheap model 
    # >> self.parallel.set_parallel_jobs(self.process_list, self.parallel_jobs, 1)
    # %% C %%

    os.chdir(self.PATH)

    self.define_path(self.krun)

    response_dict = make_response_dict(self)

    self.ResultList.append(response_dict)

    _write_and_read.checking_constraints(self, response_dict)

    os.chdir(self.PATH)

    self.Converged = False

    convergence_check(self)

    self.newdesignlist = list(self.newdesignlist)
    self.newdesignlist.append(self.newpoint)
    self.newdesignlist = np.array(self.newdesignlist)

    self.Terminated = False

    self.krun = self.krun + 1

    if self.plot_convergence_checks:
        _plotting.plot_prediction_quality(
            os.path.join(self.dictn, self.backup_pickle), 
            self.kind_of_design['Starting_Number'], sum(self.fix_indices))

    if self.show_every_step_pickle:
        _step_pickle_save.save_tmp(
            os.path.join(self.dictn, self.backup_pickle),
            self.kind_of_design['Starting_Number'],
            wd=self.dictn)


def convergence_check(self):
    '''

    Check if convergence criterion is fulfilled. 
    Here the last three points have to be close to each other.

    '''
    if self.use_Localsearch:
        # if Local Search should be used
        Local_Search(self)

    else:
        if self.Terminated and self.Fulfilled:
            self.modification_value = 0.5 * self.modification_value
            # constraints can be relaxed

            self.failvalue = ((abs(float(self.CompareList[-1]) - float(self.CompareList[-2])) +
                               abs(float(self.CompareList[-1]) - float(self.CompareList[-3])))) / 2
            if self.failvalue <= self.epsilon * \
                    (abs(float(self.CompareList[-1]))):
                self.Converged = True
        else:
            self.modification_value = 2 * self.modification_value
            # constraint are not fulfilled, hence the have to be increased


def Local_Search(self):
    '''

    Definition of a Local Search. Details given in a extra PDF. 


    '''

    if self.LocalSearch:
        # between x_1 and x_2
        if self.Terminated and self.Fulfilled:
            self.modification_value = 0.5 * self.modification_value
            # constraints can be relaxed

            self.failvalue = abs(
                float(self.CompareList[-1]) - float(self.CompareList[-2]))
            if self.failvalue <= self.epsilon * \
                    (abs(float(self.CompareList[-1]))):
                self.LocalSearch = False
                # now we are between x_2 and x_3
                Local_Update(self, -2)
                # Local Update with all points without x_1 and x_2
        else:
            self.modification_value = 2 * self.modification_value
            # constraint are not fulfilled, hence the have to be increased
    else:
        # between x_2 and x_3
        if self.Terminated and self.Fulfilled:
            self.modification_value = 0.5 * self.modification_value
            # constraints can be relaxed
            if self.convexstep < 0.25:
                self.convexstep = 2 * self.convexstep
            # the convex update worked, so the next should be greater

            self.LocalSearch = True

            self.failvalue = abs(
                float(self.CompareList[-1]) - float(self.CompareList[-3]))
            if self.failvalue <= self.epsilon * \
                    (abs(float(self.CompareList[-1]))):
                self.Converged = True
        else:
            self.convexstep = 0.5 * self.convexstep
            # the convex update did not work, so the next should be smaller
            self.modification_value = 2 * self.modification_value
            # constraint are not fulfilled, hence the have to be increased


def Local_Update(self, end_of_comparision):
    '''

    Local convex update as described in the appending PDF:

    Parameters
    ----------
    end_of_comparision : int
        last index for the optional points for the convex combination


    '''

    if self.mimax == 'MIN':
        second_best_index = np.argsort(
            self.CompareList[:end_of_comparision])[0]
    else:
        second_best_index = np.argsort(
            self.CompareList[:end_of_comparision])[-1]
    
    _cs_log_class.out_print(self, '### Local Search called')

    combination_point = self.newdesignlist[second_best_index]
    # almost up to date best point
    self.newpoint = self.convexstep * \
        np.array(self.newpoint) + (1 - self.convexstep) * combination_point
    # convex combination
    self.newpoint = _sorting_and_scaling.Var(self, x=self.newpoint)
    # refit


def make_response_dict(self):
    '''

    After the solver was called the results are read into the response dictionary.
    The belonging subroutine is defined in writing and reading.

    '''

    flag = []
    response_dict = {}
    for responsename in self.response_fun:
        if not any(np.array_equal(self.newpoint, self.newdesignlist[j]) for j in range(
                len(self.newdesignlist))):
            with open(self.dictn + '/' + self.path1 + '/' + self.response_fun[responsename]['Output_File'], 'r') as file:
                response_dict = _write_and_read.read_responses(
                    self, responsename, response_dict, flag, file)

        else:
            t = np.where(
                np.all(
                    np.array(
                        self.newpoint) == np.array(
                        self.newdesignlist),
                    axis=1))[0][0]
            response_dict[responsename] = copy.deepcopy(
                float(self.ResultList[t][responsename]))

        if responsename == self.mini:
            self.CompareList.append(response_dict[responsename])

    return response_dict


def new_optimal_point(self):
    '''

    Calculation of a new point via meta models and an optimization model.
    For that purpose meta models for the obejctive and the constraints are defined.
    Details on the subroutines ae given in the belonging function.
    If an infeasible problem arises, random points are calculated.

    '''

    CV_G = []
    HP_G = []

    if self.Optimizer == 'Gradient':
        optimization_model = _optimization_algorithms_gradient.Gradient(
            "Optimization-Model " + str(
                self.krun),
            self.max_time_Grad,
            self.Optimization,
            self.encoding,
            self.modify_constraints,
            self.modification_value,
            self.random_seed,
            self)

    else:
        raise NotImplementedError

    optimization_model.add_continuous_variables(self.spaceconjum)
    optimization_model.add_continuous_variables(self.disbyval)

    if self.Optimization == 'Discrete':
        optimization_model.add_discrete_variables(self.disbyindex)

    for output in self.response_fun:
        response = [item[output] for item in self.ResultList]
        scaled_response = response
        if self.scale_response:
            scaled_response = _sorting_and_scaling.scale_response(
                self, response, output)

        _cs_log_class.out_print(
            self,
            '### Meta-Model for ' +  output +' is made ###')
        
        # %% C %% co Kriging call
        # >> metamodel, name_of_metamodel, CV = _make_meta_model.fit_model(self, scaled_response, output)
        # %% C %%

        metamodel, name_of_metamodel, CV = _make_meta_model.fit_model(self, scaled_response, output)

        if output == self.mini:
            # objective

            optimization_model.set_objective(
                metamodel, name_of_metamodel, self.mimax)
            self.CROSSvaluelist.append(CV)
            self.HYPERHISTORY_obj.append(metamodel.kernel_)

        else:
            # constraints

            sign = self.constraint_fun[output]['sign']
            value = self.constraint_fun[output]['value']
            if self.scale_response:
                value = _sorting_and_scaling.scale_response(
                    self, response, output, value)
            optimization_model.add_constraint(
                metamodel, name_of_metamodel, sign, value)
            CV_G.append(CV)
            HP_G.append(metamodel.kernel_)

    _cs_log_class.out_print(self, '### Optimization starts ###')

    try:
        encoded_solution = optimization_model.solve()

    except BaseException:
        # If no solution is found random solution is needed.

        _cs_log_class.out_print(self, 'Problem non feasible \n')

        random.seed(self.random_seed)

        encoded_solution = list(
            (np.array(
                random.choice(
                    _sorting_and_scaling.encode(
                        self,
                        self.newdesignlist))) +
             np.array(
                random.choice(
                    _sorting_and_scaling.encode(
                        self,
                        self.newdesignlist))) +
             np.array(
                random.choice(
                    _sorting_and_scaling.encode(
                        self,
                        self.newdesignlist)))) /
            3)

        self.modification_value = 0.5 * self.modification_value

    solution = _sorting_and_scaling.decode(self, encoded_solution)

    self.newpoint = _sorting_and_scaling.Var(self, x=solution)
    # %% C %% get a random new point here as well
    # >> self.newpoint_c = select even a random point 
    # %% C %% 

    self.cross_CV_GX = np.append(np.array(self.cross_CV_GX), CV_G)
    self.HYPERHISTORY_con.append(HP_G)
