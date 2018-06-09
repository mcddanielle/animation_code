import numpy as np

nV=80
#dt_header = np.dtype("i4, i4")
#dt_body   = np.dtype("i4, f8, f8")


fp = file('smtest', 'rb')
# open the file, r= for reading, b=binary file

nV, time = np.fromfile(fp, np.int32, 2)     # read three 32 bit integers
print(nV,time)
i    = np.fromfile(fp, np.int32, 1)[0]
x,y  = np.fromfile(fp, np.float32, 2)

print(i,x,y)


