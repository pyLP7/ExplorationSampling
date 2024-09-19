
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import test_functions as tf
from matplotlib import rc

plt.close('all')


# %% Plot surface models
def plot_1d_function(function, lower_bound, upper_bound):
    fig = plt.figure()

    
    X = np.linspace(lower_bound, upper_bound, 300).reshape(-1,1)
    Y = function(X)
    
    plt.xlabel(r'$x$')
    plt.ylabel(r'$f(x)$')
    
    plt.plot(X,Y)
    plt.grid()
    plt.show()

def plot_2d_function(function, lower_bound, upper_bound, res=50, contour=False):
    fig = plt.figure()
    if contour: ax = fig.add_subplot(1, 1, 1, )
    else: ax = fig.gca(projection='3d')
    
    # fontsize
    # [t.set_va('center') for t in ax.get_yticklabels()]
    # [t.set_ha('left') for t in ax.get_yticklabels()]
    # [t.set_va('center') for t in ax.get_xticklabels()]
    # [t.set_ha('right') for t in ax.get_xticklabels()]
    # [t.set_va('center') for t in ax.get_zticklabels()]
    # [t.set_ha('left') for t in ax.get_zticklabels()]
    
    # labels
    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')
    if not contour: ax.set_zlabel(r'$f(x_1,x_2)$')
    
    # ax.zaxis._axinfo['label']['space_factor'] = 10.8
    # ax.zaxis.labelpad=15
    # if function.__name__=='zakharov':
    #    ax.zaxis.labelpad=18 

    # ax.set_title(r'$function.__name__\ Function$')
    # ax.xaxis._axinfo['label']['space_factor'] = 2.8
    if not contour:
        # 3d grid 
        ax.grid(False)
        ax.xaxis.pane.set_edgecolor('white')
        ax.yaxis.pane.set_edgecolor('white')
        ax.zaxis.pane.set_edgecolor('white')
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
    
    # rc('font',size=28)
    # rc('font',family='serif')
    # rc('axes',labelsize=12)

    # Define the mathematical domain
    X = np.linspace(lower_bound, upper_bound, res)
    Y = np.linspace(lower_bound, upper_bound, res)
    XX, YY = np.meshgrid(X, Y)

    ZZ = function(XX,YY)
    
    if not contour:
    # Plot surface plot
        surf = ax.plot_surface(XX, YY, ZZ, cmap='jet',  edgecolor='k', lw=0.1)
        # ax.contour(XX, YY, ZZ, levels=100, lw=3, cmap="jet", linestyles="solid",offset=0 )
    else:
    # plot contour plot instead
        cf = ax.contourf(XX, YY, ZZ, res, cmap='jet')
        cr = ax.contour(cf, levels=cf.levels, colors='k', linewidths=0.5, linestyles='solid', alpha =0.5)
        fig.colorbar(cf)
    # Add a color bar which maps values to colors
    # fig.colorbar(surf, shrink=0.5, aspect=5)
    plt.show()
    plt.savefig(fname='01_relevant_plots/bf_plots/'+str(function.__name__)+'.png', 
                bbox_inches="tight",dpi=500)
    
# %% Call the functions to visualize the plots

if __name__=="__main__":
    # plot_1d_function(tf.ackley,-5,5)
    
    # plot_2d_function(tf.ackley,-5,5)
    # plot_2d_function(tf.sphere,-5,5)
    # plot_2d_function(tf.shubert,-2,2)
    # plot_2d_function(tf.rosenbrock,-2,2)
    # plot_2d_function(tf.michalewicz,-0,4)
    # plot_2d_function(tf.zakharov,-10,10)
    plot_2d_function(tf.peaks,-5,5)
    plot_2d_function(tf.peaks,-5,5, contour=True)
   
   
