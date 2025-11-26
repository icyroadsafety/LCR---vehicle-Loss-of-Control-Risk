"""
Vector KML generator for 'bfpmerged' variable.

Usage:
    python nckml-bfp.py input.nc output.kml

This version reduces KML size by applying *stricter polygon filters
only to the AFP bins* (values < 100), so there are fewer AFP polygons
but the overall AFP area coverage is preserved as much as possible.
"""

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
MAX_SAMPLE_POINTS = 550

# Minimum polygon filters (in degrees, very approximate)
# These apply to NFP / BFP / CIP bins.
MIN_VERTICES = 6
MIN_BBOX_AREA = 0.01  # (deg lon * deg lat)

# AFP-specific polygon filters (ONLY bins for values < 100).
# Increase these to reduce the number of AFP polygons further.
AFP_MIN_VERTICES = 92
AFP_MIN_BBOX_AREA = 0.04  # 4x the default area threshold

# Threshold used to decide if an RGB color is "white"
WHITE_THRESHOLD = 0.99  # in [0,1]

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
    raise ValueError(
        "Could not find any of %r in coordinates or variables" % (candidates,)
    )


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
    """
    Convert RGBA floats [0,1] to KML color string 'aabbggrr'.
    KML expects colors in AABBGGRR, each component 00-ff hex.
    """
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


def load_tbl_colors(path):
    """
    Load a .tbl file that has lines like:

        R G B

    where R,G,B are 0-255 integers or floats.
    Lines starting with '!' or '#' or empty lines are skipped.
    Any line that cannot be parsed as 3 numbers is skipped.
    Returns a list of (r, g, b, a) in [0,1].
    """
    colors = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("!") or line.startswith("#"):
                continue
            # Split on whitespace or commas
            parts = line.replace(",", " ").split()
            if len(parts) < 3:
                continue
            try:
                r, g, b = map(float, parts[:3])
            except ValueError:
                # Something like "!This" slipped through; skip
                continue
            colors.append((r / 255.0, g / 255.0, b / 255.0, 1.0))

    if not colors:
        raise RuntimeError("No valid colors found in %s" % path)

    return colors


def sample_5_colors(colors):
    """
    From a list of RGBA colors, pick 5 evenly spaced samples
    (by index) across the table.
    """
    n = len(colors)
    if n < 5:
        # If table is very short, just repeat or interpolate.
        return (colors * 5)[:5]

    idxs = np.linspace(0, n - 1, 5)
    idxs = np.round(idxs).astype(int)
    picked = [colors[i] for i in idxs]
    return picked


def build_levels():
    """
    Build contour levels for 4 ranges:

    AFP: 0 to 0.1, then 0.1 to 100
    NFP: 100 to 100.1, then 100.1 to 200
    BFP: 200 to 200.1, then 200.1 to 300
    CIP: 300 to 300.1, then 300.1 to a large upper bound

    We create 5 bins per range (4 bins within the 0.1 span,
    plus 1 bin for the "greater than 0.1" tail). That means:

        AFP bins: (0, e1], (e1, e2], (e2, e3], (e3, 0.1], (0.1, 100]
        NFP bins: (100, ...], ..., (100.1, 200]
        etc.

    Returns sorted list of level boundaries.
    """
    def range_edges(base, tail_top):
        fine_start = base
        fine_end = base + 0.1
        step = (fine_end - fine_start) / 4.0
        return [
            base,
            base + step,
            base + 2 * step,
            base + 3 * step,
            fine_end,
            tail_top,
        ]

    edges = []
    edges += range_edges(0.0, 100.0)      # AFP (5 bins)
    edges += range_edges(100.0, 200.0)    # NFP (5 bins)
    edges += range_edges(200.0, 300.0)    # BFP (5 bins)
    edges += range_edges(300.0, 1000.0)   # CIP (5 bins, tail to big cap)

    # Unique and sorted
    levels = sorted(set(edges))
    return levels


def main():
    if len(sys.argv) != 3:
        print("Usage: python nckml-bfp.py input.nc output.kml")
        sys.exit(1)

    nc_path = sys.argv[1]
    kml_path = sys.argv[2]

    # ------------------------------------------------------------------
    # Load palette tables and sample 5 colors per scale
    # ------------------------------------------------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(script_dir)
    script_dir= os.path.join(script_dir, "maps"); 
              
    afp_colors_full = load_tbl_colors(os.path.join(script_dir, "bfpplus-afp-colors-0-to-1.tbl"))
    nfp_colors_full = load_tbl_colors(os.path.join(script_dir, "bfpplus-nfp-colors-0-to-1.tbl"))
    bfp_colors_full = load_tbl_colors(os.path.join(script_dir, "bfpplus-bfp-colors-0-to-1.tbl"))
    cip_colors_full = load_tbl_colors(os.path.join(script_dir, "bfpplus-cip-colors-0-to-1.tbl"))

    afp_colors_5 = sample_5_colors(afp_colors_full)
    nfp_colors_5 = sample_5_colors(nfp_colors_full)
    bfp_colors_5 = sample_5_colors(bfp_colors_full)
    cip_colors_5 = sample_5_colors(cip_colors_full)

    # Concatenate in AFP, NFP, BFP, CIP order
    all_rgba = afp_colors_5 + nfp_colors_5 + bfp_colors_5 + cip_colors_5
    n_bins = len(all_rgba)  # should be 20

    # Build KML colors and mark which ones are "white" (to skip)
    style_colors = []
    style_is_white = []
    for (r, g, b, a) in all_rgba:
        style_colors.append(kml_color_from_rgba(r, g, b, a))
        is_white = (r >= WHITE_THRESHOLD and
                    g >= WHITE_THRESHOLD and
                    b >= WHITE_THRESHOLD)
        style_is_white.append(is_white)

    # Style IDs
    style_ids = ["bfp%02d" % (i + 1) for i in range(n_bins)]

    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    ds = xr.open_dataset(nc_path)

    if "bfpmerged" not in ds:
        raise KeyError("Variable 'bfpmerged' not found in dataset")

    # Mask out values that should not be plotted:
    #   0, 100, 200, 300 are "no shading" for each component.
    da = ds["bfpmerged"]
    mask = ~da.isin([0.0, 100.0, 200.0, 300.0])
    da = da.where(mask)

    # Coordinate and dimension names
    lat_name = find_coord_name(da, LAT_CANDIDATES)
    lon_name = find_coord_name(da, LON_CANDIDATES)

    lat_dim = find_dim_for_coord(da, lat_name)
    lon_dim = find_dim_for_coord(da, lon_name)

    lat_vals = da[lat_name].values
    lon_vals = da[lon_name].values

    # ------------------------------------------------------------------
    # Crop to CONUS box
    # ------------------------------------------------------------------
    lat_mask = (lat_vals >= LAT_MIN) & (lat_vals <= LAT_MAX)
    lon_mask = (lon_vals >= LON_MIN) & (lon_vals <= LON_MAX)

    if not lat_mask.any() or not lon_mask.any():
        raise RuntimeError("Lat/lon masks are empty; check LAT/LON_MIN/MAX.")

    lat_idx = np.where(lat_mask)[0]
    lon_idx = np.where(lon_mask)[0]

    da = da.isel({lat_dim: lat_idx, lon_dim: lon_idx})
    lat_vals = lat_vals[lat_idx]
    lon_vals = lon_vals[lon_idx]

    n_lat = da.sizes[lat_dim]
    n_lon = da.sizes[lon_dim]

    # ------------------------------------------------------------------
    # Thin the grid to control complexity / file size
    # (applies uniformly to all variables; AFP thinning is handled later
    # by more aggressive polygon filters, not grid resolution.)
    # ------------------------------------------------------------------
    lat_step = max(1, int(round(float(n_lat) / MAX_SAMPLE_POINTS)))
    lon_step = max(1, int(round(float(n_lon) / MAX_SAMPLE_POINTS)))

    da_c = da.isel(
        {
            lat_dim: slice(0, None, lat_step),
            lon_dim: slice(0, None, lon_step),
        }
    )
    lat_c = lat_vals[0:n_lat:lat_step]
    lon_c = lon_vals[0:n_lon:lon_step]

    # Build grid for contouring
    lon_grid, lat_grid = np.meshgrid(lon_c, lat_c)

    # ------------------------------------------------------------------
    # Contouring (no display)
    # ------------------------------------------------------------------
    levels = build_levels()  # 21 boundaries -> 20 bins
    fig, ax = plt.subplots(figsize=(6, 4))
    cs = ax.contourf(lon_grid, lat_grid, da_c.values, levels=levels)
    plt.close(fig)

    allsegs = cs.allsegs  # list (per interval) of lists of Nx2 arrays (lon,lat)

    if len(allsegs) != n_bins:
        # This should normally be equal; warn if not.
        print(
            "Warning: number of contour bins (%d) != number of styles (%d)"
            % (len(allsegs), n_bins)
        )

    # ------------------------------------------------------------------
    # Write KML
    # ------------------------------------------------------------------
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write("  <Document>\n")
        title = "bfpmerged from %s" % os.path.basename(nc_path)
        f.write("    <name>%s</name>\n" % title)

        # Styles
        for style_id, color_str, is_white in zip(style_ids, style_colors, style_is_white):
            # We still define styles even for white, but we will not use them
            # (polygons for those bins will be skipped).
            f.write('    <Style id="%s">\n' % style_id)
            f.write("      <PolyStyle>\n")
            f.write("        <color>%s</color>\n" % color_str)
            f.write("        <outline>0</outline>\n")
            f.write("      </PolyStyle>\n")
            f.write("    </Style>\n")

        # Polygons, bin by bin. Higher index levels later so they sit on top.
        for level_index, seg_list in enumerate(allsegs, start=1):
            bin_idx = level_index - 1
            if bin_idx < 0 or bin_idx >= n_bins:
                continue

            # Skip bins whose color is effectively white
            if style_is_white[bin_idx]:
                continue

            style_id = style_ids[bin_idx]

            # Decide polygon filter thresholds.
            # AFP bins are indices 0..4 (values < 100).
            if 0 <= bin_idx <= 4:
                min_vertices = AFP_MIN_VERTICES
                min_area = AFP_MIN_BBOX_AREA
            else:
                min_vertices = MIN_VERTICES
                min_area = MIN_BBOX_AREA

            for poly in seg_list:
                # poly is an Nx2 array [lon, lat]
                if poly.shape[0] < min_vertices:
                    continue
                if poly_bbox_area(poly) < min_area:
                    continue

                # Ensure closed ring
                if not np.allclose(poly[0], poly[-1]):
                    poly = np.vstack([poly, poly[0]])

                f.write("    <Placemark>\n")
                f.write("      <name>bin %d</name>\n" % (bin_idx + 1))
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
    print("AFP polygon filters: min_vertices=%d, min_bbox_area=%.4f"
          % (AFP_MIN_VERTICES, AFP_MIN_BBOX_AREA))


if __name__ == "__main__":
    main()