#!/usr/bin/env python

"""
A simple example of an animated plot
SOURCE: http://matplotlib.org/examples/animation/simple_anim.html
#to make a gif:
https://eli.thegreenplace.net/2016/drawing-animated-gifs-with-matplotlib/

movie_type 
"simple"        # one panel standard, single window
"animate"       # two panels, side by side, phase diagram
"animate_fd_v0" # two panels, side by side, Force-Velocity diagram

Data files format
smtest (single binary), ascii (velocity_data/XV...integer), binary (*npy)
[0="smtest", 1="ascii", 2="npy style binary"]
"""

#numeric and basic plotting libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

#for multiplots (not used, but could be)
#import matplotlib.gridspec as gridspec

#for axes labels (not used, but could be)
#import matplotlib.ticker as ticker

#Not used (was used for contour plot to make background colors)
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib.colors import LightSource, Normalize
from matplotlib import cm

#to animate, obviously
import matplotlib.animation as animation

#to work with files, call sys.exit(), etc
import sys, getopt

#--------------------------------------------------
#functions written by D.M.
#to get and plot specific data files
import colloid_plot_library as cpl
#read in Pa0 or Pcw0 with a dict/hash construct
import smart_file_reader as sfr

plt.rc('font', size=20)

      
################################################################
def get_command_args(argv):

   ############################################################
   #hardwire some parameters here (conveniently top of file)
   ############################################################
   outputfile="Supp1.mp4"
   inputfile = "Pcw0"
   movie_type = "simple"
   data_type = 0  #smtest is fastest (0 is preferable)
   zoom=True

   #hard coded by what "looks good" basically a ratio of system size
   #and fig size to make the particles look the size
   #of their interaction length -
   #this is tricky with this system since they don't have a well defined size.
   disk_size=200
   
   starttime=0 #int(3*10000/4.0)
   corr = True #False
   image_test = True
   image_test_name = "test.png"
   verbose = False
   #the following are hardwired for now, for time
   shift = False 
   n_corr=20.0 #number of troughs in the corrugations

   #############################################################
   #put all of the flags in a string for a rudimentary help menu
   ############################################################
   information_string='channel_colloid_movie_maker.py -i <inputfile Pcw0> -o <outputfile string.mp4> -m <movie_type string>  -d <data_type 0/1/2> -z <zoom 0/1>  -s <disk_size int>  -t <starttime int> -c <corrugation 0/1> --image --image_name -v/--verbose'

   ####################################
   #optionally change parameters here
   ####################################
   try:
      opts, args = getopt.getopt(argv,"hi:o:m:d:z:s:t:c:v:",["inputfile=","outputfile=","movie_type=","data_type=","zoom=","disk_size=","starttime=","corr=","image=","image_name=","verbose="])
   except getopt.GetoptError:
      print(information_string)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(information_string)
         sys.exit()
      elif opt in ("-i", "--inputfile"):
         plottime = str(arg)
      elif opt in ("-o", "--outputfile"):
         outputfile = str(arg)
         
      elif opt in ("-m", "--movie_type"):
         movie_type = str(arg)

         #ADD ERROR CHECKING
         if movie_type not in ("simple","animate","animate_fd_v0"):
            print("can't process movie_type %s"%(movie_type))
            print("options are '%s' '%s' '%s'"%("simple","animated","animated_fd_vy"))
            sys.exit()
            
      elif opt in ("-d", "--data_type"):
         data_type = int(arg)
      elif opt in ("-z", "--zoom"):
         zoom = bool(int(arg))
      elif opt in ("-s", "--disk_size"):
         disk_size = int(arg) #although could be a float in principle
      elif opt in ("-t", "--starttime"):
         starttime = int(arg)
      elif opt in ("-c", "--corr"):
         corr = bool(int(arg))
      elif opt in ("--image"):
         image_test = bool(int(arg))
      elif opt in ("--image_name"):
         image_test_name = arg
      elif opt in ("-v","--verbose"):
         verbose = arg

   parameters = [outputfile,inputfile,movie_type,data_type,
                 zoom,disk_size,starttime,corr,image_test,
                 image_test_name,verbose,shift,n_corr]
      
      
   #wrap into a hash instead?
   return parameters

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
    Adds the washboard in the y-direction.  
    Hardwired for a single parameter set.    
    '''

    a_p = L/N

    #assuming Tiare's trough system, so we won't want to cover the entire range
    X = np.arange(0, L/2.0, 0.1)
    Y = np.arange(0, L, 0.1)
    X, Y = np.meshgrid(X, Y)

    Z_mag = 2.0 # set by what "looks good"
    Z = Z_mag*np.sin(2*np.pi*X/L)
    if corrugated == True:
        Z += np.sin(2*np.pi*Y/a_p) 

    cmap=cm.coolwarm_r

    #alphs is the degree of transparency, again, set by what looks good.
    cset = ax.contourf(X, Y, Z, cmap=cmap,alpha=0.25)

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
def vertical_shift(yp,SY=36.5,percent_shift=0.25):
    '''
    if the interesting action is happening too low,
    shift the entire data set up/down
    note that we're hardwiring the system size and the degree of the shift
    so this also needs to be rewritten

    required arguments:
    yp: (type numpy array) data that needs to be moved, nominally y-positions of particles 

    optional arguments: 
    SY: (type floating point scalar) system size in shift direction
    percent_shift: (type floating point scalar) amount of SY to shift by, 
                       may be positive/negative
    '''
    shift = SY*percent_shift
        
    for m in range(len(yp)):
        if yp[m] > shift:
            yp[m] -= shift #shift everyone at the top 3/4 down
        else:
            yp[m] += (1-shift) #move the bottom 1/4 up to the top 1/4
            
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

    if extra_args != None:
        shift = extra_args[3]
        drop = extra_args[4]
        curr_inc = extra_args[5]
        verbose = extra_args[6]
        decifactor=extra_args[7]
        
        if shift == True:
           #hardwired parameters
           vertical_shift(yp)

    '''
    #if you need to change the particle sizes with time
    #for instance if your system is under compression
    #this is the format of the array and the manner
    #to update a size array
    if i>1000000:
        new_sizes = np.array([50 - i/1000000.0]*len(xp))
        scatter1.set_sizes(new_sizes)
    '''

    #specially formatted array to update positions in scatter plot
    #format is in pairs [x1,y1], [x2,y2], etc
    data = np.hstack((xp[:i,np.newaxis], yp[:i, np.newaxis]))
    #data = np.hstack((xp[:i,0], yp[:i,0]))

    #update the scatter plot created in the main function with the new data
    scatter1.set_offsets(data)
    
    #if you're changing the color
    #color_array = np.array(something)
    #scatter1.set_array(color_array)


    #The driving force is calculating assuming you are
    #ramping it up as in the MD code (by the curr_inc every drop steps)
    fd = (i//drop)*curr_inc 
    if force_template:
        force_text.set_text(force_template%(fd))
    

    if verbose == True and (i%decifactor==0):
        print("plotting frame: %d"%(i))

        
    #TODO: this i%100==0 is hardcoded, find/fix
    if extra_args != None and (i%decifactor==0):
        
        #unpack the extra_args - these are user defined by function
        scatter2 = extra_args[0]

        #independent variable 1
        #time = extra_args[1]  #or phi_y or fd

        #dependent variable 2
        #y0 = extra_args[2]

        #TODO: this i%100==0 is hardcoded, find/fix
        time_int = int(i/10000)
        #print(time_int)
        

        try:
            #To be general, I'm not naming extra_args[1] and [2]
            #they are the independent and dependent variables of the plot
            #to change the "bouncing ball" (magenta circle)
            #give the .set_offsets() method a
            #carefully formatted data point (x,y)
            #so the bouncing ball is plotted at this integer time

            data_new = [extra_args[1][time_int],extra_args[2][time_int]]

            #update the bouncing ball point location
            scatter2.set_offsets(data_new)
        except:
            print("data_new doesn't exist",i,time_int)

        #update the text label for the new FORCE (fd)
        #this is for the "animate: modes
        if force_template:
            force_text.set_text(force_template%(fd))
            return force_text,scatter1,scatter2
        else:
            return scatter1,scatter2
            
    #"simple" mode
    #update the text label for the new time
    if force_template:
        return force_text,scatter1
    else:
        return scatter1

################################################################
################################################################
################################################################

if __name__ == "__main__":

    #obviously the following is a mess, but makes for easier use.  TODO - clean up.
    (outputfile,inputfile,movie_type,data_type,zoom,disk_size,starttime,corr,image_test,image_test_name,verbose,shift,n_corr) = get_command_args(sys.argv[1:])

    if verbose == True:
        print_dt(data_type)
        print("Getting system size and times from %s",inputfile)

    #get the data from Pcw0 - hardwired for a certain format
    #this could be improved - with a has for instance
    parameters_MD_dict = sfr.get_input_data(inputfile)
    Sx=parameters_MD_dict['SX']
    #print(Sx)
    Sy=parameters_MD_dict['SY']
    radius=parameters_MD_dict['radius']
    maxtime=parameters_MD_dict['maxtime']
    writemovietime=parameters_MD_dict['writemovietime']
    drop=parameters_MD_dict['drop']
    dc_curr_incr=parameters_MD_dict['dc_curr_incr']
    dt=parameters_MD_dict['dt']
    decifactor=parameters_MD_dict['decifactor']
    
    #This is to zoom in along the x-axis
    #and cut some of the blank space, could tweak the aspect ratio more

    #zoom=True
    if zoom == True:
        Sx=Sx/2.0
    

    #######################################################################
    #times - may adjust if your initial sampling was too many / too long
    #######################################################################
    #starttime (command line args) 
    time_inc=writemovietime     #make larger if the movie is too detailed
    maxtime=maxtime - time_inc  #make lesser if the movie is too long
    
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------

    if movie_type == "simple":
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
    #plot the energy landscape- it would never be pins in channel system
    #---------------------------
    if 0:
        #pinning array 
        cpl.plot_pins(ax1,size=disk_size)
    else:
        #use a contour plot to show the landscape,
        #corr = True/False turns off/on the corrugations in the plot

        add_contour(ax1,Sy,n_corr,corrugated = corr)

    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="
    id,type,xp,yp = cpl.get_and_parse_data(data_type,
                                           starttime,
                                           movie_type="smovie")

    #the following code may be used
    #if the interesting behavior is happening too high/low on the
    #screen, so the interesting behavior is obscured by the pbc.
    #when you shift the particle positions, you have to account for the pbc.
    #note that this is NOT a pythonic way to do this, so it is probably inefficient

    if shift == True:
        vertical_shift(yp)
    
    #--------------------------------------------
    #COLOR THE PARTICLES
    #---------------------------------------------
    #the plot needs to know what size to make each particle
    #make all particles the same size
    size = disk_size*np.ones(len(type))

    #color the driven particle differently than non-driven
    type[0] = 2
        
    if movie_type == "simple":
        #make a two color map given types 1,2
        mycmap = colors.ListedColormap(['mediumseagreen','coral'])
    else:
        #this colors a particle bright pink to make it obvious
        mycmap = colors.ListedColormap(['magenta'])

    #----------------------------------------------
    #plot the particles
    #----------------------------------------------
    scatter1=ax1.scatter(xp,yp,c=type,s=size,cmap=mycmap,edgecolor='k')

    
    if movie_type != "simple":
        #get the data to make either the phase plot or the vy vs. fd plot.  mainly hardwired.

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

            #TODO, modify the cpl to get these params
            #drop = 4000.0  #this is from Pcw0 as well, but we would need cpl to return it...
            #curr_inc = 0.001
            fd = time*dc_curr_inc/drop

            #plot the entire data set
            ax2.plot(fd,fy0,"o--") 

            #plot the "bouncing ball" that will be updated to move with the animation
            scatter2=ax2.scatter(fd[0],fy0[0],
                                 marker="o",s=100,c="magenta",zorder=9)

            ax2.set_xlabel(r"$F_{Drive}$")
            ax2.set_ylabel(r"$\bar{v}_y$")
        
        elif movie_type == "animate":

            #phase calculations - TBD how to do this for our system
            #if DC is zero (or small), then subtracting off the (mean force)*time
            #actually creates a helix.
            #what is going on, and how can we fix it.

            #TODO: another hardwired value to fix
            phi_y =  2*np.pi*(y0 - np.mean(fy0)*time*dt - y0[0])
            dphi_y = 2*np.pi*(fy0-np.mean(fy0))
            
            ax2.scatter(phi_y,dphi_y) #,"o--") #,c=type,s=size,cmap=mycmap)

            #TODO document this plot_time
            #seriously, I actually don't understand it
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
    if movie_type == "simple":
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
    #the arguments sent to to the animate subroutine change by movie style
    #not that I used a new animate_with_phase() routine to deal with the side-by-side
    #-----------------------------------------------------------------

    #single frame/1x1 plot
    if movie_type == "simple":
        #this is from the general library
        function=cpl.animate
        fargs=(scatter1,
               datafile_prefix,
               force_template,
               force_text,
               data_type,None)
        
    elif "animate" in movie_type:
       #multiframe/1x2 plot
       #note this is locally defined,
       #a distinct function from it's 'parent' cpl.animate()
       function=animate_with_phase
       
       if movie_type == "animate":
          #phase diagram, as in animate
          extra_args=[scatter2,phi_y,dphi_y] #partial list, will add to this
          
       elif movie_type == "animate_fd_v0":
          extra_args=[scatter2,fd,fy0]
       elif movie_type == "not yet coded":
          extra_args=[scatter2,time,y0]
      
       #the extra args above are unique to the plot type,
       #both functions benefit from these variables
       extra_args+=[shift,drop,dc_curr_incr,verbose,decifactor]
         
       fargs=(scatter1, datafile_prefix, force_template, force_text,
              data_type,extra_args)   
            
            
       #following should resize system and pad, but with 1x1 grid
       #causes function to error
       #if movie_type != "simple":
       fig.tight_layout() #h_pad=-0.5,w_pad=1.0,pad=0.5)

       
    #fig.tight_layout() #h_pad=-0.5,w_pad=1.0,pad=0.5)
    ani = animation.FuncAnimation(fig, 
                                  function,
                                  range(starttime,maxtime,time_inc), 
                                  fargs=fargs,
                                  interval=20, blit=False)

        


    #option to look at a single frame that you set up for the animation
    if image_test == True:
        plt.savefig(image_test_name)
    
    elif movie_type == "simple" or "animate" in movie_type:

        #make a movie
        
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

