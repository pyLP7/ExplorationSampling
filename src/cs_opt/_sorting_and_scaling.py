import numpy as np
import math
import random
from cs_opt import _cs_log_class


def Var(self, numberofsamples=None, x=None):
    '''

    Either defines a Start DOE fitting the solver domain or 
    re-fits a given sample or DOE to the solver domain.


    Parameters
    ----------
    numberofsamples : int, optional
        number of samples that are needed. The default is None.
    x : array, optional
        point/DOE that must be fitted. The default is None, then a new DOE is build.

    Returns
    -------
    x : array
        point or Start-DOE fitting for solver .

    '''

    values, allvalues, number_of_optimated_dimensions = get_potential_values(
        self)

    if x is None:
        x = make_fitted_DOE(self, numberofsamples, values)

    else:
        x = fit_DOE(self, x, allvalues, number_of_optimated_dimensions)

    return x


def fit_DOE(self, x, allvalues, number_of_optimated_dimensions):
    '''

    Re-fits the DOE/point to the solver domain by reassigning each point to 
    its closest within the solver domain.

    Parameters
    ----------
    x : array
        point/DOE that must be fitted.
    allvalues : array
        containing all values that might be attained in  every dimension.
    number_of_optimated_dimensions : int
        number of dimensions in which the parameters shoulod be optimized. Only relevant for the fine tuning part.

    Returns
    -------
    x : array
        DOE fitting for solver .

    '''
    x = np.array(x)
    numberofsamples = len(x)
    if x.shape == (len(x),):
        for i in range(number_of_optimated_dimensions):
            x[i] = allvalues[i][int(np.argmin(abs(allvalues[i] - x[i])))]
    else:
        for i in range(number_of_optimated_dimensions):
            for j in range(numberofsamples):
                x[j][i] = allvalues[i][int(
                    np.argmin(abs(allvalues[i] - x[j][i])))]

    return x


def make_fitted_DOE(self, numberofsamples, values):
    '''

    Defines a Start-DOE fitting the solver domain. 
    First a Latin Hypercube is whcih is then transformed to cover the solver domain.

    Parameters
    ----------
    numberofsamples : int
        dedicating the size of the Start-DOE.
    values : array
        values attainable by continuous parameters.

    Returns
    -------
    x : array
        Start DOE.

    '''
    x = self.dsgn(self.numberofdimensions, numberofsamples)
    for i in range(self.nscj + self.ndbv):
        x[:, i] = x[:, i] * (max(values[i]) - min(values[i])) + min(values[i])
        for j in range(numberofsamples):
            x[j][i] = values[i][int(np.argmin(abs(values[i] - x[j][i])))]
    for i in range(self.ndbi):
        for j in range(numberofsamples):
            x[j][i +
                 self.nscj +
                 self.ndbv] = self.disbyindex[i][int(math.floor(x[j][i +
                                                                     self.nscj +
                                                                     self.ndbv] *
                                                                len(self.disbyindex[i]) -
                                                                0.000001))]

    return x


def get_potential_values(self):
    '''

    Gets relevant parameters for the fitting of DOEs:
        All continous values (not really continuous becuase of the jumpsize)
        number of optimated dimensions depending on if the discrete parameters are variable or fixed.

    Returns
    -------
    values : array
        values attainable by continuous parameters.
    allvalues : array
        containing all values that might be attained in  every dimension.
    number_of_optimated_dimensions : int
        number of dimensions in which the parameters shoulod be optimized. 
        Only relevant for the fine tuning part.


    '''
    con_values = []
    for i in range(self.nscj):
        potential_values = list(np.round(np.arange(self.spaceconjum[i][0],
                                                   self.spaceconjum[i][1],
                                                   self.jumsiz[i]), 7))
        con_values.append(potential_values)

    values = con_values + self.disbyval
    if self.Optimization == 'Discrete':
        allvalues = values + self.disbyindex
        number_of_optimated_dimensions = self.numberofdimensions
    else:
        allvalues = values
        number_of_optimated_dimensions = self.numberofdimensions - self.ndbi

    return values, allvalues, number_of_optimated_dimensions


def encode(self, X):
    '''

    Translates from the solver to the modeling domain. 
    Details are given in the MAster Thesis.

    Parameters
    ----------
    X : array
        solver domain X.

    Returns
    -------
    X : array
        modeling domain X.

    '''
    X_new = []
    for sample in X:
        sample_new = []

        if self.nscj != 0:
            sample_new = list(np.round((np.array(sample[:self.nscj]) - np.amin(
                self.spaceconjum, axis=1)) / np.ptp(self.spaceconjum, axis=1), 5))

        if self.ndbv != 0:
            sample_new = sample_new + list(np.round((np.array(sample[self.nscj:self.nscj + self.ndbv]) - np.min(
                self.disbyval, axis=1)) / np.ptp(self.disbyval, axis=1), 5))

        if self.Optimization == 'Discrete':
            if self.encoding == 'One-Hot':
                sample_new = one_hot_encode(self, sample, sample_new)
            elif self.encoding == 'Label':
                sample_new = label_encode(self, sample, sample_new)
            elif self.encoding == 'Logarithmic':
                sample_new = log_encode(self, sample, sample_new)
        X_new.append(sample_new)

    return np.array(X_new)


def log_encode(self, sample, sample_new):
    '''


    Parameters
    ----------
    sample : array
        To be encoded point
    sample_new : array
        Partly encoded point.

    Returns
    -------
    sample_new : array
        Fully encoded point.

    '''
    for i in range(self.ndbi):
        index_of_occurance = self.disbyindex[i].index(
            sample[self.numberofdimensions - self.ndbi + i])
        log_encoded = list(map(int, np.binary_repr(
            index_of_occurance, width=int(np.ceil(np.log2(len(self.disbyindex[i])))))))
        sample_new = sample_new + log_encoded
    return sample_new


def label_encode(self, sample, sample_new):
    '''


    Parameters
    ----------
    sample : array
        To be encoded point
    sample_new : array
        Partly encoded point.

    Returns
    -------
    sample_new : array
        Fully encoded point.

    '''
    for i in range(self.ndbi):
        index_of_occurance = self.disbyindex[i].index(
            sample[self.numberofdimensions - self.ndbi + i])
        sample_new = sample_new + [index_of_occurance]
    return sample_new


def one_hot_encode(self, sample, sample_new):
    '''


    Parameters
    ----------
    sample : array
        To be encoded point
    sample_new : array
        Partly encoded point.

    Returns
    -------
    sample_new : array
        Fully encoded point.

    '''
    for i in range(self.ndbi):
        hot_encoded = [0 for j in self.disbyindex[i]]
        index_of_occurance = self.disbyindex[i].index(
            sample[self.numberofdimensions - self.ndbi + i])
        hot_encoded[index_of_occurance] = 1
        sample_new = sample_new + hot_encoded

    return sample_new


def decode(self, X):
    '''

    Translates from the modeling domain to the solver domain.
    Details are given in the MAster Thesis.

    Parameters
    ----------
    X : array
        modeling domain X.

    Returns
    -------
    X : array
        solver domain X.

    '''
    X_new = []
    if self.nscj != 0:
        X_new = list(np.array(X[:self.nscj]) *
                     np.ptp(self.spaceconjum, axis=1) +
                     np.amin(self.spaceconjum, axis=1))

    if self.ndbv != 0:
        X_new = X_new + list(np.array(X[self.nscj:self.nscj + self.ndbv]) * np.ptp(
            self.disbyval, axis=1) + np.min(self.disbyval, axis=1))

    if self.Optimization == 'Discrete':
        if self.encoding == 'One-Hot':
            X_new = one_hot_decode(self, X, X_new)
        elif self.encoding == 'Label':
            X_new = label_decode(self, X, X_new)
        elif self.encoding == 'Logarithmic':
            X_new = log_decode(self, X, X_new)

    return np.array(X_new)


def log_decode(self, X, X_new):
    '''


    Parameters
    ----------
    X : array
        To be decoded point
    X_new : array
        Partly decoded point.

    Returns
    -------
    X_new : array
        Fully decoded point.

    '''
    k = self.ndbv + self.nscj
    for i in range(self.ndbi):
        k_end = k + int(np.ceil(np.log2(len(self.disbyindex[i]))))
        try:
            index = int("".join(map(str, map(int, X[k:k_end]))), 2)
            decoded_value = self.disbyindex[i][index]
        except ValueError and IndexError:
            random.seed(self.random_seed)
            _cs_log_class.out_print(
                self, 'Random Index was choosen, since runtime was passed.')
            decoded_value = random.choice(self.disbyindex[i])
        X_new.append(decoded_value)
        k = k_end
    return X_new


def label_decode(self, X, X_new):
    '''


    Parameters
    ----------
    X : array
        To be decoded point
    X_new : array
        Partly decoded point.

    Returns
    -------
    X_new : array
        Fully decoded point.

    '''
    k = self.ndbv + self.nscj
    for i in range(self.ndbi):
        try:
            decoded_value = self.disbyindex[i][int(X[k])]
        except ValueError:
            random.seed(self.random_seed)
            _cs_log_class.out_print(
                self, 'Random Index was choosen, since runtime was passed.')
            decoded_value = random.choice(self.disbyindex[i])
        X_new.append(decoded_value)
        k = k + 1
    return X_new


def one_hot_decode(self, X, X_new):
    '''


    Parameters
    ----------
    X : array
        To be decoded point
    X_new : array
        Partly decoded point.

    Returns
    -------
    X_new : array
        Fully decoded point.

    '''
    k = self.ndbv + self.nscj
    for i in range(self.ndbi):
        k_end = k + len(self.disbyindex[i])
        try:
            decoded_value = self.disbyindex[i][X[k:k_end].index(1)]
        except ValueError:
            random.seed(self.random_seed)
            _cs_log_class.out_print(
                self, 'Random Index was choosen, since runtime was passed.')
            decoded_value = random.choice(self.disbyindex[i])
        X_new.append(decoded_value)
        k = k_end

    return X_new


def scale_response(self, response, output, value=None):
    '''

    Scaling the responses for the meta modeling part. Mean = 0, std = 1.
    Details are given in the MAster Thesis.

    Parameters
    ----------
    response : array
        unscaled response
    output : str
        name of the corresponding output.
    value : TYPE, optional
        unscaled value. Only relevant if a constraint value has to be rescaled. Hence the default is None.

    Returns
    -------
    response: array
       scaled response/value.

    '''
    response = np.array(response)
    if value is None:
        try:
            self.response_dict[output] = {}
            self.response_dict[output]['mean'] = np.mean(response[:self.Krun])
            self.response_dict[output]['std'] = np.std(response[:self.Krun])

            return (
                response - self.response_dict[output]['mean']) / self.response_dict[output]['std']
        except ZeroDivisionError:
            return response

    else:
        try:
            value = (
                value - self.response_dict[output]['mean']) / self.response_dict[output]['std']
            return value
        except ZeroDivisionError:
            return value
