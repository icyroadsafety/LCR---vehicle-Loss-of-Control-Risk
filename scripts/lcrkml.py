
import sys
import os

import numpy as np
import xarray as xr

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Approximate domain for CONUS (trim dataset and keep file size down)
LON_MIN, LON_MAX = -130.0, -60.0
LAT_MIN, LAT_MAX = 20.0, 55.0

# Number of sample points along each dimension used to thin the grid
# Smaller -> coarser, larger -> finer (and bigger KML)
MAX_SAMPLE_POINTS = 1050

# Minimum polygon filters (in degrees, very approximate)
MIN_VERTICES = 6
MIN_BBOX_AREA = 0.01  # (deg lon * deg lat)

# LCR custom colors (same as your plotting script)
CUSTOM_COLORS = [
    (188/255.0, 225/255.0, 191/255.0, 1.0),
    (113/255.0, 185/255.0,  99/255.0, 1.0),
    (81/255.0,  133/255.0,  67/255.0, 1.0),
    (237/255.0, 242/255.0, 116/255.0, 1.0),
    (218/255.0, 225/255.0,  49/255.0, 1.0),
    (226/255.0, 177/255.0, 119/255.0, 1.0),
    (214/255.0, 137/255.0,  55/255.0, 1.0),
    (234/255.0, 119/255.0, 122/255.0, 1.0),
    (215/255.0,  55/255.0,  55/255.0, 1.0),
    (241/255.0, 123/255.0, 220/255.0, 1.0),
    (235/255.0,  73/255.0, 210/255.0, 1.0),
    (230/255.0,  30/255.0, 201/255.0, 1.0),
]

# Candidate coordinate names
LAT_CANDIDATES = ["lat", "latitude", "y", "yc", "nav_lat"]
LON_CANDIDATES = ["lon", "longitude", "x", "xc", "nav_lon"]


def find_coord_name(data_array, candidates):
    """Find a coordinate/variable name from a list of candidates."""
    for name in candidates:
        if name in data_array.coords:
            return name
    for name in candidates:
        if name in data_array._to_dataset().variables:
            return name
    raise ValueError("Could not find any of %r in coordinates or variables" % (candidates,))


def find_dim_for_coord(data_array, coord_name):
    """Find the dimension corresponding to a coordinate."""
    coord = data_array[coord_name]
    coord_len = coord.size

    if coord_name in data_array.dims and data_array.sizes[coord_name] == coord_len:
        return coord_name

    for dim in data_array.dims:
        if data_array.sizes[dim] == coord_len:
            return dim

    raise ValueError("Could not find a dimension matching coordinate '%s'" % coord_name)


def kml_color_from_rgba(r, g, b, a=1.0):
    """Convert RGBA floats [0,1] to KML color string 'aabbggrr'."""
    r_i = int(round(r * 255.0))
    g_i = int(round(g * 255.0))
    b_i = int(round(b * 255.0))
    a_i = int(round(a * 255.0))
    return "%02x%02x%02x%02x" % (a_i, b_i, g_i, r_i)


def poly_bbox_area(poly):
    """Simple bounding-box area in degree units."""
    xs = poly[:, 0]
    ys = poly[:, 1]
    return float((xs.max() - xs.min()) * (ys.max() - ys.min()))


def main():
    if len(sys.argv) != 3:
        print("Usage: python nckml.py input.nc output.kml")
        sys.exit(1)

    nc_path = sys.argv[1]
    kml_path = sys.argv[2]

    # --- Load data ---
    ds = xr.open_dataset(nc_path)

    if "lcr" not in ds:
        raise KeyError("Variable 'lcr' not found in dataset")

    # Mask out zeros
    lcr = ds["lcr"].where(ds["lcr"] != 0)

    # Coordinate and dimension names
    lat_name = find_coord_name(lcr, LAT_CANDIDATES)
    lon_name = find_coord_name(lcr, LON_CANDIDATES)

    lat_dim = find_dim_for_coord(lcr, lat_name)
    lon_dim = find_dim_for_coord(lcr, lon_name)

    lat_vals = lcr[lat_name].values
    lon_vals = lcr[lon_name].values

    # --- Crop to CONUS box ---
    lat_mask = (lat_vals >= LAT_MIN) & (lat_vals <= LAT_MAX)
    lon_mask = (lon_vals >= LON_MIN) & (lon_vals <= LON_MAX)

    if not lat_mask.any() or not lon_mask.any():
        raise RuntimeError("Lat/lon masks are empty; check LAT/LON_MIN/MAX.")

    lat_idx = np.where(lat_mask)[0]
    lon_idx = np.where(lon_mask)[0]

    lcr = lcr.isel({lat_dim: lat_idx, lon_dim: lon_idx})
    lat_vals = lat_vals[lat_idx]
    lon_vals = lon_vals[lon_idx]

    n_lat = lcr.sizes[lat_dim]
    n_lon = lcr.sizes[lon_dim]

    # --- Thin the grid to control complexity / file size ---
    lat_step = max(1, int(round(float(n_lat) / MAX_SAMPLE_POINTS)))
    lon_step = max(1, int(round(float(n_lon) / MAX_SAMPLE_POINTS)))

    lcr_c = lcr.isel(
        {
            lat_dim: slice(0, None, lat_step),
            lon_dim: slice(0, None, lon_step),
        }
    )
    lat_c = lat_vals[0:n_lat:lat_step]
    lon_c = lon_vals[0:n_lon:lon_step]

    # Build grid for contouring
    lon_grid, lat_grid = np.meshgrid(lon_c, lat_c)

    # Levels 1 12
    levels = np.arange(0.5, 13.5, 1.0)

    # --- Contouring (no display) ---
    fig, ax = plt.subplots(figsize=(6, 4))
    cs = ax.contourf(lon_grid, lat_grid, lcr_c.values, levels=levels)
    plt.close(fig)

    # allsegs is a list (per level) of lists of Nx2 arrays (lon,lat)
    allsegs = cs.allsegs

    # --- Prepare styles ---
    style_ids = ["lcr%d" % (i + 1) for i in range(12)]
    style_colors = [kml_color_from_rgba(*rgba) for rgba in CUSTOM_COLORS]

    with open(kml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write("  <Document>\n")
        title = "LCR from %s" % os.path.basename(nc_path)
        f.write("    <name>%s</name>\n" % title)

        # Styles
        for style_id, color_str in zip(style_ids, style_colors):
            f.write('    <Style id="%s">\n' % style_id)
            f.write("      <PolyStyle>\n")
            f.write("        <color>%s</color>\n" % color_str)
            f.write("        <outline>0</outline>\n")
            f.write("      </PolyStyle>\n")
            f.write("    </Style>\n")

        # --- Polygons ---
        # Draw level by level; higher index levels later, so they sit on top.
        for level_index, seg_list in enumerate(allsegs, start=1):
            # levels array has 12 bins -> 12 categories 1..12
            if level_index < 1 or level_index > 12:
                continue

            style_id = "lcr%d" % level_index

            for poly in seg_list:
                # poly is an Nx2 array [lon, lat]
                if poly.shape[0] < MIN_VERTICES:
                    continue
                if poly_bbox_area(poly) < MIN_BBOX_AREA:
                    continue

                # Ensure closed ring
                if not np.allclose(poly[0], poly[-1]):
                    poly = np.vstack([poly, poly[0]])

                f.write("    <Placemark>\n")
                f.write("      <name>%d</name>\n" % level_index)
                f.write("      <styleUrl>#%s</styleUrl>\n" % style_id)
                f.write("      <Polygon>\n")
                f.write("        <altitudeMode>clampToGround</altitudeMode>\n")
                f.write("        <outerBoundaryIs>\n")
                f.write("          <LinearRing>\n")
                f.write("            <coordinates>\n")

                for lon_val, lat_val in poly:
                    f.write("              %.5f,%.5f,0\n" %
                            (float(lon_val), float(lat_val)))

                f.write("            </coordinates>\n")
                f.write("          </LinearRing>\n")
                f.write("        </outerBoundaryIs>\n")
                f.write("      </Polygon>\n")
                f.write("    </Placemark>\n")

        f.write("  </Document>\n")
        f.write("</kml>\n")

    print("Wrote KML to %s" % kml_path)
    print("Grid thinning steps: lat_step=%d, lon_step=%d" % (lat_step, lon_step))


if __name__ == "__main__":
    main()