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


def create_overlayed_bfp_plot(nc_file, output_image, color_table_paths, variable_names, titles):
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, figsize=(20, 16))
    ax.set_extent([-127, -65, 17, 48])  
    
    # Add map features
    ax.add_feature(cfeature.NaturalEarthFeature(
        category='cultural', name='roads', scale='10m', facecolor='none', edgecolor='grey', alpha=0.3), linewidth=1.0)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.5)
    ax.add_feature(cfeature.LAKES, edgecolor='blue', facecolor=(200/255, 200/255, 200/255), linewidth=0.1, alpha=1)
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='ocean',scale='50m',
        facecolor=(200/255, 200/255, 200/255), edgecolor='none',alpha=1))
    ax.coastlines()
    gl = ax.gridlines(crs=ccrs.PlateCarree(), linestyle='--', alpha=0.8)
    
    
    color_bar1 = plt.imread('mapoverlays/bfpplus-scale.png')
    ax.imshow(color_bar1, extent=[-120, -72, 17, 24.5], transform=ccrs.PlateCarree(), alpha=1, zorder=10)  

    # Read the shapefiles for Canada and Mexico
    canada_shapefile = 'shp/CAN_adm0.shp'
    mexico_shapefile = 'shp/MEX_adm1.shp'

    canada_feature = ShapelyFeature(shpreader.Reader(canada_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)
    mexico_feature = ShapelyFeature(shpreader.Reader(mexico_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)
    ax.add_feature(canada_feature)
    ax.add_feature(mexico_feature)

    # Add interstate from local data
    reader = shpreader.Reader("shp/tl_2019_us_primaryroads.shp")
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
    timestamp_file_path = 'bfptimestamp.txt'
    with open(timestamp_file_path, 'r') as timestamp_file:
        timestamp = timestamp_file.read().strip()

    # Add timestamp to the top of the image
    fig.text(0.5, 0.845, f'{timestamp}', ha='center', fontsize=14)

    # # Read logo overlay image
    overlay2_path = 'mapoverlays/logomap.png'
    overlay2 = plt.imread(overlay2_path) 
    ax.imshow(overlay2, extent=[-77, -69, 27, 31],   transform=ccrs.PlateCarree(), alpha=1, zorder=10)

    # plt.savefig('bfpplus.png', dpi=100, bbox_inches='tight')
    plt.savefig(output_image , dpi=100, bbox_inches='tight')
    # plt.show()



# data_paths = ['afp.nc', 'nfp.nc', 'bfp.nc']

# This should be an absolute file path to nc data file
nc_file=sys.argv[1]
# this should be an absolute file path to output png image
output_image=sys.argv[2]

# the meta data for the maps is in maps directory
# so we need to be in this directory when running this script
lcrBase=os.path.dirname(__file__)
lcrBase=os.path.dirname(lcrBase)
os.chdir("maps");



color_table_paths = ['bfpplus-afp-colors-0-to-1.tbl', 'bfpplus-nfp-colors-0-to-1.tbl', 'bfpplus-bfp-colors-0-to-1.tbl']
variable_names = ['afp', 'nfp', 'bfp']
titles = ['AFP Data', 'NFP Data', 'BFP Data']



# Generate overlayed plots
create_overlayed_bfp_plot(nc_file, output_image, color_table_paths, variable_names, titles)

