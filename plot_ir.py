from TelopsToolbox.readIRCam import read_ircam
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import glob
import sys 
import os 
from shapely.geometry import Point
from pathlib import Path
import os
os.environ['PROJ_LIB'] = '/home/paugam/miniforge3/envs/telops/share/proj'
import pdb 
from PIL import PngImagePlugin, Image
import tifffile


dirTelops = '/home/paugam/Data/ATR42/as250026/telops'
if True:
    extractionName='Sijean06'
    flightname = 'SILEX_test001'
    start_FrameID=1190580
    end_FrameID  =1232752
    start_dt = None
    end_dt   = None 
    dt_period = 0.1
if False:
    extractionName='Sijean010'
    flightname = 'SILEX_test001'
    start_FrameID=2990344
    end_FrameID  =3010688
    start_dt = None
    end_dt   = None 
    dt_period = 0.1


#dirTelops = '/home/paugam/Data/ATR42/as250018/telops'
#extractionName='cimenterie'
#extractionName='imgRef2'
#extractionName='Sijean06'
#extractionName='Sijean10'
#flightname = dirTelops.split('/')[-2]
#  select data in time range.
#start_dt = pd.to_datetime("2025-07-10 08:26:50")
#end_dt = pd.to_datetime("2025-07-10 08:27:13")
#dt_period = 1
##start_dt = pd.to_datetime("2025-07-10 09:46:30")
##end_dt   = pd.to_datetime("2025-07-10 09:51:30")

root_dir = Path(dirTelops)
telopsfiles = list(root_dir.rglob('*.hcc'))  

#
#  load flight summary
#
gdf = gpd.read_file(f"{dirTelops}/summary_{flightname}.gpkg")

#
#  select data in bbox.
#
#gdf_box = gpd.read_file(f"{dirTelops}/../{extractionName}/bbox.gpkg")
#gdf_clipped = gpd.clip(gdf, gdf_box)

if start_dt != None:
    gdf_clipped = gdf[(gdf['timestamp'] >= start_dt) & (gdf['timestamp'] <= end_dt)]
elif  start_FrameID != None:
    gdf_clipped = gdf[(gdf['FrameID'] >= start_FrameID) & (gdf['FrameID'] <= end_FrameID)]
else:
    print('missing info to select transect')
    print('stop here')
    sys.exit()

#update time
#gdf_clipped = gdf_clipped.copy()  # avoid SettingWithCopyWarning
#gdf_clipped.loc[:,'datetime2']  = pd.to_datetime(gdf_clipped["POSIXTime"], unit="s").astype('datetime64[ms]') +\
#                                  pd.to_timedelta(gdf_clipped["SubSecondTime"], unit="ms")

os.makedirs(f"{dirTelops}/../{extractionName}/png/", exist_ok=True)
os.makedirs(f"{dirTelops}/../{extractionName}/png_f1/", exist_ok=True)
flag_start = True
ii = 1
idxaxes = [0, 3, 6, 7, 8, 5, 2, 1]
lastTimePlotted = gdf_clipped.sort_values(by='FrameID')['timestamp'].iloc[0]
flag_grab_other_fr = False
for iii, infoframe in gdf_clipped.sort_values(by='FrameID').iterrows():
  
    #print(infoframe['FWPosition'], (infoframe['timestamp'] - lastTimePlotted).total_seconds(), lastTimePlotted)
    filename = infoframe['filename']
    data, header, specialPixel, nonSpecialPixel = read_ircam(filename, frames=[infoframe['iframe']] )

    img = data[0].reshape(infoframe['Height'],infoframe['Width'])
    #print(infoframe['FWPosition']) 
   

    if flag_start: 
        if infoframe['FWPosition'] != 0: 
            continue
        else:
            flag_start = False
    
    #if (infoframe['timestamp'] - lastTimePlotted).total_seconds() < dt_period: 
    #    if not(flag_grab_other_fr): 
    #        #print(' ', iii, ii, infoframe['FWPosition'], (infoframe['timestamp'] - lastTimePlotted).total_seconds())
    #        continue


    if (not(flag_grab_other_fr)) and ( infoframe['FWPosition'] == 0 ):
        
        ratio_ = infoframe.Height/infoframe.Width
        target_width, target_height = 640, 512
        dpi = 100  # Set DPI such that figsize * dpi = pixel size
        figsize = (target_width / dpi, target_height / dpi)
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.subplot(111)
        ax.imshow(img[:,::-1], origin='lower' ,vmin=4000,vmax=5500)
        ax.set_axis_off()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove padding/margins
        plt.margins(0)  # No padding
        plt.gca().xaxis.set_major_locator(plt.NullLocator())  # No ticks
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        fig.savefig(f"{dirTelops}/../{extractionName}/png_f1/f1-{ii:09d}.png")
        plt.close(fig)
        # Add metadata using Pillow
        temp_path = f"{dirTelops}/../{extractionName}/png_f1/f1-{ii:09d}.png"
        img_pil = Image.open(temp_path)
        meta = PngImagePlugin.PngInfo()
        meta.add_text("Time", str(infoframe['timestamp']))
        meta.add_text("FrameID", str(infoframe['FrameID']))
        # Save again with metadata (overwrite)
        img_pil.save(temp_path, pnginfo=meta)
        print('*', end='')
        
        # Path for the TIFF file
        tif_path = f"{dirTelops}/../{extractionName}/tif_f1/f1-{ii:09d}.tif"
        # Ensure directory exists
        os.makedirs(os.path.dirname(tif_path), exist_ok=True)
        # Save as float32 TIFF with metadata
        tifffile.imwrite(
            tif_path,
            img[::-1,::-1].astype('float32'),
            metadata={
                "Time": str(infoframe['timestamp']),
                "FrameID": str(infoframe['FrameID'])
            }
        )

        fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(10, 10))
        axes = axes.flatten()
        fig.suptitle(f"{infoframe['timestamp']}\n lon:{infoframe['Latitude_deg']} lat:{infoframe['Latitude_deg']}, alt(m):{infoframe['GPSAltitude']/100}", fontsize=12)
        lastTimePlotted = infoframe['timestamp']
        flag_grab_other_fr = True 
    
    if (flag_grab_other_fr) and (infoframe['FWPosition'] < 7):
        print(' ', end='')
        axes[idxaxes[infoframe['FWPosition']]].imshow(img[:,::-1], origin='lower') 
        axes[idxaxes[infoframe['FWPosition']]].set_title(f"filtre{infoframe['FWPosition']+1}")

        print( iii, ii, infoframe['FWPosition'], infoframe['FrameID'], (infoframe['timestamp'] - lastTimePlotted).total_seconds(), infoframe['timestamp'], infoframe['GPSLatitude']*1.e-7, infoframe['GPSLongitude']*1.e-7)
    
        if (infoframe['FWPosition'] == 5):
            # Path for the TIFF file
            tif_path = f"{dirTelops}/../{extractionName}/tif_f5/f5-{ii:09d}.tif"
            # Ensure directory exists
            os.makedirs(os.path.dirname(tif_path), exist_ok=True)
            # Save as float32 TIFF with metadata
            tifffile.imwrite(
                tif_path,
                img[::-1,::-1].astype('float32'),
                metadata={
                    "Time": str(infoframe['timestamp']),
                    "FrameID": str(infoframe['FrameID'])
                }
            )


    if (flag_grab_other_fr) and (infoframe['FWPosition'] == 7): 
        axes[4].set_axis_off()
        fig.savefig(f"{dirTelops}/../{extractionName}/png/{ii:09d}.png")
        plt.close(fig)
        flag_start = True
        ii+=1
        flag_grab_other_fr = False        
    

