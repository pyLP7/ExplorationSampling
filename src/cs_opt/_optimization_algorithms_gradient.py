from scipy.optimize import differential_evolution, minimize, NonlinearConstraint
import numpy as np
from time import time
import warnings
from cs_opt import _cs_log_class


class TookTooLong(Warning):
    pass


class Gradient():

    def __init__(
            self,
            name,
            max_time,
            Optimization,
            encoding,
            modify_constraints,
            modification_value,
            random_seed,
            cs_opt):
        '''

        Further details on this part are given in the Master thesis.

        Parameters
        ----------
        name : str
            name of the optimization model.
        max_time : float
            maximal calculation time in seconds.
        Optimization : str
            deciding if mixed or continuous optimization.
        encoding : str
            defining the encoding routines.
        modify_constraints : bool
            deciding if constraint modification heuristic should be used.
        modification_value : float
            start value for the heuristic modification.
        random_seed : int
            describing the used random seeds.
        cs_opt : object
            containing all informations about the base object.

        '''
        self.name = name
        self.constraints = []
        self.bounds = []
        self.max_time = max_time
        self.Optimization = Optimization
        self.encoding = encoding
        self.modify_constraints = modify_constraints
        self.modification_value = modification_value
        self.random_seed = random_seed
        self.cs_opt = cs_opt

    def add_continuous_variables(self, variables):
        '''


        Parameters
        ----------
        variables : list
            Indicating the number of continuous variables.


        '''
        for variable in variables:
            self.bounds.append((0, 1))

    def add_discrete_variables(self, discrete_parameter):
        '''


        Parameters
        ----------
        discrete_parameter : list
            Indicating the number of discrete variables and their values.

        '''
        self.discrete_parameter = discrete_parameter
        if self.encoding == 'One-Hot':
            self.add_hot_encoded_parameter()
        elif self.encoding == 'Label':
            self.add_label_encoded_parameter()
        elif self.encoding == 'Logarithmic':
            self.add_log_encoded_parameter()

    def add_hot_encoded_parameter(self):
        for parameter in self.discrete_parameter:
            for value in parameter:
                self.bounds.append((0, 1))
                n = len(self.bounds)
                discrete_function = self.main_constraintfunction(n - 1)
                discrete_constraint = NonlinearConstraint(
                    discrete_function, 0, 0)
                self.constraints.append(discrete_constraint)

            k_end = len(self.bounds)
            encoded_function = self.encoded_constraintfunction(
                k_end - len(parameter), k_end)
            encoded_constraint = NonlinearConstraint(encoded_function, 1, 1)
            self.constraints.append(encoded_constraint)

    def add_label_encoded_parameter(self):
        for parameter in self.discrete_parameter:
            self.bounds.append((0, len(parameter) - 1))
            n = len(self.bounds)
            modulo_function = self.modulo_function(n - 1)
            discrete_constraint = NonlinearConstraint(modulo_function, 0, 0)
            self.constraints.append(discrete_constraint)

    def add_log_encoded_parameter(self):
        for parameter in self.discrete_parameter:
            size = int(np.ceil(np.log2(len(parameter))))
            for j in range(size):
                self.bounds.append((0, 1))
                n = len(self.bounds)
                discrete_function = self.main_constraintfunction(n - 1)
                discrete_constraint = NonlinearConstraint(
                    discrete_function, 0, 0)
                self.constraints.append(discrete_constraint)
                
            k_end = len(self.bounds)
            log_function = self.log_save_function(
                k_end - size, k_end)
            log_constraint = NonlinearConstraint(log_function,0, len(parameter)-1)
            self.constraints.append(log_constraint)
            

    def set_objective(self, metamodel, name_of_metamodel, sense='MIN'):
        '''

        Setting the objective for the optimization model.

        Parameters
        ----------
        metamodel : object
            the meta model for the objective.
        name_of_metamodel : str
            name of this meta model according to the User Interface.
        sense : str, optional
            Indicating if minimization or maximization is desired. The default is 'MIN'.


        '''
        self.objective = self.make_function(metamodel, sense)

    def add_constraint(self, metamodel, name_of_metamodel, sign, value):
        '''

        Adding a constraint to the optimization model.

        Parameters
        ----------
        metamodel : object
            the best meta model for this output.
        name_of_metamodel : str
            name of this meta model according to the User Interface.
        sign : str
            indicating the kind of constraint.
        value : float
            constraint value.

        '''

        constraintfunction = self.make_function(metamodel)

        if sign == 'LESS':
            if self.modify_constraints:
                nonLinCon = NonlinearConstraint(
                    constraintfunction, -np.inf, (1 - np.sign(value) * self.modification_value) * value)
            else:
                nonLinCon = NonlinearConstraint(
                    constraintfunction, -np.inf, value)
        elif sign == 'GREATER':
            if self.modify_constraints:
                nonLinCon = NonlinearConstraint(
                    constraintfunction, (1 + np.sign(value) * self.modification_value) * value, +np.inf)
            else:
                nonLinCon = NonlinearConstraint(
                    constraintfunction, value, +np.inf)
        elif sign == 'EQUAL':
            nonLinCon = NonlinearConstraint(constraintfunction, value, value)

        self.constraints.append(nonLinCon)

    def make_function(self, metamodel, sense='MIN'):
        '''

        Modifying a function such that is it readable by scipy.

        Parameters
        ----------
        metamodel : object
            the meta model for the objective.
        sense : str, optional
            Indicating if minimization or maximization is desired. The default is 'MIN'.


        '''

        if sense == 'MIN':
            def function(X):
                return metamodel.predict(np.array([X])).ravel()
        elif sense == 'Maximize':
            def function(X):
                return - metamodel.predict(np.array([X])).ravel()

        return function

    def main_constraintfunction(self, n):
        '''
        Binary constraint function
        '''
        def one_or_zero(X):
            return X[n] * (X[n] - 1)
        return one_or_zero

    def encoded_constraintfunction(self, k_start, k_end):
        '''
        One Hot constraint function
        '''
        def sum_is_one(X):
            return sum(X[k_start:k_end])
        return sum_is_one

    def modulo_function(self, n):
        '''
        Integer constraint function
        '''
        def modulo(X):
            return X[n] % 1
        return modulo
    
    def log_save_function(self,k_start, k_end):
        '''
        Logarithmic constraint function
        '''
        def log_sum(X):
            return sum(X[k_start+i]*2**i for i in range(k_end-k_start))
        return log_sum

    def bring_back_to_encoded(self, answer):
        '''

        Because of numerical mistakes after GRAD optimization a refinement/readjustment is necessary.

        Parameters
        ----------
        answer : array
            unfitted answer.

        Returns
        -------
        answer : array
            fitted answer.

        '''
        k = len(answer)

        for parameter in self.discrete_parameter:
            if self.encoding == 'One-Hot':
                k_start = k - len(parameter)
                encoded_list = [0 for j in parameter]
                encoded_list[int(
                    np.argmin(abs(np.array(answer[k_start:k]) - 1)))] = 1
            elif self.encoding == 'Logarithmic':
                k_start = k - int(np.ceil(np.log2(len(parameter))))
                encoded_list = [0 for j in range(
                    int(np.ceil(np.log2(len(parameter)))))]
                for l in np.where(np.array(answer[k_start:k]) - 0.5 > 0)[0]:
                    encoded_list[l] = 1
            elif self.encoding == 'Label':
                k_start = k - 1
                encoded_list = int(answer[k_start:k])

            answer[k_start:k] = encoded_list
            k = k_start

        for i in range(k):
            if answer[i] < 0:
                answer[i] = 0
            elif answer[i] > 1:
                answer[i] = 1

        return answer

    def solve(self):
        '''

        Stepwise gradient based optimization as descirbed in Scipy

        Returns
        -------
        answer: list
            optimization solution.

        '''
        self.start_time = time()
        np.random.seed(self.random_seed)

        start_point = differential_evolution(
            self.objective, self.bounds, strategy='best1bin', constraints=(
                self.constraints), callback=self.callback, polish=False)['x']
        try:
            try:
                self.start_time = time()
                answer = minimize(
                    self.objective,
                    start_point,
                    method='trust-constr',
                    bounds=self.bounds,
                    constraints=(
                        self.constraints),
                    callback=self.callback)['x']
            except ValueError:
                _cs_log_class.out_print(
                    self.cs_opt, 'Using COBYLA instead of trust-constr')
                self.start_time = time()
                answer = minimize(
                    self.objective,
                    start_point,
                    method='COBYLA',
                    bounds=self.bounds,
                    constraints=(
                        self.constraints),
                    callback=self.callback)['x']
        except BaseException:
            answer = start_point
            _cs_log_class.out_print(
                self.cs_opt, 'Even that did not work. Differential is used.')

        if self.Optimization == 'Discrete' and self.encoding in [
                'One-Hot', 'Logarithmic']:
            answer = self.bring_back_to_encoded(answer)

        return list(answer)

    def callback(self, xk=None, convergence=None):
        '''

        Callback function to stop after a certain amount of time.

        Returns
        -------
        bool
            indicating if the maximal time has elapsed or not.

        '''

        elapsed = time() - self.start_time
        if elapsed > self.max_time:
            warnings.warn(
                "Terminating optimization: time limit reached",
                TookTooLong)
            return True
        else:
            return False
