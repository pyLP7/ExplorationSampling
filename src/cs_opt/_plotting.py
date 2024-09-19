import numpy as np
from itertools import compress
import pickle, os
import matplotlib.pyplot as plt
from scipy import polyval, polyfit
from cs_opt import _sorting_and_scaling


def plot_model(self, model, name_of_model, response, output):
    '''

    Plots a meta model for given responses and shows all used DOE points.

    Parameters
    ----------
    model : object
        meta model for which the predicition should be plotted.
    name_of_model : str
        name of the meta model for which the predicition should be plotted.
    response : list
        responses of the simulated points.
    output : str
        name of the response.

    '''
    # initialize few variables
    res = self.settings['metamodels_plot']['resolution']
    contour = self.settings['metamodels_plot']['countour_plot']
    axis_labels = np.array([self.settings['metamodels_plot']['X1-Axis'],
                            self.settings['metamodels_plot']['X2-Axis'],])
    
    # get scaled DOE
    encoded_X = _sorting_and_scaling.encode(self, self.used_designs)
    
    # 1-d plot
    if self.nscj == 1:
        
        if output in self.constraint_fun:
            color = 'red'
        else:
            color='green'
        
        x = np.linspace(0, 1, res*10).reshape(-1,1)
        mu, sigma = model.predict(x, return_std=True)
        x = x.ravel()
        
        # rescale y vlaues back
        if self.scale_response:
            mu = mu * self.response_dict[output]['std'] + self.response_dict[output]['mean']
            # sigma = sigma * self.response_dict[output]['std'] + self.response_dict[output]['mean']
        
        fig, ax = plt.subplots()
        ax.plot(x, mu, c=color)
        ax.fill_between(x, mu + 1.96*sigma, mu - 1.96*sigma, alpha=0.15, label=r"95% confidence interval", color='C1')
        ax.fill_between(x, mu + 1.5*sigma, mu - 1.5*sigma, alpha=0.15,  color='C1')
        ax.fill_between(x, mu + 1.0*sigma, mu - 1.0*sigma, alpha=0.15,  color='C1')
        ax.fill_between(x, mu + 0.5*sigma, mu - 0.5*sigma, alpha=0.15,  color='C1')
        
        # scatter plot for DOE samples
        for ii, value in enumerate(response):
            ax.scatter(encoded_X[ii],
                       value*self.response_dict[output]['std'] + self.response_dict[output]['mean'],
                       c='k',
                       zorder=10)
        
        ax.set(xlabel=axis_labels[0], ylabel=output, title='Metamodel: ' + name_of_model)
        ax.grid()
        
    # n-d plot
    else:
        # initialize pos_var
        pos_var, jj = np.zeros(2), 0
        # based on the features we want to plot
        for ii in self.cont_vars:
            if ii in axis_labels:
                pos_var[np.where(ii==axis_labels)[0][0]]=jj
            jj+=1
        
        # plt.close('all')
        fig = plt.figure()
        if contour: ax = fig.add_subplot(1, 1, 1, )
        else: ax = plt.axes(projection='3d')
    
        x = np.linspace(0, 1, res)
        y = np.linspace(0, 1, res)
    
        X, Y = np.meshgrid(x, y)
        # %% beta version of n-dimensional plot (all not visible variables constant = 0.5)
        new_index = [int(pos_var[0]),int(pos_var[1])]
        
        # evaluate just on the input features you wanred to plot
        inputPlot = np.array([(np.zeros((res,res))+0.5).ravel() for ii in range(self.nscj)])
        inputPlot[new_index]= X.ravel(), Y.ravel()
        
        # predict over the two selected input variables
        Z = model.predict(inputPlot.T).reshape(X.shape) 
        # %%
        
        # Z = model.predict((np.array([X.ravel(), Y.ravel()])).T).reshape(X.shape) # $$$
        if self.scale_response:
            Z = Z * self.response_dict[output]['std'] + \
                self.response_dict[output]['mean']
    
        # ax = plt.axes(projection='3d')
        ax.set_xlabel(axis_labels[new_index[0]])
        ax.set_ylabel(axis_labels[new_index[1]])
        if not contour: ax.set_zlabel(output)
        
        # switch color if constraint function 
        if output in self.constraint_fun:
            cmap = 'autumn_r'
        else:
            cmap='viridis'
        
        if contour:
            cf = ax.contourf(X, Y, Z, res, cmap=cmap)
            cr = ax.contour(cf, levels=np.linspace(Z.min(),Z.max(),20), colors='k', 
                            linewidths=0.5, linestyles='solid', alpha =0.5)
            fig.colorbar(cf)
            for ii, value in enumerate(response):
                ax.scatter(encoded_X[ii][new_index[0]],
                           encoded_X[ii][new_index[1]],
                           c='k')
        else:
            ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                        cmap=cmap, edgecolor='none', alpha=0.8)
    
            for ii, value in enumerate(response):
                ax.scatter(encoded_X[ii][new_index[0]],
                           encoded_X[ii][new_index[1]],
                           value*self.response_dict[output]['std'] + self.response_dict[output]['mean'],
                           c='k')
    
        ax.set_title('Metamodel: ' + name_of_model)# +

    plt.show()  
    # store metamodels in the plot attribute
    filename = 'metamodel_'+name_of_model+'_'+ \
                output+'_in_Design_'+str(self.krun+1)+'.svg'
    self.plot[output] = [ax, filename]


def plot_prediction_quality(file_name, start_DOE_size, pre_loop_size):
    '''

    Plots a linear interpolation of the last calculated points in order 
    to describe the current convergence direction.

    Parameters
    ----------
    file_name : str
        name of the storage file.
    start_DOE_size : int
        size of the Start-DOE. Necessary in order to know what part of the DOE is calculated by the optimization part.
    pre_loop_size : int
        size of the pre loop. Necessary for the fine tuning in order to know what part of the DOE is calculated by the optimization part.


    '''

    loadDOE = pickle.load(open(file_name, 'rb'))
    y = loadDOE['CompareList']

    y_valid = [a and b for a,
               b in zip(loadDOE['ifconstraintsarefulfilled'],
                        loadDOE['ifterminationworkedwell'])][pre_loop_size:]
    x = list(range(1, len(y) + 1))
    if sum(y_valid) > 0:
        best_value = np.min(np.array(list(compress(y, y_valid))))
    else:
        best_value = np.min(np.array(y))
    best_index = y.index(best_value)

    markersOn = []
    markersOff = []
    for i in range(len(y_valid)):
        if y_valid[i]:
            markersOn.append(i)
        else:
            markersOff.append(i)

    plt.figure()
    plt.plot(x, y, '-gD', markevery=markersOn)
    plt.plot(x, y, 'rD', markevery=markersOff)
    plt.plot(best_index + 1, best_value, 'D', color=(1, 1, 0.2), markersize=5)

    # Interpolation
    x_inter = [len(y) + 1]
    length = 2
    a, b = polyfit(x[-length:], y[-length:], 1)
    y_inter = polyval([a, b], x_inter)
    plt.plot([x[-1]] + x_inter, [y[-1]] + list(y_inter), '--b')
    plt.axvline(x=start_DOE_size, c='orange', zorder=0)
    plt.ylim(0)
    #plt.fill_between(x,0, y, ls='--', hatch ='/', facecolor='none',edgecolor='orange', where=[ii<=start_DOE_size for ii in x])

    plt.xlabel('Design')
    plt.ylabel('Objective')
    plt.grid()
    plt.savefig(fname='Convergence_check_plot_no' + str(len(x) + \
                1 - start_DOE_size), bbox_inches="tight", dpi=500)
