#!/usr/bin/python

"""General_Vortex2D_PlotModule.py
Danielle McDermott
May 29, 2014

Some general data importing routines... 
need to refer to these rather than earlier copies... 
sigh... Version control
"""

import csv
import numpy as np

#####################################################
#Define Modules
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
                print("")
            elif line:
                #print line
                yield line
    return
#------------------------------------------------------------
#end CSV reader------------------------------------------
#------------------------------------------------------------

def get_data(file_name,columns,sep=' ',path1=''):
    '''Really nice data importer, since it works for any columnar data.

    file_name = "data.txt"
    columns = number of columns in file
    sep = optional, default is space, other could be '\t'
    path1 = path before file name
    '''

    file_name=path1+file_name
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
