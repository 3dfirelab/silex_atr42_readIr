from TelopsToolbox.readIRCam import read_ircam
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt 
import glob
import sys 
import os 
from shapely.geometry import Point
from pathlib import Path
from datetime import datetime

#dirTelops = '/home/paugam/Data/ATR42/as250018/telops'
#flightname = dirTelops.split('/')[-2]

dirTelops = '/home/paugam/Data/ATR42/as250026/telops'
flightname='SILEX_test001' # bad naming of the file 

root_dir = Path(dirTelops)
telopsfiles = list(root_dir.rglob('*.hcc'))  
telopsfiles_sorted = sorted(
    telopsfiles,
    key=lambda p: datetime.strptime(p.stem.split('_')[-1], "%Y%m%dT%H%M%S%f")
)
#
#  generate flight summary
#
if os.path.isfile(f"{dirTelops}/summary_{flightname}.gpkg"):
    gdf = gpd.read_file(f"{dirTelops}/summary_{flightname}.gpkg")
else:
    df = None
    for ii, telopsfile in enumerate(telopsfiles_sorted):
        
        if flightname not in telopsfile.name: continue
        print( f"{ii}/{len(telopsfiles)} - {os.path.basename(telopsfile)}", end='  ')
        sys.stdout.flush()

        data, header, specialPixel, nonSpecialPixel = read_ircam(str(telopsfile.absolute()), headers_only=True)

        header_df = pd.DataFrame(header)

        header_df['filename'] = str(telopsfile.absolute())
        header_df["timestamp"] = (
                pd.to_datetime(header_df["POSIXTime"], unit="s").astype('datetime64[us]') +\
                pd.to_timedelta(header_df["SubSecondTime"]*1.e-7, unit="s")
                )
        header_df['iframe'] = header_df.index

        header_df["Latitude_deg"]  = header_df["GPSLatitude"] / 1.e7
        header_df["Longitude_deg"] = header_df["GPSLongitude"] / 1.e7
        

        print(  header_df["timestamp"].iloc[-1])
        if df is None:
            df = header_df
        else:
            df = pd.concat([df, header_df], ignore_index=True)

    # Create Point geometries
    geometry = [Point(xy) for xy in zip(df["Longitude_deg"], df["Latitude_deg"])]

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # WGS84

    gdf.to_file(f"{dirTelops}/summary_{flightname}.gpkg", driver="GPKG")






