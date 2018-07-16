import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

from matplotlib import cm

#import classColloid.plotColloid as plotColloid
import colloid_plot_library as cpl
import data_importerDM as di

import sys
import numpy as np
import matplotlib.colors as mpl_colors

#################################################################
#################################################################
def plot_ratchet_potential_2D(ax, L=36.0,Npins=24.0):
    '''not recently updated.  use at your own risk.
    '''

    Fp = 1

    x_max = L
    a_p = L/Npins

    X = np.arange(0, x_max, 0.1)
    Y = np.arange(0, L, 0.5)
    X, Y = np.meshgrid(X, Y)

    Z = Fp*(np.sin(2*np.pi*X/a_p) + 0.25*np.sin(4*np.pi*X/a_p))

    if 0:
        cmap=cm.YlGn_r
    else:
        cmap=cm.coolwarm_r

    cset = ax.contourf(X, Y, Z, zdir='z',offset=-1, 
                       cmap=cmap,alpha=0.6,rasterized=True)

    return

################################################################
def histogram_velocities(ax,time,filename=None,path=""):
    '''not recently updated.  use at your own risk.
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

    ax:      subplot pointer to plot on
    tf:      the time of interest, we will do a scatter plot of this
    delta_t: range of timesteps to plot the particle trail 
             prior to the time of interest
             NOTE: no current contingency for small times, 
             where trails do not exist
    N:       number of particles in the simulation
    '''

    verts=[]
    codes=[]

    for i in range(N):
        verts.append([])
        codes.append([])

    t0= tf - delta_t*6

    x0=None

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
            x0=x_p ##array containing all starting positions of particles

        ########################################################
        #center everybody, 
        ########################################################
        if 0:
            x_p=np.add(x_p,36.5/4.0)

        ########################################################
        #periodic boundary conditions 
        ########################################################
        if 0:
            for q in range(len(x_p)):
                if x_p[q] > 36.5:
                    x_p[q]-=36.5

        for i in range(N):

            restart=0
            
            if time > t0:
                x_old,y_old = verts[i][-1]

                dist_x = x_p[i]-x_old
                dist_y = y_p[i]-y_old

                if abs(dist_x) > SX/2.0 or abs(dist_y) > SY/2.0:
                    #print dist_x,  x_p[i],x_old
                    #print dist_y,  y_p[i],y_old
                    del(codes[i][-1])
                    codes[i].append(Path.MOVETO)

                    #codes[i].append(Path.END)

                    restart=1
            #print i, N    
            verts[i].append( [ x_p[i],y_p[i] ])
            

            if time == t0 or restart==1:
                    
                codes[i].append(Path.MOVETO)
            elif time>t0 and time<tf:
                codes[i].append(Path.LINETO)

            elif time == tf:
                print Path.END
                codes[i].append(Path.END)

    #now that we've collected all the data, plot it
    sysSX=36.0
    sysSY=36.0
    for i in range(N):

        #Measure the length of the path
        dx=abs(verts[i][0][0]-verts[i][-1][0])
        dy=abs(verts[i][0][1]-verts[i][-1][1])
        if dx>(sysSX/2.0):
            dx = abs(dx - sysSX)
        if dy>(sysSY/2.0):
            dy = abs(dy - sysSY)
        distance = np.sqrt( dx**2 + dy**2 )
        
        #only if the path length is longer than this:
        if distance > 0.25:
            path = Path(verts[i], codes[i])
            patch = patches.PathPatch(path, facecolor='none', edgecolor='black', lw=line,antialiased=True)
            #,rasterized=True)
            ax.add_patch(patch)

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

    delta_x=x_p-x0 #total difference moved over the plotted frame
    colors=np.zeros(N) #array containing a zero for every particle
    #print len(colors), len(delta_x)
    if 1:
        for i in range(len(delta_x)):
            period=0.26*SX/num_troughs
            if delta_x[i] <=-period:
                colors[i]=-1
            elif delta_x[i]>=period:
                colors[i]=1

            #print delta_x[i], colors[i]
            #else:
            #    colors
            '''
                if 20 < x_p[i] and  x_p[i] < 28 and y_p[i] <8:
                    print i
                    exit()
            '''
    elif hardcode_figure==11:
        colors[535]=1

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
