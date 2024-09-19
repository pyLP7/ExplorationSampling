from sklearn.gaussian_process import GaussianProcessRegressor as gp
from sklearn.model_selection import cross_val_score
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, DotProduct, RationalQuadratic, Matern
import numpy as np

from cs_opt import _sorting_and_scaling, _plotting


def fit_model(self, response, output):
    '''

    Defines the best meta model for a given output and belonging responses.
    For that purpose first the hyperparameters are optimized and
    then all different options are compared by cross validation.

    Parameters
    ----------
    response : array
        simulated responses of the output.
    output : str
        name of the to be predicited output.

    Returns
    -------
    metamodel : object
        the best meta model for this output.
    name_of_metamodel : str
        name of this meta model according to the User Interface.
    CV : float
        cross validation value for this model.

    '''
    CV = -np.inf

    for potential_name in self.model_options:

        model_option, potential_CV = tune_hyperparameter(
            self, potential_name, response)

        if potential_CV > CV:
            metamodel = model_option
            CV = potential_CV
            name_of_metamodel = potential_name

    if self.ndbv == 0 and self.Optimization == 'Continuous' \
    and self.settings['metamodels_plot']['active']:
        _plotting.plot_model(
            self,
            metamodel,
            name_of_metamodel,
            response,
            output)

    return metamodel, name_of_metamodel, CV


def tune_hyperparameter(self, name, response):
    '''

    Tunes the best hyperparameter for a given type of model. 
    This means for a specific model the best hyperparameters are calculated
    and with them cross validation is used to calculate a Cross Validation Score.

    Parameters
    ----------
    name : str
         name of this meta model according to the User Interface.
    response : array
        simulated responses of the output.

    Returns
    -------
    model : object
        tuned model.
    CV : float
        cross validation value for this model.

    '''

    encoded_X = _sorting_and_scaling.encode(self, self.used_designs)
    
    model = get_Gaussian_model(self, encoded_X, response, name)
    CV = cross_val_score(
        model,
        encoded_X,
        response,
        scoring=self.CV_scoring,
        cv=self.cv).mean()

    return model, CV


def get_Gaussian_model(self, encoded_X, response, name):
    '''

    Here for ech kind of gaussian meta model (indicated by its name), the best set
    of hyperparameters is calculated. For that purpose the idea of maximal
    likelihood is used. This is done by scikit learn.

    Parameters
    ----------
    encoded_X : encoded input for the calculation of a given type of meta model.
        DESCRIPTION.
    response : array
        simulated responses of the output.
    name : str
        name of this meta model according to the User Interface.

    Returns
    -------
    model : object
        the best meta model for this output.

    '''

    k1 = RBF(length_scale_bounds=[0.05, 2.0]) 
    k2 = DotProduct(sigma_0_bounds=[1e-05, 10.0])
    k3 = RationalQuadratic(
        length_scale_bounds=[
            0.05, 2.0], alpha_bounds=[
            1e-01, 1])
    k4 = Matern(length_scale_bounds=[0.05, 2.0])
    k5 = ConstantKernel(constant_value_bounds=[1e-01, 1000000.0])

    try:

        if name == 'Gauss_RBF':
            model = gp(1 * k1 + 1 * k1**2 + k5)
            model.fit(encoded_X, response)

        elif name == 'Gauss_Dot':
            model = gp(1 * k2 + 1 * k2**2 + k5)
            model.fit(encoded_X, response)

        elif name == 'Gauss_Quad':
            model = gp(1 * k3 + 1 * k3**2 + k5)
            model.fit(encoded_X, response)

        elif name == 'Gauss_Matern':
            model = gp(1 * k4 + 1 * k4**2 + k5)
            model.fit(encoded_X, response)

        elif name == 'Gauss_MaternQuad':
            model = gp(1 * k3 + 1 * k4 + k5)
            model.fit(encoded_X, response)

        elif name == 'Gauss_Sum':
            model = gp(1 * k1 + 1 * k2 + 1 * k3 + k5)
            model.fit(encoded_X, response)

    except np.linalg.LinAlgError:
        model = gp().fit(encoded_X, response)

    return model
