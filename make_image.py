"""
Make a png/pdf of a single frame.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
#from matplotlib import cm
import matplotlib.ticker as ticker

import sys
#functions written by D.M. to get and plot specific data files
import data_importerDM as di

plt.rc('font', size=20)


#--------------------------------------------------------------
#add pin locations to scatter plot
#--------------------------------------------------------------
def plot_pins(scatter_axis, size=75,pin_file="pin_array.dat"):
    '''plot the pinning array from ascii file with pin_file:
    --------------------------------------------------
    n     x     y    radius mag
    int float float  float  float
    ---------------------------------------------------
    required args:
    scatter_axis = matplotlib axes object

    optional args:
    size=75, to plot pin radius
    pin_file="pin_array.dat"
    '''
    try: 
        pin_data = di.get_data(pin_file,5,sep=" ")
    except:
        print("No pinning data in expected format")
        return
    pin_x = pin_data[1]
    pin_y = pin_data[2]
    pin_rad = pin_data[3]
    pin_mag = pin_data[4]

    scatter_axis.scatter(pin_x,pin_y,c="gray",alpha=0.4,s=size) #,rasterized=True)

    return


################################################################
################################################################
################################################################

if __name__ == "__main__":


    #---------------------------
    #system specific variables
    #---------------------------
    disk_size=100

    Sx=[0,60.0]
    Sy=[0,60.0]

    plot_time=4500000 #9950 #what frame to plot
    #---------------------------
    #Set up a gridded figure
    #---------------------------
    rows=1
    columns=1

    gs=gridspec.GridSpec(rows,columns)
    fig = plt.figure(figsize=(6*columns,6*rows))

    ax1 = fig.add_subplot(gs[:])  #scatter plot of particles

    #---------------------------------
    #add labels and axes ticks
    #-----------------------------------
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_ylim(0,Sy[1])
    ax1.set_xlim(0,Sx[1])
    num_ticks=6
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(num_ticks))

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------
    
    datafile_prefix = "velocity_data/XV_data_t="
    plot_file=datafile_prefix+"%08d"%(plot_time)
    particle_data = di.get_data(plot_file,7,sep=" ")
        
    id   = particle_data[0]  #NOT USED
    type = particle_data[1]  #1 OR 2, SETS SIZE, FIXED FOR ANIMATION
    xp   = particle_data[2]  #DYMAMICALLY UPDATED POSITIONS
    yp   = particle_data[3]

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
            size[k]=disk_size
            

    #make a two color map 
    mycmap = colors.ListedColormap(['cornflowerblue', 'red'])

    #---------------------------------------------------------
    #Finally plot the data
    #---------------------------------------------------------
    plot_pins(ax1,size=disk_size)
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap)

    #------------------------------------------------------------------------
    # (turned off) add an annotation
    # note: "force" was for a different system, here time is relevant
    #------------------------------------------------------------------------
    if 0:
        force_template = r'$F_D/F_p = %1.2f$'
        #force_template = r'time = %d'        
        force_text = ax1.text(0.5, 1.05, '', ha='center',
                              transform=ax1.transAxes,fontsize=22)

    out_name="scatter_figure.png"
    fig.savefig(out_name)
        
    sys.exit()
