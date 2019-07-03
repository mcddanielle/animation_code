#!/usr/bin/env python

"""
A simple example of an animated plot
SOURCE: http://matplotlib.org/examples/animation/simple_anim.html
#to make a gif:
https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/

trouble saving file, but animation library working:
https://stackoverflow.com/questions/23856990/cant-save-matplotlib-animation
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#import matplotlib.gridspec as gridspec
#import matplotlib.ticker as ticker

import matplotlib.animation as animation
import sys, os

#functions written by D.M. to get and plot specific data files
#import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=14)
plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'
################################################################
################################################################
################################################################

if __name__ == "__main__":

    directory="velocity_data"

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    #all possibilities
    data_types = [0,1,2] #["smtest", "ascii", "binary"]

    #the one we will use
    data_type = data_types[2]

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

    if 1:
        (Sx, Sy, radius, maxtime, writemovietime ) = cpl.get_input_data(inputfile)

        #maxtime = 10*writemovietime
    '''
    Sx=[0,60.0]
    Sy=[0,60.0]
    radius=0.5
    maxtime=40000020 #- 30 #30000 #10000000
    writemovietime=30 #50
    '''
    #get from Pa0
    #Sx=[0,36.5]
    #Sy=[0,36.5]
    #dt=0.002

    disk_size=30  #hard coded by what "looks good"

    starttime=writemovietime #49500000 #
    starttime = 40000020 
    time_inc=writemovietime
    #maxtime=starttime + 10000 # - 30 #40010000
    maxtime=starttime+999*time_inc  #maxtime - time_inc
    
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


    radius_ratio=2.0

    for k in range(len(type)):
        if type[k]==2:
            size[k]=disk_size
        else:
            size[k]=disk_size*(radius_ratio**2)

    
    #----------------------------------------------
    #plot the particles
    #----------------------------------------------
    
    #make a two color map 
    mycmap = colors.ListedColormap(['cornflowerblue', 'red'])
    
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap,edgecolor='k',linewidth=1)

    #---------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #-------------------------------------------------------------
    force_template = r'time = %d'


    label=True
    if label == True:
        figure_text1 = r"Fig. 11(b), Yang $et$ $al.$"
        figure_text2 = r"$\phi = 0.59$, $F_D/F_P = 0.90$"
    
        ax1.text(-0.1, 1.1, figure_text1, transform=ax1.transAxes) 
        ax1.text(0.01, 1.01, figure_text2, transform=ax1.transAxes)

    #add the time at each subsequent timestep
    force_text = ax1.text(0.6, 1.01, '', transform=ax1.transAxes)
   
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
                                  interval=20, blit=True)

        
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

        '''
        note that if you feed this code improper file names, 
        you won't see the effects earlier as a code failure, 
        it will just fail dramatically here
        '''
        
    else:
        #live animation for testing
        plt.show()

    sys.exit()

    ###################################################################
    #####################################################################
    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.
    #multiple times?  fix!


