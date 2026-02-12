import numpy as np 
import matplotlib.pyplot as plt 
import pyradi.ryptw as ryptw
import sys
import glob 

ptwfiles  = sorted(glob.glob('/home/paugam/Data/ATR42/as250018/flir/*.ptw'))

for ptwfile in ptwfiles:

    header = ryptw.readPTWHeader(ptwfile)
    #ryptw.showHeader(header)

    rows = header.h_Rows
    cols = header.h_Cols
    
    sys.exit()
    framesToLoad = list(range(1, 101, 1))
    frames = len(framesToLoad)
    data,_ = ryptw.getPTWFrame (header, framesToLoad[0])
    for frame in framesToLoad[1:]:
        f, _ = (ryptw.getPTWFrame (header, frame))
        data = np.concatenate((data, f))
        
    img = data.reshape(frames, rows ,cols)

    plt.imshow(img[60])
    plt.show()
