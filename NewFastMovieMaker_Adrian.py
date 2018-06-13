#!/usr/bin/env python

"""
A simple example of an animated plot
SOURCE: http://matplotlib.org/examples/animation/simple_anim.html
#to make a gif:
https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#import matplotlib.gridspec as gridspec
#import matplotlib.ticker as ticker

import matplotlib.animation as animation
import sys

#functions written by D.M. to get and plot specific data files
#import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=20)

################################################################
################################################################
################################################################

if __name__ == "__main__":

    #all possibilities
    data_types = [0,1,2] #["smtest", "ascii", "binary"]

    #the one we will use
    data_type = data_types[0]

    if data_type == 0:
        print("Reading directly from smtest (binary)")
        print("Writing velocity_data/XV*npy files")
    elif data_type == 1:
        print("Reading from velocity_data/XV* files (ascii)")
        print("Writing velocity_data/XV*npy files")
    elif data_type == 2:
        print("Reading velocity_data/XV*npy files (binary)")

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------
    inputfile = "Pa0"
    
    (Sx, Sy, radius, maxtime, writemovietime ) = cpl.get_input_data(inputfile)

    #get from Pa0
    #Sx=[0,36.5]
    #Sy=[0,36.5]
    #dt=0.002

    disk_size=100  #hard coded by what "looks good"

    starttime=0 
    time_inc=writemovietime
    maxtime=maxtime - time_inc
    
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------
    fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sy)

    #---------------------------
    #plot the pinning array
    #---------------------------
    cpl.plot_pins(ax1,size=disk_size)

    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="
    id,type,xp,yp = cpl.get_and_parse_data(data_type,
                                           starttime,
                                           movie_type="cmovie")

    #the plot needs to know what size to make each particle
    #this is overkill for monodisperse systems
    size = disk_size*np.ones(len(type))

    #----------------------------------------------
    #plot the particles
    #----------------------------------------------
    
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
                                         data_type),
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

    #####################################################################
    #####################################################################
    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.
    #multiple times?  fix!

    '''
    radius_ratio=2.0

    for k in range(len(type)):
    if type[k]==1:
        size[k]=disk_size
    else:
        size[k]=disk_size*(radius_ratio**2)
    ''' 
