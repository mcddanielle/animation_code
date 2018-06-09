#https://wiki.helsinki.fi/display/~mjuvela@helsinki.fi/Reading+files+with+Python

import numpy as np


fp = file('smtest', 'rb')
# open the file, r= for reading, b=binary file

nV, time = np.fromfile(fp, np.int32, 2)     # read three 32 bit integers
for n in range(nV):
    i    = np.fromfile(fp, np.int32, 1)[0]
    x,y  = np.fromfile(fp, np.float32, 2)
    

print(i,x,y)


