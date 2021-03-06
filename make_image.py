#!/usr/bin/env python

"""
Make a png/pdf of a single frame.
"""

import matplotlib
matplotlib.use('Agg')   #for batch jobs!!!

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
#from matplotlib import cm
import matplotlib.ticker as ticker

import sys, getopt

#functions written by D.M. to get and plot specific data files
import data_importerDM as di
import colloid_plot_library as cpl

plt.rc('font', size=20)

################################################################
################################################################
def get_command_args(argv):
   plottime = ''
   file_output_type = ".pdf"
   try:
      opts, args = getopt.getopt(argv,"ht:f:",["time=","file="])
   except getopt.GetoptError:
      print('make_image.py -t <plottime> -f <file_output_type>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('make_image.py -t <plottime> -f <file_output_type>')
         sys.exit()
      elif opt in ("-t", "--time"):
         plottime = int(arg)
      elif opt in ("-f", "--file"):
         outputfile = arg

   return plottime, file_output_type

################################################################
################################################################

    
if __name__ == "__main__":


    try:
       plot_time, file_output_type = get_command_args(sys.argv[1:])
    except:
       plot_time=9
    print("plotting system at time: ", plot_time)
    print("file output type: ", file_output_type)
    
    verbose = 1
    get_ascii_data = 1
    #---------------------------
    #system specific variables
    #---------------------------

    Sx=[0,60.0]
    Sy=[0,60.0]

    scale = 1
    disk_size=15*scale
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------
    fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sx,rows=scale,columns=scale)

    #------------------------------------------------------------------------
    #get data for initial frame, 
    #------------------------------------------------------------------------   
    datafile_prefix = "velocity_data/XV_data_t="
    plot_file=datafile_prefix+"%08d"%(plot_time)

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
        if type[k]==2:
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

    #------------------------------------------------------------------------
    # (turned off) add an annotation
    # note: "force" was for a different system, here time is relevant
    #------------------------------------------------------------------------
    if 0:
        force_template = r'$F_D/F_p = %1.2f$'
        #force_template = r'time = %d'        
        force_text = ax1.text(0.5, 1.05, '', ha='center',
                              transform=ax1.transAxes,fontsize=22)

    out_name="scatter_figure"+file_output_type
    
    fig.savefig(out_name)
        
    sys.exit()
