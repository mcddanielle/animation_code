#!/usr/bin/bash

#script is intended to loop through outputs of MD codes
#and separate all of the time separated data into particle separated data
#a different manner of sorting for a different kind of plotting


#terminal sample command
#{ for i in velocity_data/XV_data_t\=0000*0; do echo "$( head -n 20 "$i" | tail -n 1 )"; done ;} > output.txt

#grab all ascii files of the right name structure
file=( velocity_data/XV_data_t\=*0 )

#check whether position_data is already a directory
if [ -d position_data ]
then
    echo "deleting old version of directory position_data"
    rm -r position_data/  #delete the old version
fi

#start clean with a blank directory
mkdir position_data    #

i=0
for ((i=0;i<21;i++));
do
    #i is the particle number, print it to the terminal
    echo "executing particle: " $i

    #give the file for that particle number a name
    name=$(printf 'position_data/id%02d_XV_data.txt' "$i")

    #make the file exist so we can write to it
    touch $name
    
    for j in "${file[@]}" #loop through all files
    do
	#grab the time from the file number
	time=$(echo $j | cut -d'=' -f2)

	#grab the line number, assuming there is a 3 line header
	k=$(expr $i + 4)

	#$echo $i $j, $k, $time

	#put the pertinate information in our particle_data file
	echo "$( head -n "$k" "$j" | tail -n 1 ) $time" >> $name

    done  #finish the first for loop

    echo $name  #print the file name
done #finish the second for loop
    
