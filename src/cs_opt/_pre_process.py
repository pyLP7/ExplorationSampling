import re as re_set
import os


def prepare(self):
    '''

    Generating the names and ranges of all variables.
    Reading the standard keyfile in order to check if the ref values are given correctly and save time later.

    '''
    self.spaceconjum = []
    self.jumsiz = []
    self.disbyval = []
    self.disbyindex = []
    self.names = []

    self.cont_vars = add_variable_names(self, ['CONTINUOUS', 'C'])
    self.dbv_vars = add_variable_names(self, ['ORDINALDISCRETE_VALUE', 'O_V'])
    self.dbi_vars = add_variable_names(self, ['ORDINALDISCRETE_INDEX', 'O_I'])
    
    self.names = self.cont_vars + self.dbv_vars + self.dbi_vars

    for parameter in self.input_param:
        if self.input_param[parameter]['value_type'] in [
                'CONTINUOUS', 'C']:
            self.spaceconjum.append(self.input_param[parameter]['range'])
            self.jumsiz.append(self.input_param[parameter]['jumpsize'])

        elif self.input_param[parameter]['value_type'] in ['ORDINALDISCRETE_VALUE', 'O_V']:
            self.disbyval.append(self.input_param[parameter]['range'])

        elif self.input_param[parameter]['value_type'] in ['ORDINALDISCRETE_INDEX', 'O_I']:
            self.disbyindex.append(self.input_param[parameter]['range'])

    self.nscj = len(self.spaceconjum)
    self.ndbv = len(self.disbyval)
    self.ndbi = len(self.disbyindex)
    self.numberofdimensions = self.nscj + self.ndbv + self.ndbi

    self.keyfile_dictionary = {}
     
    # iterate over the input file list
    for name in self.names:
        found_flag = False
        for ii_file in self.settings['Workspace']['Input_File']:
            with open(os.path.join(self.src, ii_file), 'r') as file:
                for line in file:                
                    if line.find(name) != -1 and name in line.split() or line.find(name) != -1 and name in line.split('='):
                        try:
                            # save the string value and the relative input file
                            self.keyfile_dictionary[name] = {}
                            self.keyfile_dictionary[name]['string'] = re_set.search(name + '(.*)' + str(self.input_param[name]['ref_value']), line).group()
                            self.keyfile_dictionary[name]['input_file'] =ii_file
                            found_flag = True
                            break # break the line loop
                            
                        except AttributeError:
                            raise(r'Wrong ref_value was used for ' +name + '. Not valid ref_value. Could not be found in the key.file.')
            if found_flag:
                break # break the file loop is the variable has been found
    file.close()


def add_variable_names(self, kind_of_variable):
    '''


    Parameters
    ----------
    kind_of_variable : list
        containing strings indicating if a continuous or a discrete variable is considered.

    '''
    var_name = []
    for parameter in self.input_param:
        if self.input_param[parameter]['value_type'] in kind_of_variable:
            var_name.append(parameter)
    return var_name
