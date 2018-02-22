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
#from matplotlib import cm
import matplotlib.ticker as ticker

import matplotlib.animation as animation

#functions written by D.M. to get and plot specific data files
import data_importerDM as di

plt.rc('font', size=20)


#IMPORTANT FLAG FOR EFFICIENT MOVIE MAKING (GLOBAL)
get_data=0

#if get_data=1,
#reads ascii files (slow) AND writes binary files
#for subsequent movie making from the same data sets
#if get_data=0
#code directly reads the ".npy" binary files
#which contain numpy arrays of the data that also sits in the ascii file
#note the similar naming structure
#which is much more efficient
##used in both animate and the main function

#could use os.path.isfile(fname) 
#to deterimine if binary files already exist
#but the problem is if you have re-written the ascii files
#you want to read those and create new binary files
#rather than reading the old (faulty?) files
    
################################################################
################################################################
################################################################
def animate(i,scatter1,fileprefix,
            force_template,force_text):
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

    '''
    
    ############################################################
    #get new particle positions from new integer time i
    ############################################################
    init_file=fileprefix+"%08d"%(i)
    
    if get_data:
        #read ascii file
        particle_data = di.get_data(init_file,7,sep=" ")

    else:
        #read binary file
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)        

    #either way, the relevant data the particle positions
    #we already know the particle id and its size
    xp = particle_data[2]
    yp = particle_data[3]
    
    if get_data:
        #if we haven't save the data in binary format, do it now
        np.save(init_file,particle_data)
    
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

    #update the scatter plot created in the main function with the new data
    scatter1.set_offsets(data)
    
    #if you're changing the color
    #color_array = np.array(something)
    #scatter1.set_array(color_array)

    #update the text label for the new time
    force_text.set_text(force_template%(i))

    #print current time to user 
    print i
    
    return scatter1,

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

    pin_data = di.get_data(pin_file,5,sep=" ")
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

    disk_size=100
    radius_ratio=2.0
    #---------------------------
    #Create a grid figure -
    #overkill for this, but useful for including more data
    #---------------------------
    rows=1
    columns=1

    gs=gridspec.GridSpec(rows,columns)
    fig = plt.figure(figsize=(10*columns,10*rows))

    ax1 = fig.add_subplot(gs[:])  #scatter plot of particles

    plot_pins(ax1,size=disk_size)
    #create a simple figure
    #fig, ax = plt.subplots()

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------
    Sx=[0,60.0]
    Sy=[0,60.0]
    dt=0.002

    datafile_prefix = "velocity_data/XV_data_t="

    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.set_ylim(0,Sy[1])
    ax1.set_xlim(0,Sx[1])
    num_ticks=6
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(num_ticks))
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(num_ticks))

    if 1:
        starttime=40000020 #40000000
    else:
        starttime=4500000

    time_inc=30   #increment to count by
    maxtime=starttime + 30000 #maximum frame to read     
    init_file=datafile_prefix+"%08d"%(starttime)

    if get_data:    
        particle_data = di.get_data(init_file,7,sep=" ")
    else:
        binary_file = "%s%s"%(init_file,".npy")
        particle_data = np.load(binary_file)
        
    id   = particle_data[0]  #NOT USED
    type = particle_data[1]  #1 OR 2, SETS SIZE, FIXED FOR ANIMATION
    xp   = particle_data[2]  #DYMAMICALLY UPDATED POSITIONS
    yp   = particle_data[3]

    #DON'T BOTHER WITH THESE PARAMETERS
    #vx    = particle_data[4]
    #vy    = particle_data[5]
    #speed = particle_data[6]

    if get_data:
        np.save(init_file,particle_data)

    #RESIZE PARTICLES BASED ON TYPE    
    #not efficient - python can do this much faster
    #than this c-like array
    #since we only do this once, that is fine.  multiple times?  fix!
    size  = np.zeros(len(type))
    for k in range(len(type)):
        if type[k]==2:
            size[k]=disk_size
        else:
            size[k]=disk_size*(radius_ratio**2) #size = scale*radius^2, i.e. area, not radius
            

    #make a two color map 
    mycmap = colors.ListedColormap(['cornflowerblue', 'red'])
    
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap)

    #------------------------------------------------------------------------
    #add an annotation
    #note: "force" was for a different system, here time is relevant
    #------------------------------------------------------------------------
    force_template = r'time = %d'
    force_text = ax1.text(0.4, 1.01, '', transform=ax1.transAxes)

    #------------------------------------------------------------------------
    #finally animate everything
    #------------------------------------------------------------------------   

    
    ani = animation.FuncAnimation(fig, 
                                   animate, range(starttime,maxtime,time_inc), 
                                   fargs=(scatter1,
                                          datafile_prefix,
                                          force_template,
                                          force_text),
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
        
    exit()
