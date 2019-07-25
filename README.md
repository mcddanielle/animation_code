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
The ascii has been made faster using np.loadtxt()

### make_image.py
Uses colloid_plot_library.py as does the movie codes
optional command line arguments, so you can set the plottime and output file type (png, pdf, etc) at run time.
`$ ~/Codes/animation_code/make_image.py -t 5000 -f "pdf"`


### movie_maker.py
For D.M.'s projects

### get_data.sh
Translates time separated data (stored in velocity_data/XV...) into particle separated data (stored in position_data/id00_XV...)

To run, be in directory with `velocity_data` and run

`~/Codes/animation_code/get_data.sh`


** for any code, you can play with the colors or particle sizes and other options by digging around the source code. **


