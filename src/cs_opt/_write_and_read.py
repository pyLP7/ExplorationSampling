import os
import re as re_set
import pickle
import numpy as np


def write_key_and_solver(self, designlist, number_of_point):
    '''

    Preperation of the key-file and call of the solver. 
    In the key file  the real calculated point is written isntead of the ref values.

    Parameters
    ----------
    designlist : list
        containing the DOE.
    number_of_point : int
        index of the considered point.


    '''
    # loop on input files containing features
    variable_files = [self.keyfile_dictionary[ii]['input_file'] for ii in self.keyfile_dictionary]
    file_list = list(dict.fromkeys(variable_files))
    
    for kk_file in file_list:
        key_data = read_lines(self, file_to_read=kk_file)
    
        key_data = modify_data(self, key_data, kk_file, designlist, number_of_point)
        
        with open(os.path.join(self.dictn, self.path1, kk_file), 'w') as file:
            file.write(key_data) 
    
            save_in_resultfile(self, designlist, number_of_point)
    
            call_solver(self, number_of_point)


def modify_data(self, key_data, input_file, designlist, number_of_point):
    '''

    Modification of the key data string such that the solver indeed executes the right simulation.
     Little complicated because of the right allignment for LS DYNA.


    Parameters
    ----------
    key_data : str
        Data-string of the key-file.
    designlist : list
        containing the DOE.
    number_of_point : int
        index of the considered point.

    Returns
    -------
    key_data : str
        modified Data-string of the key-file.

    '''
    for j in range(self.numberofdimensions):
        if self.keyfile_dictionary[self.names[0]]['input_file'] != input_file:
            pass
        
        replaced_line = self.keyfile_dictionary[self.names[j]]['string'] # $$$

        if self.input_param[self.names[j]]['value_type'] in ['ORDINALDISCRETE_INDEX', 'O_I']:
            number_of_blanks = replaced_line.count(' ') + len(str(self.input_param[self.names[j]]['ref_value'])) - len(str(int(designlist[number_of_point][j])))
            key_data = re_set.sub(replaced_line, self.names[j] + number_of_blanks * ' ' + str(int(designlist[number_of_point][j])), key_data, 1)
        else:
            number_of_blanks = replaced_line.count(' ') + len(str(self.input_param[self.names[j]]['ref_value'])) - len(str(designlist[number_of_point][j]))
            key_data = re_set.sub(replaced_line, self.names[j] + number_of_blanks * ' ' + str(designlist[number_of_point][j]), key_data, 1)

    return key_data


def read_lines(self, file_to_read=None):
    '''

    Reads all lines of the key file as one data string.

    Returns
    -------
    key_data : str
        Data-string of the key-file.

    '''
    with open(os.path.join(self.dictn, self.path1, file_to_read), 'r') as file:
        key_data = file.read()

    return key_data


def save_in_resultfile(self, designlist, number_of_point):
    '''

    Writes the parameters of the new calculated point in a file for supervision.


    Parameters
    ----------
    designlist : list
        containing the DOE.
    number_of_point : int
        index of the considered point.


    '''
    file = open(self.kind_of_design['EndFile'], "w")
    for j in range(self.numberofdimensions):
        file.write(str(self.names[j]) + "=" +
                   str(designlist[number_of_point][j]) + "\n")
    file.close()


def call_solver(self, number_of_point):
    '''

    Solver call for the given point. 
    Either by a bat file or directly with the exectuer path.

    Parameters
    ----------
    number_of_point : int
        index of the considered point.
    '''

    if self.settings['Workspace']['Bat_File'] != '': #and self.settings['Solver']['Workspace'] is not None
        self.process_list[number_of_point] = (self.settings['Workspace']['Bat_File'], self.dictn + '/' + self.path1)
    else:
        self.process_list[number_of_point] = str(self.settings['Workspace']['Python_Executer']) + "  " + str(
            self.dictn + '/' + self.path1 + '/' + self.settings['Workspace']['Master_File']), self.dictn + '/' + self.path1
    os.chdir(self.PATH)


def read_responses(self, responsename, response_dict, flag, file):
    '''

    Reads the responses from the given file for the certain responsename
    and adds it to the response_dict.

    Parameters
    ----------
    responsename : str
        name of the considered response.
    response_dict : dict
        dict containing all responses.
    flag : list
        flags for all responses.
    file : file
        the file in which the results are stored.

    Returns
    -------
    response_dict : dict
        modified dict containing all responses.

    '''
    lines = []
    for line in file:
        lines.append(line)
    for ii in range(len(lines)):
        line = lines[ii]
        if line.find(responsename) != -1:
            index = line.find(responsename)
            new_line = line[index + len(responsename):]
            regexp = re_set.compile(r'.*?([0-9.-]+)')
            match = regexp.match(new_line)
            flag.append(new_line.find(match.group(1)))
            starting_column = index + len(responsename) + flag[-1]
            helpvar = match.group(1)
            helpvar = helpvar.strip()
            length = helpvar.count('') - 1
            if line[starting_column +
                    length] == 'e' or line[starting_column +
                                           length] == 'E':
                helpvar = helpvar + \
                    line[starting_column + length: starting_column + length + 4]
            response_dict[responsename] = float(helpvar)
            break

    return response_dict


def checking_constraints(self, response_dict):
    '''

    Checks wheater all constraints are fulfilled and the termination went well.

    Parameters
    ----------
    response_dict : dict
        dict containing all responses.


    '''

    check_termination(self)

    check_constraint(self, response_dict)

    if len(self.ifconstraintsarefulfilled) >= len(self.newdesignlist):
        self.build_table()

    save_pickle(self)


def check_termination(self):
    '''

    FE solver Termination check.

    '''

    self.Terminated = True
    if self.settings['Workspace']['Termination_Name'] != '':
        with open(self.dictn + '/' + self.path1 + '/' + self.settings['Workspace']['Termination_File'], 'r') as file:
            lines = []

            # Reading through all Lines
            for line in file:
                lines.append(line)
            for ii in range(len(lines)):
                line = lines[ii]
                if line.find(
                        self.settings['Workspace']['Termination_Name']) != -1:
                    index = line.find(
                        self.settings['Workspace']['Termination_Name'])
                    new_line = line[index +
                                    len(self.settings['Workspace']['Termination_Name']):]
                    regexp = re_set.compile(r'.*?([0-9.-]+)')
                    match = regexp.match(new_line)
                    END = match.group(1)
                    END = float(END.strip())
                    if END != 1:
                        self.Terminated = False
                    break

    self.ifterminationworkedwell.append(self.Terminated)


def check_constraint(self, response_dict):
    '''

    Checks wheater all constraints are fulfilled in the response_dict.

    Parameters
    ----------
    response_dict : dict
        dict containing all responses.


    '''

    self.Fulfilled = True

    for responsename in self.constraint_fun:
        if self.constraint_fun[responsename]['sign'] == 'LESS':
            if self.constraint_fun[responsename]['value'] < response_dict[responsename]:
                self.Fulfilled = False
        elif self.constraint_fun[responsename]['sign'] == 'GREATER':
            if self.constraint_fun[responsename]['value'] > response_dict[responsename]:
                self.Fulfilled = False
        elif self.constraint_fun[responsename]['sign'] == 'EQUAL':
            if self.constraint_fun[responsename]['value'] != response_dict[responsename]:
                self.Fulfilled = False

    self.ifconstraintsarefulfilled.append(self.Fulfilled)


def save_pickle(self):
    '''

    Supervision with a pickle. Here allmost all the data is saved efficiently.

    '''

    responseData = np.zeros((len(self.ResultList), len(self.response_fun)))

    for ii in range(len(self.ResultList)):
        jj = 0
        for response in self.response_fun:
            responseData[ii][jj] = self.ResultList[ii][response]
            jj += 1

    pickle.dump({'DOE': self.newdesignlist, 'responseData': responseData,
                 'ifconstraintsarefulfilled': self.ifconstraintsarefulfilled,
                 'ifterminationworkedwell': self.ifterminationworkedwell,
                 'CompareList': self.CompareList,
                 'ResultList': self.ResultList,
                 'inParDict': self.input_param,
                 'resNam': self.response_fun,
                 'data': self.mydata,
                 'headers': self.headers},
                open(os.path.join(self.dictn,self.backup_pickle), "wb"))
