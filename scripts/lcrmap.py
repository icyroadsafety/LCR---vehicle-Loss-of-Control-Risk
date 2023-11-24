import os,sys
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap
import numpy as np
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature



# this should be an absolute file path to nc data file
file_path=sys.argv[1]
# this should be an absolute file path for  output png image
output_image=sys.argv[2]

# The meta data for the maps is in maps directory
# So we need to be in this directory when running this script
# So given  that this file is in lcr/scripts - we wish to be in lcr/maps
lcrBase=os.path.dirname(__file__)
lcrBase=os.path.dirname(lcrBase)
os.chdir("maps");

# Define custom colors without transparency
custom_colors = [
    (188/255, 225/255, 191/255, 1),
    (113/255, 185/255, 99/255, 1),
    (81/255, 133/255, 67/255, 1),
    (237/255, 242/255, 116/255, 1),
    (218/255, 225/255, 49/255, 1),
    (226/255, 177/255, 119/255, 1),
    (214/255, 137/255, 55/255, 1),
    (234/255, 119/255, 122/255, 1),
    (215/255, 55/255, 55/255, 1),
    (241/255, 123/255, 220/255, 1),
    (235/255, 73/255, 210/255, 1),
    (230/255, 30/255, 201/255, 1)
]

# Create custom colormap
custom_cmap = ListedColormap(custom_colors, name='custom_cmap')

# Open a NetCDF file using xarray
# file_path = 'lcr.nc'
ds = xr.open_dataset(file_path)

# Set values equal to 0 to NaN
ds['lcr'] = ds['lcr'].where(ds['lcr'] != 0)

# Create a subplot with Mercator projection centered over the US
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator(central_longitude=-95)}, figsize=(20, 16))


# Set the extent for the Mercator projection
ax.set_extent([-127, -65, 21, 48])

# Read the shapefiles for Canada and Mexico
canada_shapefile = 'shp/CAN_adm0.shp'
mexico_shapefile = 'shp/MEX_adm1.shp'

# Add features for Canada and Mexico
canada_feature = ShapelyFeature(shpreader.Reader(canada_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)
mexico_feature = ShapelyFeature(shpreader.Reader(mexico_shapefile).geometries(),
                                ccrs.PlateCarree(), facecolor=(0.8, 0.8, 0.8), edgecolor='black', alpha=0.3)

# Add the Canada and Mexico features to the map
ax.add_feature(canada_feature)
ax.add_feature(mexico_feature)

# Use levels to map values 1-12 to colors 0-11 in the custom colormap and plot the data
levels = np.arange(0.5, 13.5, 1)
plot = ds['lcr'].plot(ax=ax, transform=ccrs.PlateCarree(), cmap=custom_cmap, add_colorbar=False, levels=levels, vmin=0, vmax=13)

# # Add map features such as roads, borders, states, rivers, and lakes
ax.add_feature(cfeature.NaturalEarthFeature(
    category='cultural',
    name='roads',
    scale='10m',
    facecolor='none',
    edgecolor='grey', 
    alpha=0.3
), linewidth=1.0)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=0.5)
ax.add_feature(cfeature.LAKES, edgecolor='blue', facecolor=(173/255, 216/255, 230/255), linewidth=0.1, alpha=0.9)

# Shade oceans like lakes
ax.add_feature(cfeature.NaturalEarthFeature(
    category='physical',
    name='ocean',
    scale='50m',
    facecolor=(173/255, 216/255, 230/255),  # Use the same blue color as lakes
    edgecolor='none',
    alpha=0.9
))

# Add coastlines to the map
ax.coastlines()

# # Read scale overlay image
overlay1_path = 'mapoverlays/scalemap.png'
overlay1 = plt.imread(overlay1_path) 
ax.imshow(overlay1, extent=[-115.5, -77, 21, 23],   transform=ccrs.PlateCarree(), alpha=1, zorder=10)

# # Read logo overlay image
overlay2_path = 'mapoverlays/logomap.png'
overlay2 = plt.imread(overlay2_path) 
ax.imshow(overlay2, extent=[-78, -69, 27, 31],   transform=ccrs.PlateCarree(), alpha=1, zorder=10)

# # Read map description overlay image
overlay3_path = 'mapoverlays/lcrmap-desc.png'
overlay3 = plt.imread(overlay3_path) 
ax.imshow(overlay3, extent=[-126.5, -116.5, 21, 25.5],   transform=ccrs.PlateCarree(), alpha=1, zorder=10)

# Add interstate from local data
reader = shpreader.Reader("shp/tl_2019_us_primaryroads.shp")
names = []
geoms = []
for rec in reader.records():
    if rec.attributes['FULLNAME'].startswith('I'):
        names.append(rec)
        geoms.append(rec.geometry)

# Make interstate feature
shape_feature = ShapelyFeature(geoms, ccrs.PlateCarree(), edgecolor='red', alpha=0.1, lw=1, facecolor='none')
ax.add_feature(shape_feature)

# Read timestamp from the text file
timestamp_file_path = 'lcrtimestamp.txt'
with open(timestamp_file_path, 'r') as timestamp_file:
    timestamp = timestamp_file.read().strip()

# Add timestamp to the top of the image
fig.text(0.5, 0.815, f'{timestamp}', ha='center', fontsize=14)

# Save the plot as an image file
plt.savefig(output_image, dpi=130, bbox_inches='tight')

# Display the plot
# plt.show() 
