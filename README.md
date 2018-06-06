To run this on a data set:

''' $ python NewFastMovieMaker.py '''

or

'''$ python make_image.py '''

* data should be in a file resembling "velocity_data/XV_data_t="
* for either code, you can play with the colors or particle sizes and other options by digging around the source code.
* For an animation code, if this is the first time you're running, set the flag

''' get_data=1 '''

this means that python will read in the ascii files one by one, which is one of the most inefficient parts of the process.  Once you’ve run the code once, you should have twice the number of files with the python binary file handle “.npy” instead of the original extension free name.  Then you can change “get_data” to zero, and it will read the .npy files instead.  Basically it is writing a python formatted binary of the arrays you stored the first time you loaded the files.  The read/writes of binary files is faster, so this happens faster.

Next improvement, it doesn’t completely redraw the frame every time.  Instead it updates the particle positions (the other parameters such as size can also be updated).  This is much faster too.

