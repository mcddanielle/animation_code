import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from matplotlib import cm

import colloid_plot_library as cpl
import data_importerDM as di

import sys
import numpy as np
import matplotlib.colors as mpl_colors

#################################################################
#################################################################
def plot_ratchet_potential_2D(ax, L=36.0,Npins=24.0):
    '''makes a plot of a "ratchet" potential to show the 
    landscape an active particle moves through in this paper: 
    http://pubs.rsc.org/en/content/articlelanding/2016/sm/c6sm01394e/unauth#!divAbstract
    or the arXiv version (which isn't as clear)
    https://arxiv.org/abs/1604.01072

    required argument(s):
    ax - matplotlib axes object to place plot
    
    optional arguments:
    L=36.0 - system dimension 

    Npins = 24, where this is the number of troughs a particle can get stuck in
    so the period is L/Npins
    '''

    #scaling for trough height
    Fp = 1

    #plot range (doesn't have to be L)
    x_max = L

    #period of potential landscape
    a_p = L/Npins 

    #make a grid, closely spaced
    X = np.arange(0, x_max, 0.1)
    Y = np.arange(0, L, 0.5)
    X, Y = np.meshgrid(X, Y)

    #ratchet potential - see reference in docstring
    Z = Fp*(np.sin(2*np.pi*X/a_p) + 0.25*np.sin(4*np.pi*X/a_p))

    #choose a color maps
    if 0:
        cmap=cm.YlGn_r
    else:
        cmap=cm.coolwarm_r

    #plot it - see matplotlib for additional documentation and options
    #rasterize is important for making figures with clear
    #labels, but not too much data
    cset = ax.contourf(X, Y, Z, zdir='z',offset=-1, 
                       cmap=cmap,alpha=0.6,rasterized=True)

    return

################################################################
def histogram_velocities(ax,time,filename=None,path=""):
    '''currently written to combine the discrete velocities 
    from many files from 
    a data file such as linked below.  
    current versions of the code may instead generate a large file
    containing raw velocity values 
    written directly with c to bypass this step

    use at own risk
    '''
    
    tf=time
    delta_t=10
    t0= tf - delta_t*100


    for time in range(t0,tf,delta_t):


        if filename==None:
            filename ="velocity_data/XV_data_t=%05d"%(time)
            num_col=7
            n=2
        else:
            num_col=6
            n=1

        data_list = di.get_data(filename,num_col,sep=' ',path1=path)

        #x_p = data_list[n]
        #y_p = data_list[n+1]
        if time==t0:
            v_x=data_list[n+2]
        else:
            v_x_old = v_x
            v_x = np.concatenate((v_x,v_x_old),axis=0)
        #v_y = data_list[n+3]
        #speed   = data_list[n+4]

        '''
        print len(v_x)
        print v_x
    
        if time==t0+2*delta_t:
            exit()
        '''
    #hist, bin_edges = np.histogram(x_p)

    ax.hist(v_x,50)

    return
        

################################################################
def make_trails(ax,tf,delta_t=500,N=256,path1='',
                SX=36.0,SY=36.0,size=100,line=2,
                edgecolor='gray',facecolor='black',edgewidth=1.0,
                hardcode_figure=None,num_troughs=24.0):

    '''not called by the main function, 
    but now this is more adaptable for calling from 
    other functions... work on this

    modern version of the turtle - what do draw and where

    required arguments
    ax:      matplotlib axes object for subplot 

    tf:      the time of interest, we will do a scatter plot of this

    delta_t: range of timesteps to plot the particle trail 
             prior to the time of interest

             WARNING: no current contingency for small times, 
             where trails do not exist

    N:       number of particles in the simulation

    optional arguments
    SX = 36.0 system size in x
    SY = 36.0 system size in y
    size = 100 - disk size scaling
    line = 2 - width of trails to draw
    edgecolor = "gray"  - color of disk
    facecolor = "black" - color of trail line
    edgewidth = ?
    hardcode_figure = 1,11,etc - for the ratchet paper
    num_troughs = 24 - written for ratchet paper - unnecessary
    '''

    #vertices - where to draw things
    verts=[]
    #codes - directions on what to draw
    codes=[]

    #make a list of vertices and codes for every single particle
    #doesn't seem very efficient,
    #but it is a good manner for grouping by property of each particle
    for i in range(N):
        verts.append([])
        codes.append([])

    #back up 6 data files to make the trails
    #arbitrary hardcode that worked
    t0= tf - delta_t*6

    #array containing all starting positions of particles
    x0=None

    #loop through (hardcoded) 6 files
    #grab the data slightly differently depending on which version
    #of the code wrote the data files
    for time in range(t0,tf,delta_t):

        if hardcode_figure==1:
            filename ="velocity_data/XV_data_t=%05d"%(time)
            data_list = di.get_data(filename,7,sep=' ',path1=path1)
            n=2
        else:
            filename = "frame_data/velocity_frame%d"%(time)
            data_list = di.get_data(filename,6,sep=' ',path1=path1)
            n=1

        x_p = data_list[n]
        y_p = data_list[n+1]
        v_x = data_list[n+2]
        v_y = data_list[n+3]
        speed   = data_list[n+4]

        if x0==None:
            x0=x_p #initial positions

        ########################################################
        #if called, center everybody (assuming 1/4 system shift)
        ########################################################
        if 0:
            x_p=np.add(x_p,36.5/4.0)


        #if you shift, check periodic boundary conditions 
        if 0:
            for q in range(len(x_p)):
                if x_p[q] > 36.5:
                    x_p[q]-=36.5

        ########################################################
        #loop through each particle separately
        ########################################################
        for i in range(N):

            #for periodic boundary conditions
            #if restart is 0, connect to the previous location
            #if it is 1, we will have to jump to the other side
            restart=0
            
            if time > t0:
                #we are connecting locations in space to draw the trails
                #so we need the previous location
                x_old,y_old = verts[i][-1]

                #find the distance between
                dist_x = x_p[i]-x_old
                dist_y = y_p[i]-y_old

                #don't draw off the edge of the page
                if abs(dist_x) > SX/2.0 or abs(dist_y) > SY/2.0:
                    
                    #print dist_x,  x_p[i],x_old
                    #print dist_y,  y_p[i],y_old
                    
                    del(codes[i][-1])            #delete the connection
                    codes[i].append(Path.MOVETO) #wrap around instead

                    #codes[i].append(Path.END)

                    restart=1 #starting from a new point
                    
            #print(i, N)
            #add the new positions to the vertex list
            verts[i].append( [ x_p[i],y_p[i] ])
            
            #if we are at the initial time, don't have the pen down
            #just start at the vertex
            if time == t0 or restart==1:        
                codes[i].append(Path.MOVETO)
            
            elif time>t0 and time<tf:
                #keep the pen down and draw to the new spot
                codes[i].append(Path.LINETO)

            elif time == tf:
                #no more trail after the last timestep, so stop drawing
                print Path.END
                codes[i].append(Path.END)

    #now that we've collected all the data, plot it
    #hardcoded
    sysSX=36.0
    sysSY=36.0
    
    for i in range(N):

        #Measure the length of the path in components
        #particle i, from first position [0] to last [-1], x position [0]
        dx=abs(verts[i][0][0]-verts[i][-1][0]) 
        #particle i, from first position [0] to last [-1], y position [1]
        dy=abs(verts[i][0][1]-verts[i][-1][1])

        #periodic boundary conditions
        if dx>(sysSX/2.0):
            dx = abs(dx - sysSX)
        if dy>(sysSY/2.0):
            dy = abs(dy - sysSY)

        #measure the distance apart,
        #make sure it isn't too small - messy to draw
        distance = np.sqrt( dx**2 + dy**2 )
        
        #only draw if the path length is longer than this hardcoded value
        #particles oscillate in place, so this hides the "noise"
        #which is misleading, but avoids a messy figure
        if distance > 0.25:
            path = Path(verts[i], codes[i])
            patch = patches.PathPatch(path, facecolor='none', edgecolor='black', lw=line,antialiased=True)
            #,rasterized=True)

            #this is where the trails get added to the figure
            ax.add_patch(patch)

    #now we plot the particles 
    #get the data AGAIN!  slow!
    if hardcode_figure==1:
        filename ="velocity_data/XV_data_t=%05d"%(tf)
        data_list = di.get_data(filename,7,sep=' ',path1=path1)
        n=2
    else:
        filename = "frame_data/velocity_frame%d"%(time)
        data_list = di.get_data(filename,6,sep=' ',path1=path1)
        n=1
        
    x_p = data_list[n]
    y_p = data_list[n+1]
    v_x = data_list[n+2]
    v_y = data_list[n+3]
    speed   = data_list[n+4]

    #for a ratchet paper, it is important to know
    #if the particles make progress in the x-direction
    #so there is an unusual coloring scheme,
    #red (1), blue (-1), gray (0), to note
    #forward, backward, neither
    
    delta_x=x_p-x0 #total difference moved over the plotted frame
    colors=np.zeros(N) #array containing a zero for every particle
    
    #print len(colors), len(delta_x)
    
    if 1:
        #choose colors as described above
        for i in range(len(delta_x)):
            period=0.26*SX/num_troughs  #hardcode!
            if delta_x[i] <=-period:
                colors[i]=-1
            elif delta_x[i]>=period:
                colors[i]=1

    elif hardcode_figure==11:
        colors[535]=1

        #plot the particles on top of the trails, two options for how...
        
    if hardcode_figure==None:

        ax.scatter(x_p,y_p,s=size,
                   facecolor=facecolor,edgecolor=edgecolor,
                   linewidth=edgewidth, rasterized=True)
        
        #,c=v_x,vmin=-1.0,vmax=1.0,s=size,cmap=cm.seismic)

    elif 1:
        'color one particle blue, the rest gray,no clue why one is teal.'
        cmap=mpl_colors.ListedColormap(['royalblue', 'gray', 'r'])
        ax.scatter(x_p,y_p,c=colors,s=size,cmap=cmap,vmin=-2,vmax=2)

        
    return
#################################################################
#################################################################


if __name__ == "__main__":

    #assume square system size
    Sy = [0.0, 36.0]
    Sx = [0.0, 36.0]

    SX = (Sx[1]-Sx[0])
    SY = (Sy[1]-Sy[0])

    #set rows and columns
    columns = 1
    rows = 1
    
    #use your handy-dandy class to make the figure
    pC = plotColloid.plotColloid(rows,columns,Sx,Sy,
                                 scale_x=4.0,scale_y=4.0)


    fig = pC.createAxes(suppress_axes_labels=2)
    all_axes = fig.get_axes()

    ax = all_axes[0]
    
    #-----------------------------
    t0=int(sys.argv[1])
    tf=int(sys.argv[2])

    
    make_trails(ax,tf,delta_t=500,N=256,path1='',
                SX=36.0,SY=36.0,size=100,line=2)

    #work on calling the rest of this from the subroutine above

    #################################################################
    #get and organize the data AKA the scary part
    #################################################################

    #number of particles to draw trails of,s 
    #could figure this out from array lengths after first import
    N=int(sys.argv[3])

    #directory ='/home/mcdermott/Research/ActiveMatterProject/'
    #directory+='k30springs/Ap3.0_N1200_Npins12_RL10000/frame_data/'

    
        
    fig.tight_layout() #pad=0.0)

    out_file="trails%d-%d.eps"%(t0,tf)
    plt.savefig(out_file)

    exit()
