#!/usr/bin/env python

"""
A simple example of an animated plot
SOURCE: http://matplotlib.org/examples/animation/simple_anim.html
#to make a gif:
https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
import matplotlib.ticker as ticker

import matplotlib.animation as animation
import sys

#functions written by D.M. to get and plot specific data files
import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=20)


################################################################
################################################################
################################################################

if __name__ == "__main__":

    get_ascii_data = 1

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------
    Sx=[0,60.0]
    Sy=[0,60.0]
    dt=0.002

    disk_size=100
    radius_ratio=2.0

    starttime=0 
    time_inc=1000   #increment to count by
    maxtime=starttime + 98000 #18000 #9900 #maximum frame to read

    datafile_prefix = "velocity_data/XV_data_t="
    init_file=datafile_prefix+"%08d"%(starttime)
    
    #---------------------------
    #Create a grid figure -
    #overkill for this, but useful for including more data
    #---------------------------
    rows=1
    columns=1

    gs=gridspec.GridSpec(rows,columns)
    fig = plt.figure(figsize=(10*columns,10*rows))

    ax1 = fig.add_subplot(gs[:])  #scatter plot of particles

    cpl.plot_pins(ax1,size=disk_size)

    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_ylim(0,Sy[1])
    ax1.set_xlim(0,Sx[1])
    num_ticks=6
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(num_ticks))

    if 1:

        di.read_smtest()
        datafile_prefix = "velocity_data/smtest_"
        init_file=datafile_prefix+"%08d"%(starttime)
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)            

        
    if 0:
        if get_ascii_data:    
            particle_data = di.get_data(init_file,7,sep=" ")
        else:
            binary_file = "%s%s"%(init_file,".npy")
            particle_data = np.load(binary_file)
        
    id   = particle_data[0]  #NOT USED
    type = particle_data[1]  #1 OR 2, SETS SIZE, FIXED FOR ANIMATION
    xp   = particle_data[2]  #DYMAMICALLY UPDATED POSITIONS
    yp   = particle_data[3]

    size = disk_size*np.ones(len(type))
    
    #DON'T BOTHER WITH THESE PARAMETERS
    #vx    = particle_data[4]
    #vy    = particle_data[5]
            #speed = particle_data[6]

    if get_ascii_data:
        np.save(init_file,particle_data)

    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.
    #multiple times?  fix!

    '''
    for k in range(len(type)):
    if type[k]==1:
        size[k]=disk_size
    else:
        size[k]=disk_size*(radius_ratio**2)
    '''        
    
    #make a two color map 
    mycmap = colors.ListedColormap(['cornflowerblue', 'red'])
    
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap)

    #---------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #-------------------------------------------------------------
    force_template = r'time = %d'
    force_text = ax1.text(0.4, 1.01, '', transform=ax1.transAxes)
            
    #-----------------------------------------------------------------
    #finally animate everything
    #-----------------------------------------------------------------   
    
    ani = animation.FuncAnimation(fig, 
                                  cpl.animate,
                                  range(starttime,maxtime,time_inc), 
                                  fargs=(scatter1,
                                         datafile_prefix,
                                         force_template,
                                         force_text,
                                         get_ascii_data),
                                  interval=20, blit=False)


        
    #following should resize system and pad, but with 1x1 grid
    #causes function to error
    #plt.tight_layout(h_pad=-0.5,w_pad=1.0,pad=0.5)

    #make a movie
    if 1:
        #name of the movie file
        outputfile="Supp1.mp4"
        
        #changing the fps should speed/slow the visual rate
        #do not change the extra_args unless you know what you're doing
        #this sets the codec so that quicktime knows how to handle the mp4
        ani.save(outputfile, fps=12.0, 
                 extra_args=['-vcodec', 'libx264','-pix_fmt', 'yuv420p'])
    else:
        #live animation for testing
        plt.show()

    sys.exit()
