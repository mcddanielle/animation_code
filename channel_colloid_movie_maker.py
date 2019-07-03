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
def print_dt(data_type):
    '''just a little function for verbose printing
    '''
    
    if data_type == 0:
        print("Reading directly from smtest (binary)")
        print("Writing velocity_data/XV*npy files")
    elif data_type == 1:
        print("Reading from velocity_data/XV* files (ascii)")
        print("Writing velocity_data/XV*npy files")
    elif data_type == 2:
        print("Reading velocity_data/XV*npy files (binary)")

    return

################################################################
def animate_with_phase(i,scatter1,fileprefix,
            force_template,force_text,data_type,
            extra_args):
    '''
    subroutine driven by the matplotlib animation library

    i:  integer
        clock time of simulation, 
        used in naming scheme for velocity files

    scatter1: matplotlib plot object
              plot containing positions of particles to be updated

    fileprefix: string 
                used to name all data files, needs i to specify file

    force_template: string with integer argument
                    is used to update the frame-by-frame label

    force_text: matplotlib text object
                the text itself is updated with every frame call
                but the object's position and settings 
                are given in the main function 

    data_type: 0/1/2

              0: read formatted data from smtest AND writes binary files
              for subsequent movie making from the same data sets

              1: reads ascii files (slow) AND writes binary files
              for subsequent movie making from the same data sets

              2: directly reads the ".npy" binary files
              which contain numpy arrays of the data that 
              also sits in the ascii file

    fp: file pointer
    nV: number vorticles

    optional args:
    extra_args: may contain a list of 
    whatever you'd like to unpack into more variables

    '''

    ############################################################
    #get new particle positions from new integer time i
    ############################################################
    init_file=fileprefix+"%08d"%(i)

    if data_type == 0 or data_type == 2:
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)
        
    elif data_type == 1:    
        particle_data = di.get_data(init_file,7,sep=" ")
        
        #if we haven't save the data in binary format, do it now
        np.save(init_file,particle_data)
        
    #either way, the relevant data the particle positions
    #we already know the particle id and its size
    xp = particle_data[2]
    yp = particle_data[3]
    
    
    '''
    #if you need to change the particle sizes with time
    #for instance if your system is under compression
    #this is the format of the array and the manner
    #to update a size array
    if i>1000000:
        new_sizes = np.array([50 - i/1000000.0]*len(xp))
        scatter1.set_sizes(new_sizes)
    '''

    #specially formatted array to update scatter plot
    #format is in pairs [x1,y1], [x2,y2], etc
    data = np.hstack((xp[:i,np.newaxis], yp[:i, np.newaxis]))
    #data = np.hstack((xp[:i,0], yp[:i,0]))

    #update the scatter plot created in the main function with the new data
    scatter1.set_offsets(data)
    
    #if you're changing the color
    #color_array = np.array(something)
    #scatter1.set_array(color_array)

    #update the text label for the new time
    force_text.set_text(force_template%(i))

    #print current time to user
    verbose = True
    if verbose == True and (i%10000==0):
        print("plotting frame: %d"%(i))

    if extra_args != None and (i%200==0):
        
        #unpack the extra_args - these are user defined by function
        scatter2 = extra_args[0]
        time = extra_args[1]
        y0 = extra_args[2]

        time_int = int(i/200)

        #print("")
        data_new = [time[time_int],y0[time_int]]
        scatter2.set_offsets(data_new)
        
        return scatter1,scatter2
    
    return scatter1

################################################################
################################################################
################################################################

if __name__ == "__main__":

    verbose = False

    #name of the movie file - make this anything you want
    outputfile="Supp1.mp4"

    #this is because I'm adding a second subplot
    if 0:
        movie_type = "Simple"  # standard, single window
    else:
        movie_type = "animate" # two panels, side by side, phase diagram
    
    #Data files can be the following, smtest is fastest
    #smtest (single binary), ascii (velocity_data/XV...integer), binary (*npy)
    #[0="smtest", 1="ascii", 2="npy style binary"]
    data_type = 0 

    #------------------------------------------------------------------------
    #get data for initial frame, this is the MD code input file
    #------------------------------------------------------------------------
    inputfile = "Pcw0"

    if verbose == True:
        print_dt(data_type)
        print("Getting system size and times from %s",inputfile)

    #get the data from Pcw0 - hardwired for a certain format
    #this could be improved
    (Sx, Sy, radius, maxtime, writemovietime ) = cpl.get_input_data(inputfile)

    #hard coded by what "looks good" basically a ratio of system size
    #and fig size to make the particles look the size
    #of their interaction length
    disk_size=100  

    #######################################################################
    #times - may adjust if your initial sampling was too many / too long
    #######################################################################
    starttime=0 
    time_inc=writemovietime     #make larger if the movie is too detailed
    maxtime=maxtime - time_inc  #make lesser if the movie is too long
    
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------

    if movie_type == "Simple":
        #1x1 plot
        fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sy)
    else:
        #1x2 plot
        fig,ax1,ax2 = cpl.format_plot(Sx=Sx,Sy=Sy,
                                  rows=1,columns=2,
                                  movieoption="animate")

    #---------------------------
    #plot the pinning array - the channel has none colloid
    #---------------------------
    cpl.plot_pins(ax1,size=disk_size)

    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="
    id,type,xp,yp = cpl.get_and_parse_data(data_type,
                                           starttime,
                                           movie_type="smovie")

    #--------------------------------------------
    #COLOR THE PARTICLES
    #---------------------------------------------
    #the plot needs to know what size to make each particle
    #make all particles the same size
    size = disk_size*np.ones(len(type))

    #this is to color the driven particle differently than non-driven
    type[0] = 2

    #----------------------------------------------
    #plot the particles
    #----------------------------------------------
    
    #make a two color map on axis
    mycmap = colors.ListedColormap(['mediumseagreen','coral'])
    
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap)

    if movie_type == "animate":
        #set up a yp vs. time plot... for now
        #get the data

        data_phase = np.loadtxt("phase_p0.dat", #delimiter =' ',
                                comments='#',
                                usecols =(0, 1, 2, 3, 4),  
                                unpack = True)
        time = data_phase[0]
        x0 = data_phase[1]
        y0 = data_phase[2]
        fx0 = data_phase[3]
        fy0 = data_phase[4]
        
        ax2.plot(time,y0) #,c=type,s=size,cmap=mycmap)
        scatter2=ax2.scatter(time[0],y0[0],
                             marker="o",s=50,c="magenta",zorder=9)
        
        #ax2.set_xlim(time,maxtime)
        #ax2.set_ylim(0.0,36.5)
        ax2.set_xlabel("time")
        ax2.set_ylabel(r"$y_0$")
    #---------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #-------------------------------------------------------------
    force_template = r'time = %d'
    force_text = ax1.text(0.4, 1.01, '', transform=ax1.transAxes)
            
    #-----------------------------------------------------------------
    #finally animate everything
    #-----------------------------------------------------------------

    if movie_type == "Simple":
        #this is from the general library
        function=cpl.animate
        fargs=(scatter1,
               datafile_prefix,
               force_template,
               force_text,
               data_type,None)
        
    elif movie_type == "animate":
        #note this is local
        function=animate_with_phase
        fargs=(scatter1,
               datafile_prefix,
               force_template,
               force_text,
               data_type,
               (scatter2,time,y0))   #extra args     

        #following should resize system and pad, but with 1x1 grid
        #causes function to error
        fig.tight_layout() #h_pad=-0.5,w_pad=1.0,pad=0.5)
        
    ani = animation.FuncAnimation(fig, 
                                  function,
                                  range(starttime,maxtime,time_inc), 
                                  fargs=fargs,
                                  interval=20, blit=False)

        


    #make a movie
    if movie_type == "Simple" or movie_type == "animate":
        
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

