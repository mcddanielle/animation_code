#!/usr/bin/python

"""
Get data from a variety of file formats
Danielle McDermott
June 10, 2018

need to update these using np.fromfile - 
probably more efficient that your method
"""

import csv
import numpy as np

'''to do - pass the file pointer after you've opened it, so you are reading from the buffer, rather than reading the same positions over and over.'''

def read_smtest(infile='smtest', movie_type="smovie"):
    '''Reads the binary movies generated by Reichhardt MD codes

    required arguments
    writemovietime - as in Pa0/Pcw0

    optional arguments
    infile='smtest'  default name of almost all movie files

    movie_type="smovie" other options (not coded) include "cmovie" and "jmovie"
    '''

    #better error handling
    # open the file, r= for reading, b=binary file
    #fp = file(infile, 'rb')  #doesn't account for failure

    datafile_prefix = "velocity_data/XV_data_t="    

    with open(infile, 'rb') as fp:
    
        fp.seek(0, 2)  # Seek the end
        tot_num_bytes = fp.tell()  # Get the file size
        fp.seek(0, 0)  # Seek the beginning

        while fp.tell()<tot_num_bytes:
            #get nV, number of particles
            # read two 32 bit integers
            nV, time = np.fromfile(fp, np.int32, 2)     

            #make arrays to store data
            id = np.empty(nV,dtype=np.int32)
            type = np.ones(nV,dtype=np.int32)
            x_array = np.empty(nV,dtype=np.float32)
            y_array = np.empty(nV,dtype=np.float32)
            r_array = np.empty(nV,dtype=np.float32)  #radius

            #for cmovie you also need these
            #size = disk_size * np.ones(len(id))
            #type = np.ones(len(id))
            
            if movie_type == "smovie":
                dtype = np.dtype("i4, (2)f4")
        
            elif movie_type == "cmovie":
                dtype = np.dtype("(2)i4, (3)f4")
            #    type  = np.fromfile(fp, np.int32, 1)[0]
            
            for n in range(nV):        # loop through all particles

                #i,x,y    = np.fromfile(fp, dtype, 1) #doesn't work
                data1 = np.fromfile(fp, dtype, 1)
                
                if movie_type == "smovie":
                
                    try:
                        id[n] = data1[0][0]
                        x_array[n] = data1[0][1][0]
                        y_array[n] = data1[0][1][1]
                    except:
                        print("problem reading smovie")
                        print(data1)
                        print(n)

                elif  movie_type == "cmovie":
                    
                    try:
                        type[n] = data1[0][0][0]
                        id[n] = data1[0][0][1]
                        x_array[n] = data1[0][1][0]
                        y_array[n] = data1[0][1][1]
                        r_array[n] = data1[0][1][2]
                    except:
                        print("problem reading cmovie")
                        print(data1)
                        print(n)                    

            save_file=datafile_prefix+"%08d"%(time)

            particle_data = np.array([id,type,x_array,y_array])
            #print("!!")
            np.save(save_file,particle_data)
            
    return

    
#####################################################
#simple ascii text reader
#####################################################
def import_text(filename, separator):
    '''Simple csv file reader, reads line by line, ignores comments of '#' type

    file_name = absolute name
    separator = ' ', '\t', etc
    '''
    for line in csv.reader(open(filename), delimiter=separator, 
                           skipinitialspace=True):
        if line:
            if line[0].startswith("#"):
                continue #print("")
            elif line:
                #print line
                yield line
    return
#------------------------------------------------------------
#end CSV reader------------------------------------------
#------------------------------------------------------------

def get_data(file_name,columns,sep=' ',path1='',verbose=False):
    '''Really nice data importer, since it works for any columnar data.

    file_name = "data.txt"
    columns = number of columns in file
    sep = optional, default is space, other could be '\t'
    path1 = path before file name
    '''

    file_name=path1+file_name
    if verbose == True:
        print(path1)
        print(file_name)

    import_data = []

    for i in range(columns):
        import_data.append([])

    for data in import_text(file_name, sep):  
        for i in range(columns):
            import_data[i].append(float(data[i]))
            
    return(np.array(import_data))

###############################################################
def data_read_error(error_code=-1,path=''):
        print("are you in the proper directory?")
        print("please check your data files")

        print("path is:\n", path)
        exit(error_code)
