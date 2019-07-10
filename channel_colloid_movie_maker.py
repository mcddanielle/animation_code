#!/usr/bin/env python

"""
A simple example of an animated plot
SOURCE: http://matplotlib.org/examples/animation/simple_anim.html
#to make a gif:
https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/
"""

#numeric and basic plotting libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

#for multiplots
#import matplotlib.gridspec as gridspec

#for axes labels
#import matplotlib.ticker as ticker

#used for contour plot to make background colors
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LightSource, Normalize
from matplotlib import cm

#to animate, obviously
import matplotlib.animation as animation

#to work with files, call sys.exit(), etc
import sys

#functions written by D.M. to get and plot specific data files
#import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=20)

##########################################################
#ADD CONTOUR PLOT
##########################################################
def add_contour(ax,L,N,corrugated = True):
    '''
    Hardwired to color in the quasi1D potential to contain 
    the particles in a trough.  
    Can also add the washboard/corrugated substrate.

    Required Arguments

    Optional Arguments:

    corrugated (default = True)  
    Adds the washboard in the y-direction.  Hardwired for a single parameter set.

    '''

    a_p = L/N

    X = np.arange(0, L/2.0, 0.1)
    Y = np.arange(0, L, 0.1)
    X, Y = np.meshgrid(X, Y)

    if corrugated == False:
        Z = 2.0*np.sin(2*np.pi*X/L)
    else:
        Z = np.sin(2*np.pi*Y/a_p) + 2.0*np.sin(2*np.pi*X/L)


    cmap=cm.coolwarm_r
    ls = LightSource(315, 45)
    rgb = ls.shade(Z, cmap)

    #got goofy error messages about the removed kwargs
    #cset = ax.contourf(X, Y, Z, zdir='z', offset=-1, cmap=cmap,rasterized=True,alpha=0.5)
    cset = ax.contourf(X, Y, Z, cmap=cmap,alpha=0.25)

    #ax.imshow(rgb)

    #ax1.set_xlim(15,20)
    #ax1.set_ylim(15,20)

    #ax1.set_xlabel(r"$X$")
    #ax1.set_ylabel(r"$y$",rotation='horizontal',ha='right')

    #ax1.set_xticks([])
    #ax1.set_yticks([])
    return

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
    yp = particle_data[3] #- 36.5/4.0

    shift = False
    if shift == True:
        for m in range(len(yp)):
            if yp[m] > 36.5/4.0:
                yp[m] -= 36.5/4.0
            else:
                yp[m] += 0.75*36.5
    
    
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

    #update the text
    drop = 4000.0
    curr_inc = 0.001
    fd = (i//drop)*curr_inc
    if force_template:
        force_text.set_text(force_template%(fd))
    
    #print current time to user
    verbose = True
    if verbose == True and (i%10000==0):
        print("plotting frame: %d"%(i))

    if extra_args != None and (i%100==0):
        
        #unpack the extra_args - these are user defined by function
        scatter2 = extra_args[0]
        #time = extra_args[1]
        #y0 = extra_args[2]
        
        time_int = int(i/100)

        #print("")
        try:
            data_new = [extra_args[1][time_int],extra_args[2][time_int]]
            #data_new = [extra_args[1][i],extra_args[2][i]]
            scatter2.set_offsets(data_new)
        except:
            print("data_new doesn't exist",i,time_int)

                #update the text label for the new time
                
        if force_template:

            force_text.set_text(force_template%(fd))
            return force_text,scatter1,scatter2
        else:
            return scatter1,scatter2
            

    #update the text label for the new time
    if force_template:
    
        return force_text,scatter1
    else:
        return scatter1

################################################################
################################################################
################################################################

if __name__ == "__main__":

    verbose = False
    image_test = True #if true, make a png instead of a movie to look at the "frame"
    #image_test = False
    
    #drop = 2000  #used to estimate the updates to the animated plots (hardcoded in animate() routine)
    
    #name of the movie file - make this anything you want
    outputfile="Supp1.mp4"

    #name of parameter file, this varies by simulation (Pa0, Pcw0, etc)
    inputfile = "Pcw0"
    
    #this is because I'm adding a second subplot
    if 1:
        movie_type = "Simple"        # one panel standard, single window
    elif 1:
        movie_type = "animate"       # two panels, side by side, phase diagram
    else:
        movie_type = "animate_fd_v0" # two panels, side by side, Force-Velocity diagram

        
    ###########################################################################
    #Data files format
    #smtest (single binary), ascii (velocity_data/XV...integer), binary (*npy)
    #[0="smtest", 1="ascii", 2="npy style binary"]
    ############################################################################
    data_type = 0  #smtest is fastest (0 is preferable)

    #-----------------------------------------------------------------------------------
    #get data for initial frame, this is either smtest, or one of the alternate formats
    #-----------------------------------------------------------------------------------

    if verbose == True:
        print_dt(data_type)
        print("Getting system size and times from %s",inputfile)

    #get the data from Pcw0 - hardwired for a certain format
    #this could be improved
    (Sx, Sy, radius, maxtime, writemovietime ) = cpl.get_input_data(inputfile)

    #This is to zoom in along the x-axis
    #and cut some of the blank space, could tweak the aspect ratio more
    Sx[1]=Sx[1]/2.0
    
    #hard coded by what "looks good" basically a ratio of system size
    #and fig size to make the particles look the size
    #of their interaction length -
    #this is tricky with this system since they don't have a well defined size.
    disk_size=200  

    #######################################################################
    #times - may adjust if your initial sampling was too many / too long
    #######################################################################
    starttime=0 #int(3*10000/4.0) 
    time_inc=writemovietime     #make larger if the movie is too detailed
    maxtime=maxtime - time_inc  #make lesser if the movie is too long
    
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------

    if movie_type == "Simple":
        #1x1 plot
        fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sy)
    else:
        #1x2 plot, so far that is the only option,
        #if you want something more complicated,
        #may need to rewrite the cpl module, but that isn't hard.
        fig,ax1,ax2 = cpl.format_plot(Sx=Sx,Sy=Sy,
                                      rows=1,columns=2,
                                      movieoption=movie_type)

    #---------------------------
    #plot the energy landscape
    #---------------------------
    if 0:
        #pinning array 
        cpl.plot_pins(ax1,size=disk_size)
    else:
        #use a contour plot to show the landscape,
        #corr = True/False turns off/on the corrugations in the plot
        corr = False
        corr = True
        add_contour(ax1,36.5,20.0,corrugated = corr)

    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="
    id,type,xp,yp = cpl.get_and_parse_data(data_type,
                                           starttime,
                                           movie_type="smovie")

    #the following code may be used if the interesting behavior is happening too high/low on the
    #screen, so the interesting behavior is obscured by the pbc.
    #when you shift the particle positions, you have to account for the pbc.
    #note that this is NOT a pythonic way to do this, so it is probably inefficient
    shift = False
    if shift == True:
        for i in range(len(yp)):
            if yp[i] > 36.5/4.0:
                yp[i] -= 36.5/4.0
            else:
                yp[i] += 0.75*36.5

    
    
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
    if movie_type == "Simple":
        mycmap = colors.ListedColormap(['mediumseagreen','coral'])
    else:
        mycmap = colors.ListedColormap(['magenta'])
    
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap,edgecolor='k')

    if movie_type != "Simple":
        #set up a yp vs. time plot... for now
        #get the data

        #notice that we are NOT using the DM developed data importer
        #and instead using a numpy built-in function
        #this is probably faster.  I haven't clocked it though...
        
        data_phase = np.loadtxt("phase_p0.dat", #delimiter =' ',
                                comments='#',
                                usecols =(0, 1, 2, 3, 4),  
                                unpack = True)
        time = data_phase[0]
        x0 = data_phase[1]
        y0 = data_phase[2]
        fx0 = data_phase[3]
        fy0 = data_phase[4]

        if movie_type == "animate_fd_v0":

            drop = 4000.0
            curr_inc = 0.001
            fd = time*curr_inc/drop
            
            ax2.plot(fd,fy0,"o--") #,c=type,s=size,cmap=mycmap)
            scatter2=ax2.scatter(fd[0],fy0[0],
                                 marker="o",s=100,c="magenta",zorder=9)

            ax2.set_xlabel(r"$F_{Drive}$")
            ax2.set_ylabel(r"$\bar{v}_y$")
        
        elif movie_type == "animate":

            #phase calculations - TBD how to do this for our system
            #if DC is zero (or small), then subtracting off the (mean force)*time
            #actually creates a helix.
            #what is going on, and how can we fix it.  
            phi_y =  2*np.pi*(y0 - np.mean(fy0)*time*0.01 - y0[0])
            dphi_y = 2*np.pi*(fy0-np.mean(fy0))
            
            ax2.scatter(phi_y,dphi_y) #,"o--") #,c=type,s=size,cmap=mycmap)
            plot_time = int(starttime/writemovietime)
            scatter2=ax2.scatter(phi_y[plot_time],dphi_y[plot_time],
                                 marker="o",s=100,c="magenta",zorder=9)

            ax2.set_xlabel(r"$\phi_y$")
            ax2.set_ylabel(r"$d\phi_{y}/dt$")
        
        #ax2.set_xlim(time,maxtime)
        #ax2.set_ylim(0.0,36.5)
        

    #---------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #-------------------------------------------------------------
    if movie_type == "Simple":
        if 1:
            force_template = r'time = %d'
        else:
            force_template = r'$F_{Drive}$ = %1.2f'
            
        force_text = ax1.text(0.5, 1.02, '', transform=ax1.transAxes,ha="center")
    else:
        if 0:
            force_template = r'$F_{Drive}$ = %1.2f'
            force_text = ax2.text(0.2, 0.8, '', transform=ax2.transAxes)
        else:
            force_template = None
            force_text = None
            
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
        
    elif "animate" in movie_type:
        #note this is local
        function=animate_with_phase
        fig.tight_layout() #h_pad=-0.5,w_pad=1.0,pad=0.5)
        
        if movie_type == "animate":
            fargs=(scatter1,
                   datafile_prefix,
                   force_template,
                   force_text,
                   data_type,
                   (scatter2,phi_y,dphi_y))   #extra args
            
        elif movie_type == "animate_fd_v0":

            fargs=(scatter1,
                   datafile_prefix,
                   force_template,
                   force_text,
                   data_type,
                   (scatter2,fd,fy0))   #extra args
            
        #following should resize system and pad, but with 1x1 grid
        #causes function to error
        fig.tight_layout() #h_pad=-0.5,w_pad=1.0,pad=0.5)

    else:
        fargs=(scatter1,
               datafile_prefix,
               force_template,
               force_text,
               data_type,
               (scatter2,time,y0))   #extra args
        

        
    ani = animation.FuncAnimation(fig, 
                                  function,
                                  range(starttime,maxtime,time_inc), 
                                  fargs=fargs,
                                  interval=20, blit=False)

        


    #make a movie
    if image_test == True:
        plt.savefig("test.png")
    
    elif movie_type == "Simple" or "animate" in movie_type:
        
        #changing the fps should speed/slow the visual rate
        #do not change the extra_args unless you know what you're doing
        #this sets the codec so that quicktime knows how to handle the mp4
        ani.save(outputfile, fps=10.0, 
                 extra_args=['-vcodec', 'libx264','-pix_fmt', 'yuv420p'])

    else:
        #live animation for testing - it works, but avoid this
        plt.show()

    sys.exit()

    #####################################################################

