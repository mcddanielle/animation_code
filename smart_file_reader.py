#!/usr/bin/env python3

"""
Danielle McDermott
July 24, 2019
NOT portable code for reading parameter files in the McDermott lab

To Do:
rewrite the code so you read the values into a hash, 
eliminating the need to rewrite everything when you change the parameter file
"""

"""
Shannon Gallagher
July 25, 2019

Portable code for reading parameter files in the McDermott lab

Added dictionary function to allow for greater flexibitily in parameter file
formats


"""

import csv, sys
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
                #print (type(line))
                yield line
    return

################################################################
#get and parse information that allows us to make the movie
#this is hardcoded, which is ugly
#want these variables to be globals to work with the animation subroutine
def get_input_data(filename):
    '''
    hardcoded to look for two particular types of files
    will exit if it does not get those types

    filename: Pa0, Pcw0 (or Pd0 if you want to go back to 2012)
    '''

    if filename == "Pa0" or "Pcw0":

        print("Reading parameters from: %s"%(filename))

        try:
            #data is traditionally placed in a two column file
            #with a string/number format, where number is integer or float

            #make an empty list to hold data as strings
            input_data_strings = []
            for data in import_text(filename,' '):
                #print(data)
                input_data_strings.append(data)
            
                
        except:
            print("File read error")
            sys.exit()

        
    else:
        print("Code is not written to understand your input file")
        print("Either hardcode your parameters or write a new subroutine")
        sys.exit()
        
    dict={}
    for i in range(0,len(input_data_strings)):
        try:
            float(input_data_strings[i][1])
            if '.' in input_data_strings[i][1]:
                dict[input_data_strings[i][0]] = float(input_data_strings[i][1])
            else:
                dict[input_data_strings[i][0]] = int(input_data_strings[i][1])
        except ValueError:
                dict[input_data_strings[i][0]] = str(input_data_strings[i][1])
                
    # here are the features which the origninal code states are equivalent
    if filename == "Pcw0":
        dict['maxtime'] = dict['tot_time']
        dict['writemovietime'] =dict['writemovie']
    

    # here are the feaures which are unchanging
    if filename == "Pcw0":
        dict['dt' ]= 0.01
        dict['radius'] = 1.0
    
    '''
    if filename == "Pa0":
        return(dict['SX'], dict['SY'], dict['radius'], dict['maxtime'], dict['writemovietime'])
    if filename == "Pcw0":
        return(dict['SX'], dict['SY'], dict['radius'], dict['maxtime'], dict['writemovietime'], dict['drop'], dict['dt'])
    '''
    return dict
        
    
    
    #else:
    #    print("TBD")
    #    sys.exit()
        
################################################################
################################################################
################################################################

if __name__ == "__main__":

    print(get_input_data("Pcw0"))
    print(get_input_data("Pa0"))
