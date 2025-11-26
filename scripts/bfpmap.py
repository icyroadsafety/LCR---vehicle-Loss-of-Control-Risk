import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from cartopy.feature import ShapelyFeature
import shapefile
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader


def create_overlayed_bfp_plot(nc_file, output_image, timestamp, color_table_paths, variable_names, titles):
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, figsize=(20, 16))
    ax.set_extent([-127, -65, 21, 48]) 
    
    # Add map features
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='cultural', name='roads', scale='10m', facecolor='none', edgecolor='grey', alpha=0.3), linewidth=1.0)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.5)
    ax.add_feature(cfeature.LAKES, edgecolor='blue', facecolor=(200/255, 200/255, 200/255), linewidth=0.1, alpha=1)
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='ocean',scale='50m',
        facecolor=(200/255, 200/255, 200/255), edgecolor='none',alpha=1))
    ax.coastlines()
  
    
    color_bar1 = plt.imread('maps/mapoverlays/bfpplus-scale8.png')
    ax.imshow(color_bar1, extent=[-126.8, -99.7, 21.1, 27.3], transform=ccrs.PlateCarree(), alpha=1, zorder=10) 


    # Read the shapefiles for Canada and Mexico
    canada_shapefile = 'maps/shp/CAN_adm0.shp'
    mexico_shapefile = 'maps/shp/MEX_adm1.shp'

    canada_feature = ShapelyFeature(shpreader.Reader(canada_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)
    mexico_feature = ShapelyFeature(shpreader.Reader(mexico_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)
    ax.add_feature(canada_feature)
    ax.add_feature(mexico_feature)

    # Add interstate from local data
    reader = shpreader.Reader("maps/shp/tl_2019_us_primaryroads.shp")
    names = []
    geoms = []
    for rec in reader.records():
        if rec.attributes['FULLNAME'].startswith('I'):
            names.append(rec)
            geoms.append(rec.geometry)
    shape_feature = ShapelyFeature(geoms, ccrs.PlateCarree(), edgecolor='red', alpha=0.3, lw=1, facecolor='none')
    ax.add_feature(shape_feature)
    
    data = xr.open_dataset(nc_file)
    data = data.where(data != 0)
    for color_table_path, variable_name, title in zip(color_table_paths, variable_names, titles):
        # data = xr.open_dataset(data_path)
        # data = data.where(data != 0)
        color_table_data = pd.read_csv(color_table_path, skiprows=3, delim_whitespace=True, names=['red', 'green', 'blue']) 
        color_table_data[['red', 'green', 'blue']] = color_table_data[['red', 'green', 'blue']].apply(pd.to_numeric, errors='coerce') / 255.0
        color_table_data = color_table_data.dropna()
        cmap = mcolors.ListedColormap(color_table_data.values)
        plot = data[variable_name].plot(ax=ax, cmap=cmap, add_colorbar=False,transform=ccrs.PlateCarree(), vmin=0, vmax=0.1)

    # Read timestamp from the text file
    # timestamp_file_path = 'bfptimestamp.txt'
    #with open(timestamp_file_path, 'r') as timestamp_file:
    #    timestamp = timestamp_file.read().strip()

    # Add timestamp to the top of the image
    fig.text(0.5, 0.815, f'{timestamp}', ha='center', fontsize=14)

    # Add text to map scale
    fig.text(0.194, 0.281, f'Precipitation of Any Type vs Surface Temperature Environment', ha='left', fontsize=9.5, color=(255/255, 255/255, 255/255))
    fig.text(0.367, 0.264, f'Critical Icing Temp (Highest Risk)', ha='left', fontsize=8, color=(168/255, 2/255, 4/255))
    fig.text(0.367, 0.2505, f'Below-Freezing (Icy Road Warning)', ha='left', fontsize=8, color=(0/255, 9/255, 189/255))
    fig.text(0.367, 0.237, f'Near-Freezing (Icy Road Caution)', ha='left', fontsize=8, color=(189/255, 120/255, 0/255))
    fig.text(0.367, 0.223, f'Above Freezing (No Icing)', ha='left', fontsize=8, color=(0/255, 189/255, 4/255))
    fig.text(0.132, 0.264, f'CIP: At/Below 29°F/-2°C', ha='left', fontsize=10.1, color=(168/255, 2/255, 4/255))
    fig.text(0.132, 0.2495, f'BFP: 30°F-32°F', ha='left', fontsize=10.5, color=(0/255, 9/255, 189/255))
    fig.text(0.132, 0.2355, f'NFP: 33°F-38°F', ha='left', fontsize=10.5, color=(189/255, 120/255, 0/255))
    fig.text(0.132, 0.222, f'AFP: Above 38°F/33°C', ha='left', fontsize=10.5, color=(0/255, 189/255, 4/255))
    fig.text(0.165, 0.198, f'Surface', ha='center', fontsize=8.5, color=(71/255, 71/255, 71/255))
    fig.text(0.165, 0.190, f'Temperature', ha='center', fontsize=8.5, color=(71/255, 71/255, 71/255))
    fig.text(0.42, 0.198, f'Level', ha='center', fontsize=8.5, color=(71/255, 71/255, 71/255))
    fig.text(0.42, 0.190, f'of Risk', ha='center', fontsize=8.5, color=(71/255, 71/255, 71/255))
    fig.text(0.227, 0.192, f'Maximum 1-Hour Precip Amount', ha='left', fontsize=11, color=(71/255, 71/255, 71/255))
    fig.text(0.219, 0.204, f'0"', ha='center', fontsize=14, color=(0/255, 0/255, 0/255))
    fig.text(0.293, 0.204, f'0.05"', ha='center', fontsize=14, color=(0/255, 0/255, 0/255))
    fig.text(0.366, 0.204, f'0.1"+', ha='center', fontsize=14, color=(0/255, 0/255, 0/255))
    fig.text(0.53, 0.243, f'LCR v1.2.2 :', ha='left', fontsize=15, color=(0/255, 0/255, 0/255))
    fig.text(0.6, 0.243, f'BFP+', ha='left', fontsize=15, color=(7/255, 18/255, 119/255))
    fig.text(0.53, 0.233, f'https://icyroadsafety.com/lcr/', ha='left', fontsize=9.5, color=(0/255, 0/255, 0/255))

    # # Read logo overlay image
    overlay2_path = 'maps/mapoverlays/logomap.png'
    overlay2 = plt.imread(overlay2_path) 
    ax.imshow(overlay2, extent=[-78, -69, 27, 31],   transform=ccrs.PlateCarree(), alpha=1, zorder=10)

    # plt.savefig('bfpplus.png', dpi=130, bbox_inches='tight')
    plt.savefig(output_image , dpi=130, bbox_inches='tight')
    # plt.show()



# data_paths = ['afp.nc', 'nfp.nc', 'bfp.nc']
nc_file=sys.argv[1];
output_image=sys.argv[2];
timestamp=sys.argv[3]

# get scripts directory and move to it
# then move to maps directory as all resources are relative to map directory
lcrBase=os.path.dirname(__file__)
lcrBase=os.path.dirname(lcrBase)
os.chdir(lcrBase)




color_table_paths = ['maps/bfpplus-afp-colors-0-to-1.tbl', 'maps/bfpplus-nfp-colors-0-to-1.tbl', 'maps/bfpplus-bfp-colors-0-to-1.tbl', 'maps/bfpplus-cip-colors-0-to-1.tbl']
variable_names = ['afp', 'nfp', 'bfp', 'cip']
titles = ['AFP Data', 'NFP Data', 'BFP Data', 'CIP Data']



# Generate overlayed plots
create_overlayed_bfp_plot(nc_file, output_image, timestamp, color_table_paths, variable_names, titles)

