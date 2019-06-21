#!/usr/bin/env python

"""
Make a png/pdf of a single frame.
"""

import numpy as np
from scipy.spatial import cKDTree as KDTree
import boo

import matplotlib
matplotlib.use('Agg')   #for batch jobs!!!

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
#from matplotlib import cm
import matplotlib.ticker as ticker

import sys

#functions written by D.M. to get and plot specific data files
import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=20)


################################################################
################################################################
################################################################

def just_boo_it(pos,ax, diameter=1.0,verbose=True, markersize=10):
    '''
    '''

    #somewhat arbitrary max distance between neighbors
    maxbondlength=diameter*np.sqrt(2) #*diameter

    #use library to create spatial indexing
    #the following line creates an instance of the object
    tree = KDTree(pos, 12)

    #one of the methods of tree is the query_pairs() 
    #query
    bonds = tree.query_pairs(maxbondlength, output_type='ndarray')
    
    if verbose == True:
        print("The bonds have been calculated, and are stored in an array of: ",bonds.shape)

    ################################################
    #calculate inner particles (vs. edge particles)
    ################################################
    #this is a ndarray containing data type boolean variables (T/F)
    #the ampersand is a "bitwise and" meaning that if both of the following
    #conditions are true, the overall condition of "inside" is true
    #those conditions are....
    #(1) take the minimum of ?
    #black magic of perl like proportions.
    inside = np.min((pos - pos.min(0) > maxbondlength) & (pos.max() - pos > maxbondlength), -1)

    #######################################
    #number of neighbours per particle
    #######################################
    Nngb = np.zeros(len(pos), int)
    np.add.at(Nngb, bonds.ravel(), 1)
    inside[Nngb<4] = False

    ########################################
    #calculate bond order parameters
    ########################################
    q6m = boo.bonds2qlm(pos, bonds, l=6)
    q4m = boo.bonds2qlm(pos, bonds, l=4)

    ######################################################
    #course-grained - check run time for large systems?
    #note that we don't use this one... yet
    ######################################################
    Q6m, inside2 = boo.coarsegrain_qlm(q6m, bonds, inside)
    Q4m, inside2 = boo.coarsegrain_qlm(q4m, bonds, inside)

    ######################################################
    #identify crystalline particles
    #####################################################
    xpos = boo.x_particles(q6m, bonds, nb_thr=4)
    
    if(verbose):
        print(xpos)
        print(xpos.mean())

    #id the "surface" or edge particles
    surf = boo.x_particles(q6m, bonds, nb_thr=2) & np.bitwise_not(xpos)


    for label, subset in zip(['other', 'surface', 'crystal'],
                             [np.bitwise_not(xpos|surf), surf,xpos]):
        ax.scatter(pos[subset,0], pos[subset,1], s=markersize, marker='o', label=label)



    ###########################################    
    #rotational invariants
    ##########################################
    q6 = boo.ql(q6m)
    q4 = boo.ql(q4m)

    return np.mean(q6)



################################################################
################################################################
################################################################
    
if __name__ == "__main__":

    verbose = 1
    get_ascii_data = 1
    #---------------------------
    #system specific variables
    #---------------------------
    disk_size=15

    Sx=[0,60.0]
    Sy=[0,60.0]

    plot_time=10000 #3600 #1200000 #24000000 #49950000 #time to plot
    #print(plot_time)

    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------
    fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sx)

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------   
    datafile_prefix = "velocity_data/XV_data_t="
    plot_file=datafile_prefix+"%08d"%(plot_time)

    if(verbose):
        print(plot_file)
    
    if get_ascii_data == 0:
        plot_file=plot_file+".npy"
        particle_data = np.load(plot_file)
    else:
        particle_data = di.get_data(plot_file,7,sep=" ")
        
    if(verbose):
        print("Reading in file: %s"%(plot_file))
        

        
    id   = particle_data[0]  #NOT USED
    type = particle_data[1]  #1 OR 2, SETS SIZE, FIXED FOR ANIMATION
    xp   = particle_data[2]  #DYMAMICALLY UPDATED POSITIONS
    yp   = particle_data[3]
    zp   = np.zeros(len(xp)) #for pyboo
    
    #DON'T BOTHER WITH THESE PARAMETERS
    #vx    = particle_data[4]
    #vy    = particle_data[5]
    #speed = particle_data[6]

    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.  multiple times?  fix!

    size  = np.zeros(len(type))
    for k in range(len(type)):
        if type[k]==1:
            size[k]= 1.4**2 * disk_size
        else:
            size[k]= disk_size
            

    #make a two color map
    if 0:
        mycmap = colors.ListedColormap(['mediumseagreen'])
    else:
        mycmap = colors.ListedColormap(['cornflowerblue', 'red'])


    #---------------------------------------------------------
    #Finally plot the data
    #---------------------------------------------------------

    cpl.plot_pins(ax1,size=disk_size)
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap,edgecolor='k')


    #----------------------------------------------------------
    #Just Boo It!
    #----------------------------------------------------------
    #pack all of the data into an array of 3 columns
    pos_data = np.vstack((xp, yp, zp)).T

    #run the pyboo measures.  the library has some unused functionality.
    print(just_boo_it(pos_data,ax1))
    #------------------------------------------------------------------------
    # (turned off) add an annotation
    # note: "force" was for a different system, here time is relevant
    #------------------------------------------------------------------------


    out_name="pyboo_data.png"
    fig.savefig(out_name)
        
    sys.exit()
