6/14/2018

## Getting started

Each python/bash code now has an identifier at the top of the code that reads

`#!/usr/bin/python`
or 
`#!/usr/bin/bash`

you may make these executable files by typing the following in a terminal

`$ chmod u+x *py *sh`

then you can either run the usual way:

`$ python ~/Codes/animation_code/channel_colloid_movie_maker.py`

or now that you've set these as executables, you don't need to tell the terminal what kind of code you're running

`$ ~/Codes/animation_code/channel_colloid_movie_maker.py`

## Files
### active_movie_maker.py
For Adrian's project.  Expects to find Pa0 and a "cmovie" format
(i.e. the binary file has the type and radius)

### channel_colloid_movie_maker.py
For Tiare's project.  Expects to find Pcw0 and a "smovie" format
(i.e. the binary file just has id, x, y)

### colloid_plot_library.py
Collection of plotting subroutines called by all movie_maker codes

### data_importerDM.py
Collection of data reading subroutines, both binary and ascii.
The ascii could be made faster using np.loadtxt()

### make_image.py
Not fully updated - but uses colloid_plot_library.py as does the movie codes

### movie_maker.py
For D.M.'s projects

### get_data.sh
Translates time separated data (stored in velocity_data/XV...) into particle separated data (stored in position_data/id00_XV...)

------------------------------------------------------------------------
OLD:
------------------------------------------------------------------------
To run this on a data set:

` $ python NewFastMovieMaker.py `

or

`$ python make_image.py `

* data should be in a file resembling "velocity_data/XV_data_t="
* for either code, you can play with the colors or particle sizes and other options by digging around the source code.
* For an animation code, if this is the first time you're running, set the flag

''' get_data=1 '''

this means that python will read in the ascii files one by one, which is one of the most inefficient parts of the process.  Once you’ve run the code once, you should have twice the number of files with the python binary file handle “.npy” instead of the original extension free name.  Then you can change “get_data” to zero, and it will read the .npy files instead.  Basically it is writing a python formatted binary of the arrays you stored the first time you loaded the files.  The read/writes of binary files is faster, so this happens faster.

Next improvement, it doesn’t completely redraw the frame every time.  Instead it updates the particle positions (the other parameters such as size can also be updated).  This is much faster too.

