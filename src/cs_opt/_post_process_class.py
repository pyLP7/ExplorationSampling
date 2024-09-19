from tabulate import tabulate
import os
import shutil
import pickle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class postProcessing():

    def __init__(self, selfVar=None):
        '''


        Parameters
        ----------
        selfVar : object, optional
            Design class object used as a parent. The default is None.


        '''
        self.selfVar = selfVar

    def storePlotResults(self, total_time):
        '''

        Main function making all the supervision and documentation files.

        Parameters
        ----------
        total_time : float
            Total calculation time in seconds.

        '''

        self.total_time = total_time

        self.get_sorted()

        self.MetaModellTable = tabulate(
            self.selfVar.mydata,
            headers=self.selfVar.headers,
            tablefmt="grid")

        self.get_path()

        self.make_folder()

        self.make_file()

        self.designs = list(range(1, self.selfVar.krun + 1))

        self.make_result()

        if self.selfVar.Optimization == 'Discrete':
            self.make_marker(0)
        elif self.selfVar.Optimization == 'Continuous':
            self.make_marker(sum(self.selfVar.fix_indices))

        self.convergence_plot()

        self.make_excel()

        pickle.dump({'designs': self.designs,
                     'results': self.results,
                     'markersOff': self.markersOff,
                     'mydata': self.selfVar.mydata},
                    open("optimization_data.p",
                         "wb"))

        print(self.selfVar.TABLE)
        os.chdir(self.at)

    def get_sorted(self):
        '''

        Get the best index of the calculation. If the constraints are never fulfilled, 
        the best point not fulfilling the constraints is taken.

        '''

        CompareList = self.selfVar.CompareList
        ifconstraintsarefulfilled = self.selfVar.ifconstraintsarefulfilled[-len(
            CompareList):]

        if self.selfVar.mimax == 'MIN':
            if np.array(ifconstraintsarefulfilled).any():
                self.best_index = CompareList.index(
                    min(np.array(CompareList)[ifconstraintsarefulfilled]))
            else:
                self.best_index = CompareList.index(min(CompareList))
        else:
            if np.array(ifconstraintsarefulfilled).any():
                self.best_index = CompareList.index(
                    max(np.array(CompareList)[ifconstraintsarefulfilled]))
            else:
                self.best_index = CompareList.index(max(CompareList))

    def make_folder(self):
        '''

        The final folder is made. Here simple the folder containing the best 
        result is copied.

        '''

        if self.selfVar.settings['DOE']['ExistingDOE']['loadDOE']:
            pass
        else:
            srcr_files = os.listdir(self.srcr)
            for file_name in srcr_files:
                if file_name != '__pycache__' and 'Master' not in str(
                        file_name):
                    full_file_name = os.path.join(self.srcr, file_name)
                    shutil.copy(full_file_name,
                        os.path.join(full_file_name,self.pathres))

    def get_path(self):
        '''

        The path of the final folder is defined. 
        For that purpose simply the path of the best folder is copied.


        '''

        self.pathres = os.path.join(self.selfVar.dictn, self.selfVar.kind_of_design['Final_Design'])
        if os.path.exists(self.pathres):
            shutil.rmtree(os.path.join(self.pathres))
        os.makedirs(os.path.join(self.pathres))
        self.at = os.getcwd()
        os.chdir(self.pathres)

        if self.best_index < 9:
            pathbest = '/' + \
                self.selfVar.kind_of_design['Name'] + '000' + str(self.best_index + 1)
        elif self.best_index < 99:
            pathbest = '/' + \
                self.selfVar.kind_of_design['Name'] + '00' + str(self.best_index + 1)
        else:
            pathbest = '/' + \
                self.selfVar.kind_of_design['Name'] + '0' + str(self.best_index + 1)

        self.srcr = self.selfVar.dictn + pathbest

    def make_file(self):
        '''

        The main documentation file is written. 
        In this file the documentation table is given as well as the best result
        and the total runtime.

        '''

        file = open(
            self.pathres +
            '\\' +
            self.selfVar.kind_of_design['EndFile'],
            'a')
        file.write(self.selfVar.mini + "=" +
                   str(self.selfVar.CompareList[self.best_index]) + "\n")
        file.write('Best Design was number ' + str(self.best_index + 1) + "\n")

        file.write(self.MetaModellTable)
        file.write("\n")
        file.write("\n")
        file.write('Total Optimization time: ' + self.total_time + ' s')
        file.write("\n")
        file.write("Convergence error: " + str(self.selfVar.failvalue))
        file.close()

    def make_result(self):
        '''

        The results of all responsenames are read in a list.

        '''
        self.results = []
        z = len(self.selfVar.ResultList) - len(self.selfVar.CompareList)
        for response in self.selfVar.response_fun:
            if response == self.selfVar.mini:
                for i in range(self.selfVar.krun):
                    self.results.append(
                        self.selfVar.ResultList[i + z][response])

    def make_marker(self, begin_index):
        '''

        Marking the valid points green and the invalid points red.

        Parameters
        ----------
        begin_index : int
            size of the pre loop. Necessary for the fine tuning in order to know what part of the DOE is calculated here.
            
        '''

        self.markersOn = []
        self.markersOff = []
        for i in range(
                len(self.selfVar.ifconstraintsarefulfilled) - begin_index):
            if self.selfVar.ifconstraintsarefulfilled[i + begin_index]:
                self.markersOn.append(i)
            else:
                self.markersOff.append(i)

    def make_excel(self):
        '''

        Writing the report excel file.


        '''

        self.dff = pd.DataFrame(
            self.selfVar.mydata,
            columns=self.selfVar.headers)

        df_table = self.dff.style. apply(
            self.highlight_constrFull, subset=[
                self.selfVar.headers[1]]). apply(
            self.highlight_optimum, column=[
                self.selfVar.mini], axis=1)

        df_table.to_excel("FileofResults.xlsx")

    def convergence_plot(self):
        '''

        Plots the convergence plot.

        '''

        plt.figure()
        plt.plot(self.designs, self.results, '-gD', markevery=self.markersOn)
        plt.plot(self.designs, self.results, 'rD', markevery=self.markersOff)
        plt.plot(self.designs[self.best_index],
                 self.results[self.best_index],
                 'D',
                 color=(1,
                        1,
                        0.2),
                 markersize=5)
        plt.axvline(
            x=self.selfVar.kind_of_design['Starting_Number'],
            c='orange',
            zorder=0)
        plt.fill_between(
            self.designs,
            0,
            self.results,
            ls='--',
            hatch='/',
            facecolor='none',
            edgecolor='orange',
            where=[
                ii <= self.selfVar.kind_of_design['Starting_Number'] for ii in self.designs])

        plt.xlabel('Design')
        plt.ylabel(self.selfVar.mini)
        plt.grid()
        plt.savefig(
            fname=self.selfVar.kind_of_design['EndPlot'],
            bbox_inches="tight",
            dpi=500)

    def highlight_constrFull(self, s):
        '''
        Highlights constraints fullfillment.
        '''
        is_max = s
        return [
            'background-color: #00ff95' if v else 'background-color: #e06767' for v in is_max]

    def highlight_optimum(self, values, column):
        '''
        Highlights the optimum in a Series yellow.
        '''
        is_max = pd.Series(data=False, index=values.index)
        is_max[column] = values.loc[column] == self.dff[column].iloc[self.best_index]
        return ['background-color: yellow' if is_max.any()
                else '' for v in is_max]
