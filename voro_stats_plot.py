#!/usr/bin/env python3

'''
Danielle McDermott
April 14, 2016  
updated July 2, 2018
Python 3

The is reasonably fast because it is based on Qhull,
which is written in C

excellent reference for the scipy library
http://docs.scipy.org/doc/scipy/reference/tutorial/spatial.html

Code is not perfect,
but the bones are there, and now it is refinement

Use the scipy library to make a Voronoi Tessellation
of a 2D system of particles with periodic boundary conditions
-make plots of individual frames
-analyze statistics of the percentages of cells based on side number.
-where are the stats printed?

BE CAREFUL WITH THE max_area PARAMETERS
'''

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.path import Path
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.spatial.distance import pdist, squareform

import numpy as np

#libraries developed by DM
#import classColloid.plotColloid as plotColloid //OLD
import colloid_plot_library as cpl
import data_importerDM as di
import smart_file_reader as sfr #shannon's hash function

#to work with files, call sys.exit(), etc
import sys, getopt


#########################################################
#color code for Voronoi faces
#########################################################
#this will map to Voronoi cell coloring by 
#the number of sides the particular cell has
#4=blue, 5-lightblue, etc with a linear shift in 

colors = ['cornflowerblue','skyblue','lightgray','red'] 
plt.rc('font',size=22)
###############################################################


################################################################
def get_command_args(argv):

   ############################################################
   #hardwire some parameters here (conveniently top of file)
   ############################################################
   verbose = False
   inputfile = "Pa0"
   data_type = 0  #smtest is fastest (0 is preferable)
   starttime=int(1E6) #1000000 #
   disk_size=5
   
   #the following are hardwired for now, for time
   shift = False 

   #############################################################
   #put all of the flags in a string for a rudimentary help menu
   ############################################################
   information_string='plotVoronoi.py -i <inputfile Pa0>  -d <data_type 0/1/2> -s <disk_size int>  -t <starttime int> -v/--verbose'

   ####################################
   #optionally change parameters here
   ####################################
   try:
      opts, args = getopt.getopt(argv,"hi:d:s:t:v:",["inputfile=","outputfile=","movie_type=","data_type=","zoom=","disk_size=","starttime=","verbose="])
   except getopt.GetoptError:
      print(information_string)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print(information_string)
         sys.exit()
      elif opt in ("-o", "--outputfile"):
         outputfile = str(arg)
      elif opt in ("-d", "--data_type"):
         data_type = int(arg)
      elif opt in ("-t", "--starttime"):
         starttime = int(arg)
      elif opt in ("-s", "--disk_size"):
         disk_size = int(arg) #although could be a float in principle
      elif opt in ("-v","--verbose"):
         verbose = arg

   parameters = [inputfile,data_type,
                 disk_size,starttime,
                 verbose,shift]
      
   #wrap into a hash instead?
   return parameters

#########################################################
#implementation of shoelace method
#########################################################
def PolygonArea(corners):
    '''
    The shoelace method is a way to find the area of a polygon
    given its vertices.   
    This specifically takes all of the space contained within the 
    vertices and eliminates problems with the order 
    the vertices are considered.

    http://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
    https://en.wikipedia.org/wiki/Shoelace_formula

    required argument(s)
    corners = a list of [xi,yi] coordinates (vor.vertices[i])
    '''
    n = len(corners) # of corners 
    area = 0.0       #initialize the area as zero, we will +=

    #loop through all of the vertices/corners
    for i in range(n):
        
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
        
    area = abs(area) / 2.0
    return area

########################################################
#calculate an approximate average area using a histogram
########################################################
def calc_max_area(vor):
    '''
    this is a hack that works at some densities/clustering systems 
    to find voronoi cells that are simply too big to include 
    in voronoi statistics because they are actually part of 
    the systems edge

    calculate an approximate average area using a histogram
    could do this while looping over the cells to keep
    for efficiency sake

    required arguments
    vor: voronoi tessellation data structure generated by scipy
    '''

    num_cells=len(vor.regions)
    area_to_histogram=np.zeros(num_cells)
    
    #for q,region in zip(range(num_cells),vor.regions):
    for q,index in zip(range(num_cells),vor.point_region):

        region=vor.regions[index]
        if not -1 in region:
            
            polygon = [vor.vertices[i] for i in region]
                
            if len(polygon) > 3 and len(polygon) < 8: 
                    
                area_to_histogram[q]=PolygonArea(polygon)

    #area_to_histogram is an array that contains a list 
    #of all voronoi cells in the entire system
    #we need to find the mode and set the max area just above that

    freq,bins=np.histogram(area_to_histogram,bins=np.arange(200))
    
    #find the area that most of the particles sit within
    if 0:
        print( freq )
        print( bins )
        exit()

    #estimate where to cut off using the freq of areas - 80%?

    number_zero_freq=0
    total_cells=0
    for i in range(len(bins)):

        total_cells+=freq[i]

        if freq[i]==0:
            number_zero_freq+=1


        if number_zero_freq==4 or i==10:
            break


    max_area=bins[i]

    print("The number of cells in the tessellation is: ", num_cells)

    return max_area

###############################################################
###############################################################
###############################################################
def voronoi_statistics(vor,max_area=None,periodic=False,SX=None,SY=None,
                       distance_cut=None):
    '''
    given the scipy voronoi tessellation and data structures,
    loop through the values, and count the pN statistics
    '''

    #numpy array meant to hold the integer number of particles
    #containing 4 sides, 5 sides, 6 sides, and 7 sides
    pN=np.zeros(4)
    pcenter=0   #total cells with area < max_area, these are "center"
    pedge=0     #


    #count based on side number
    #for region in vor.regions:
    
    for index in vor.point_region:
        region=vor.regions[index]

        if not -1 in region:

            #################################################
            #polygon = a series of points outlining a polygon
            #which surrounds a particle (colloid etc)
            #structure is an array of pairs of points
            #polygon=[[x1,y1],[x2,y2],etc]
            #################################################
            polygon = [vor.vertices[i] for i in region]

            #################################################
            #number of sides of this poly which 
            #are simply too short to be considered "real"
            #for statistics and drawing
            #################################################
            short_side=0 

            #our polygon needs a set number of faces to be counted
            if len(polygon) > 3 and len(polygon) < 8: 

                if distance_cut:
                    #perform a cut on len(polygon)
                    #based small vertex/ridge lengths

                    d = squareform(pdist(polygon, 'euclidean'))
                    all_distances = d.flatten()

                    for distance in all_distances:
                        if distance > 0.0 and distance < (SX/240.0):
                            '''
                            opportunity to normalize by total length
                            and throw out the distances that 
                            are a small small percentage of that total
                            '''
                            #print distance
                            short_side+=1

                            #print short_side
                            #all_distance is length N^2, so divide short_side
                        short_side /= 2

                        '''end new chunk of code
                        '''
                else:
                    short_side=0

                #if we're restricing area, check the polygon is the right size
                if (max_area and PolygonArea(polygon) < max_area):

                    pN[len(polygon)-4-short_side]+=1
                    pcenter+=1
                
                elif max_area==None:

                    #otherwise count the particle no matter what
                    pN[len(polygon)-4]+=1
                    pcenter+=1

            else:
                pedge+=1


    return (pN, pcenter, pedge)

###############################################################
def calc_voronoi_tessellation(x_p,y_p, #max_area=1.5,
                              periodic=False,SX=None,SY=None,
                              distance_cut=None):
    '''
    Use the scipy library on the given numpy arrays for 
    the positions of the particles

    x_p:      numpy array containing all x-positions of particles
    y_p:      numpy array containing all y-positions of particles

    #not used, not appropriate in original tessellation
    #max_area: a hack method to eliminate coloring in 
    #          edges when the particles are in clumps

    periodic: boolean to determine whether to consider PBC
    SX:       system size, in x, necessary for PBC
    SY:       system size, in y, necessary for PBC
    '''

    if periodic:
        if SX==None or SY==None:
            print("Can't make periodic Voronoi diagram without these.")
            return

        #total number of particles in the system
        n=len(x_p)

        #new numpy array to hold the 
        #periodic repeats + original system
        tiled_x_p = np.zeros(n*9)
        tiled_y_p = np.zeros(n*9)

        #loop through the neighboring tiles
        for i,shiftx in enumerate([-1.0, 0.0, 1.0]):
            for j,shifty in enumerate([-1.0, 0.0, 1.0]):
                #nifty numpy array math for 
                #creating the periodic repeats
                tiled_x_p[(i+j*3)*n:(i+j*3+1)*n] = x_p + shiftx*SX
                tiled_y_p[(i+j*3)*n:(i+j*3+1)*n] = y_p + shifty*SY

        ##########################################################
        #combine the x and y arrays into a single data structure
        #for the voronoi tessellation.
        ##########################################################
        np_points = np.column_stack((tiled_x_p,tiled_y_p))

    ##########################################################
    #else = NOT doing PBC, still need to
    #put the x and y data into 
    #a single np.array for voronoi analysis
    #########################################################
    else:
        np_points = np.column_stack((x_p,y_p))

    #########################################################
    #do Voronoi analysis using scipy algorithm, 
    #which calls qhull... I think
    #
    vor = Voronoi(np_points)
    #########################################################

    #########################################################
    #now we ruthlessly delete the tiled particles
    #so we don't include them in analysis
    #########################################################
    if periodic:        

        #want to delete the particles in the 8 additional tiles
        points_to_delete=np.zeros(8*n)
        j=0

        #identify i values of particles NOT in the original box
        for i,point in zip(range(len(vor.points)),vor.points):

            #surely there is a more efficient way to 
            #measure if particle NOT in box,
            #but I don't know what that is.
            if point[0]>SX or point[0]<0.0 or point[1]<0.0 or point[1]>SY:
                points_to_delete[j]=i
                j+=1

        ###########################################################
        #check that all of the particles to be remove were counted
        #if this fails, it is game over
        ###########################################################
        if j!=8*n:
            print("Somehow didn't find all of the extra particles")
            sys.exit()
        else:

            count=0
            ###########################################################
            #this is how I learned about these data structures
            #don't delete
            ###########################################################
            '''
            for array in [vor.points,
                          vor.vertices,
                          vor.ridge_points,
                          vor.regions,
                          vor.point_region]:
                print("count=",count)
                print len(array)
                print array
                count+=1
            '''
            ###########################################################
            #helpful data structure learning tool
            #don't delete
            ###########################################################
            '''
            for data_point in vor.point_region:
                print vor.points[data_point-1]
            '''
            ###########################################################
            #delete the graft from the two arrays that count by points
            ###########################################################
            vor.points     =np.delete(vor.points,      points_to_delete,0)
            vor.point_region=np.delete(vor.point_region,points_to_delete,0)

            #everybody else is too full,
            #and needs to get trimmed 
            #regions gets trimmed by point_region
            #not yet sure about the rest


    return vor

###################################################################
###################################################################
###################################################################
###################################################################
def plot_voronoi_tessellation(ax,vor,x_p,y_p,
                              max_area=100000.0,  #set high
                              periodic=False,
                              SX=None,SY=None,plotEdges=False,
                              distance_cut=None):

    #########################################################
    #plot the ridges fully surrounding particles
    #where ridges are the lines (check this)
    #and ridge_vertices are the points where lines adjoin (makes sense)
    #these data structures are nasty, 
    #there is a reason there are so many print statements.  keep these.
    #########################################################
    for simplex in vor.ridge_vertices:
        simplex = np.asarray(simplex)
        #length_simplex=np.sqrt()
        if np.all(simplex >= 0):
            #print simplex
            #print vor.vertices[simplex, 0]
            #print vor.vertices[simplex, 1]
            #exit()

            ax.plot(vor.vertices[simplex, 0], vor.vertices[simplex, 1], 'k-')

    ##################################################################
    #color by area
    ##################################################################
    '''
    http://stackoverflow.com/questions/20515554/colorize-voronoi-diagram
    '''
    # colorize
    #for region in vor.regions:
    for index in vor.point_region:
        region=vor.regions[index]
        if not -1 in region:
            short_side=0
            polygon = [vor.vertices[i] for i in region]

            if len(polygon) > 3 and len(polygon) < 8: 

                if PolygonArea(polygon) < max_area:

                    if distance_cut:
                        #TODO July 6th
                        ##################################################
                        #check length of each ridge (or vertex?) here.
                        #if vertex is too small, say length Sx/100 = 0.36
                        #subtract a value from fc1
                        ##################################################
                        d = squareform(pdist(polygon, 'euclidean'))
                        all_distances = d.flatten()
                    
                        for distance in all_distances:
                            if distance > 0.0 and distance < (SX/240.0):
                                #print distance, len(polygon), short_side
            
                                short_side+=1

                        #all_distance is length N^2, so divide short_side
                        short_side /= 2

                    else:
                        short_side=0
                    try:
                        fc1 = colors[len(polygon)-4-short_side]
                        ax.fill(*zip(*polygon),facecolor=fc1,alpha=1.0)
                    except:
                        print(len(polygon), fc1)
                        


    ##################################################################
    #plot the ridges which leave the page
    #this is dense code, apologies
    #it is supposed to make a dashed line heading off to infinity
    #you don't see this when you do PBC
    #and it doesn't work that well otherwise... sigh... 
    ##################################################################
    if plotEdges:
        #find the mean of each column in x_p,y_p of np_points
        center = np_points.mean(axis=0)
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0] # finite end Voronoi vertex
                t = np_points[pointidx[1]] - np_points[pointidx[0]]  # tangent
                t = t / np.linalg.norm(t)
                n = np.array([-t[1], t[0]]) # normal
                
                #what is this?
                midpoint = np_points[pointidx].mean(axis=0)
                far_point = vor.vertices[i] + np.sign(np.dot(midpoint - center, n)) * n * 100
                ax.plot([vor.vertices[i,0], far_point[0]],
                        [vor.vertices[i,1], far_point[1]], 'k--')


    return

################################################################
def make_plot(Sx,Sy,vor_data,xp,yp,disk_size=5,time=None):
    '''
    given the basic inputs and data, make the Voronoi tessellation plot

    Parameters
    ----------
    Sx : float
        size of the box - horizontal

    Sy : float
        size of the box - vertical

    vor_data : voronoi tessellation data structure generated by scipy library Voronoi()
        contains cell and line data for tessellation

    xp: numpy array float
        all disk x-positions in single array

    yp numpy array float
        all disk y-positions in single array
    
    '''

    #size to plot vortices/colloids
    #hard coded by what "looks good"
    size=disk_size
    
    if time is None:
        out_file="voronoi_tessellation.pdf"
    elif isinstance(time, int):
        out_file="voronoi_%d.pdf"%(time)

    #add a label such as (a)
    label = False
    
    #---------------------------
    #set up a 1x1 plot in a subroutine
    #---------------------------
    fig,ax1 = cpl.format_plot(Sx=Sx,Sy=Sy)

    #---------------------------
    #plot the pinning array
    #---------------------------
    cpl.plot_pins(ax1,size=size)

    #plot it! be careful with max_area
    plot_voronoi_tessellation(ax1,vor_data,xp,yp,max_area=2.0)
    ########################################################

    #add the particles on top of the tessellation
    ax1.scatter(xp,yp,s=size,zorder=10,facecolor='k')
    ax1.set_xlim(*Sx)
    ax1.set_ylim(*Sy)
    
    if label:
        xt=0.05
        yt=0.9
        ax1.text(xt,yt,label,transform = ax1.transAxes)
    #plt.axes().set_aspect('equal')
    #ax.set_aspect_ratio

    fig.tight_layout() #pad=0.0)
    plt.savefig(out_file)
    
################################################################
if __name__ == "__main__":

    (inputfile,data_type,disk_size,starttime,verbose,shift) = get_command_args(sys.argv[1:])

    if verbose == True:
        cpl.print_dt(data_type)

    #--------------------------------------------------------------
    #get data for initial frame, 
    #---------------------------------------------------------------

    #(Sx, Sy, radius, maxtime, writemovietime )
    #the smart_file_reader returns a hash, and we unpack the values
    parameter_data = sfr.get_input_data(inputfile)
    SX = parameter_data['SX']  #as called in file
    SY = parameter_data['SX']
    radius = parameter_data['radius']
    maxtime = parameter_data['maxtime']
    writemovietime = parameter_data['writemovietime']

    #box dimensions
    Sx = [0.0,SX]
    Sy = [0.0,SY]

    #########################################
    #open datafile
    #########################################
    f = open("voro_stat.dat",'w')
    
    #---------------------------
    #get and parse data
    #---------------------------
    datafile_prefix = "velocity_data/XV_data_t="

    time_array = np.arange(starttime,maxtime,writemovietime)

    for time in time_array:
        if verbose == True:
           print(time)
           
        #if data_type == 0 , this will process all of smtest
        id,type,xp,yp = cpl.get_and_parse_data(data_type,
                                           time,
                                           movie_type="cmovie")
    
        ########################################################
        #a method to center particles,  not needed here - use shift to put back in
        if shift == True:
            #obviously this will differ by system, shift factor?  x? y?
            x_p=np.add(x_p,SX/4.0)
        ########################################################

        ########################################################
        #calculate the tessellation using scipy
        vor_data=calc_voronoi_tessellation(xp,yp)

        #run through the data structure, accumulate information about the cells
        #max_area=None (default) - be careful with this, 
        pN, pcenter, pedge =  voronoi_statistics(vor_data)

        #normalize pN
        pN/=pcenter
    
        f.write("%d %f %f %f %f %f\n"%(time,pN[0],pN[1],pN[2],pN[3],pedge/(pcenter+pedge)))
    
    #########################################
    #close datafile
    #########################################
    f.close()

    if 0:
        make_plot(Sx,Sy,vor_data,xp,yp,disk_size=disk_size,time=starttime)
    
    sys.exit()
    
######################################################################
###############################################################
