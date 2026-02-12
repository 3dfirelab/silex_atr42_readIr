from TelopsToolbox.readIRCam import read_ircam
import pandas as pd
import matplotlib.pyplot as plt 


fileinput = '/home/paugam/Data/ATR42/as250017/telops/vol17_20250709T090252134_20250709T090351845.hcc'

""" read the first 50 frames of a sequence hcc """
data, header, specialPixel, nonSpecialPixel = read_ircam(fileinput, frames=list(range(0, 100)))

header_df = pd.DataFrame(header)



ax=plt.subplot(121)
iframe = 56
frame = data[iframe].reshape(header_df.loc[iframe]['Height'],header_df.loc[iframe]['Width'])
ax.imshow(frame)

ax=plt.subplot(122)
iframe = 56+8
frame = data[iframe].reshape(header_df.loc[iframe]['Height'],header_df.loc[iframe]['Width'])
ax.imshow(frame)
plt.show()
