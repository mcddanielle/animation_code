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

plt.rc('font', size=20)


################################################################
def get_and_parse_data(data_type,starttime,
                       datafile_prefix = "velocity_data/XV_data_t=",
                       movie_type="smovie"):
    '''Guide to data types

    0: "smtest"      
    read from smtest, write to XV_data_t=39999800.npy

    1: "ascii"
    read from XV_data_t=39999800,
    write XV_data_t=39999800.npy

    2: "binary"
    read from XV_data_t=39999800.npy, 
    could also be smtest_...npy with recode

    '''
    
    init_file=datafile_prefix+"%08d"%(starttime)
    print(data_type)
    #data_type=0
    if data_type == 0:

        #make a series of binary files in subroutine,
        #only call once

        di.read_smtest(movie_type=movie_type)
        #print("!")
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)            
        
    elif data_type == 1:
        particle_data = di.get_data(init_file,7,sep=" ")
        np.save(init_file,particle_data)
        
        #DON'T BOTHER WITH THESE PARAMETERS
        #only in ascii, not smtest
        #vx    = particle_data[4]
        #vy    = particle_data[5]
        #speed = particle_data[6]
            
    elif data_type == 2:
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)
        
    id   = particle_data[0]  #NOT USED
    type = particle_data[1]  #1 OR 2, SETS SIZE, FIXED FOR ANIMATION
    xp   = particle_data[2]  #DYMAMICALLY UPDATED POSITIONS
    yp   = particle_data[3]

    #size = disk_size*np.ones(len(type))

    return id,type,xp,yp

################################################################
#get and parse information that allows us to make the movie
#this is hardcoded, which is ugly
#want these variables to be globals to work with the animation subroutine
def get_input_data(filename):
    '''
    hardcoded to look for two particular types of files
    will exit if it does not get

    filename: Pa0 or Pd0
    '''

    if filename == "Pa0" or "Pcw0":

        print("Reading parameters from: %s"%(filename))

        try:
            #data is traditionally placed in a two column file
            #with a string/number format, where number is integer or float

            #make an empty list to hold data as strings
            input_data_strings = []
            for data in di.import_text(filename,' '):
                #print(data)
                input_data_strings.append(data)
                
        except:
            print("File read error")
            sys.exit()

        
    else:
        print("Code is not written to understand your input file")
        print("Either hardcode your parameters or write a new subroutine")
        sys.exit()
        
    if filename == "Pa0":

        #print(input_data_strings) #= di.get_data(file,2,sep=' ')
        density          = float(input_data_strings[0][1])
        #small_density    = float(input_data_strings[1][1])
        #large_density    = float(input_data_strings[2][1])
        pdensity         = float(input_data_strings[1][1])
        
        Sx               = [0.0,float(input_data_strings[2][1])]
        Sy               = [0.0,float(input_data_strings[3][1])]
        
        radius           = float(input_data_strings[4][1])
        #large_radius     = float(input_data_strings[7][1])
        runtime          = int(  input_data_strings[5][1])
        runforce         = float(input_data_strings[6][1])
        dt               = float(input_data_strings[7][1])
        
        maxtime          = int(input_data_strings[8][1])
        writemovietime   = int(input_data_strings[9][1])
        
        kspring          = float(input_data_strings[10][1])
        lookupcellsize   = float(input_data_strings[11][1])
        potentialrad     = float(input_data_strings[12][1])
        potentialmag     = float(input_data_strings[13][1])
        lengthscale      = float(input_data_strings[14][1])
        drivemag         = float(input_data_strings[15][1])
        drivefrq         = float(input_data_strings[16][1])
        decifactor       = int(  input_data_strings[17][1])
        restart          = int(  input_data_strings[18][1])
        drive_step_time  = int(  input_data_strings[19][1]) 
        drive_step_force = float(input_data_strings[20][1])


        return(Sx, Sy, radius, maxtime, writemovietime )

    elif filename == "Pcw0":
        id_str       = str(input_data_strings[0][1])
        Sx           = [0.0,float(input_data_strings[1][1])]
        Sy           = [0.0,float(input_data_strings[2][1])]
        
        nV           = int(  input_data_strings[3][1])
        f_p          = float(input_data_strings[4][1])
        tot_trough   = int(  input_data_strings[5][1])
        drop         = int(  input_data_strings[6][1])
        dc_current   = float(input_data_strings[7][1])
        dc_curr_incr = float(input_data_strings[8][1])
        dc_maxcurr   = float(input_data_strings[9][1])
        
        Temperature  = float(input_data_strings[10][1])
        temp_incr    = float(input_data_strings[11][1])
        maxtemper    = float(input_data_strings[12][1])
        tot_time     = int(  input_data_strings[13][1])
        restart      = int(  input_data_strings[14][1])
        A_v          = float(input_data_strings[15][1])
        decifactor   = int(  input_data_strings[16][1])
        writemovie   = int(  input_data_strings[17][1])
        bstrength    = float(input_data_strings[18][1])
        ac_current   = float(input_data_strings[19][1])
        ac_frequency = float(input_data_strings[20][1])
        drivenid     = int(  input_data_strings[21][1])

        radius = 1.0
        maxtime = tot_time
        writemovietime = writemovie
        
        return(Sx, Sy, radius, maxtime, writemovietime )
    
    else:
        print("TBD")
        sys.exit()
        
################################################################
def format_plot(Sx=[0,36.5], Sy=[0,36.5],rows=1,columns=1,movieoption="simple"):

    gs=gridspec.GridSpec(rows,columns)
    fig = plt.figure(figsize=(6*columns,6*rows))

    #---------------------------
    #Set up a gridded figure
    #---------------------------
    
    if movieoption == "simple":
        ax1 = fig.add_subplot(gs[:])  #scatter plot of particles
        
    elif movieoption == "animate":

        ax1 = fig.add_subplot(gs[0,0])  #scatter plot of particles
        ax2 = fig.add_subplot(gs[0,1])  #scatter plot of particles

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

    if movieoption == "simple":
        return fig,ax1
    elif movieoption == "animate":

        return fig,ax1,ax2

################################################################
def animate(i,scatter1,fileprefix,
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

    if 0: #extra_args != None:
        #print(extra_args)
        scatter2 = extra_args[0]
        
        time = extra_args[1]
        time.append(i)
        print("time", time)
        yp0 = [extra_args[2]]
        yp0.append(yp[0])
        print("yp0", yp0)
        print(np.newaxis) #what does this even do?

        print("")
        data = np.hstack((np.array(time)[:i,np.newaxis],
                          np.array(yp0)[:i,np.newaxis])) #,
        
        print("data", data)
        
        scatter2.set_offsets(data)
        
        return scatter1,scatter2
    
    return scatter1
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

    scatter_axis.scatter(pin_x,pin_y,c="gray",alpha=0.4,s=size)

    return


################################################################
################################################################
################################################################

if __name__ == "__main__":

    data_types = [0,1,2] #["smtest", "ascii", "binary"]
    data_type = data_types[2]

    disk_size=100
    radius_ratio=2.0
    Sx=[0,60.0]
    Sy=[0,60.0]
    dt=0.002

    if 1:
        plot_type = "movie"
        starttime=0 
        time_inc=1000   #increment to count by
        maxtime=starttime + 98000 #18000 #9900 #maximum frame to read

    if 0:
        plot_type = "image"
        plot_time = 98000

        
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------
    fig,ax1 = format_plot(Sx=Sx,Sy=Sy)

    #----------------------------------------------
    #plot the quenched disorder
    #----------------------------------------------
    plot_pins(ax1,size=disk_size)

    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="
    id,type,xp,yp = get_and_parse_data(data_type,starttime)
    size = disk_size*np.ones(len(type))
    
    #----------------------------------------------
    #plot the particles
    #----------------------------------------------

    #make a two color map 
    mycmap = colors.ListedColormap(['cornflowerblue', 'red'])

    #plot the data
    scatter1=ax1.scatter(xp,yp,
                         c=type,
                         s=size,cmap=mycmap,edgecolor='k',linewidth=2)

    #------------------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #------------------------------------------------------------------------
    force_template = r'time = %d'
    force_text = ax1.text(0.4, 1.01, '', transform=ax1.transAxes)

    #------------------------------------------------------------------------
    #finally animate everything/make png
    #------------------------------------------------------------------------   

    #following should resize system and pad, but with 1x1 grid
    #causes function to error
    #plt.tight_layout(h_pad=-0.5,w_pad=1.0,pad=0.5)
    
    if plot_type == "movie":
        ani = animation.FuncAnimation(fig, 
                                      animate,
                                      range(starttime,maxtime,time_inc), 
                                      fargs=(scatter1,
                                             datafile_prefix,
                                             force_template,
                                             force_text,data_type),
                                      interval=20, blit=False)


        #name of the movie file
        outputfile="colloid_movie.mp4"
        
        #changing the fps should speed/slow the visual rate
        #do not change the extra_args unless you know what you're doing
        #this sets the codec so that quicktime knows how to handle the mp4
        ani.save(outputfile, fps=12.0, 
                 extra_args=['-vcodec', 'libx264','-pix_fmt', 'yuv420p'])
        
    elif plot_type == "image":
        out_name="scatter_figure.png"
        fig.savefig(out_name)        
    else:
        #live animation for testing
        plt.show()
        
    exit()

    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.  multiple times?  fix!
    '''
        for k in range(len(type)):
            if type[k]==1:
                size[k]=disk_size
            else:
                size[k]=disk_size*(radius_ratio**2)
                #size = scale*radius^2, i.e. area, not radius
    '''     
