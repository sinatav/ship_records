"""
Main capabilities:
- load stops table and place -> lat/lon lookup
- parse voyage steps string into ordered places
- call marnet_geograph.get_shortest_path(...) to obtain coordinate paths
- detect intersection with a polygon (Suez Canal) and attempt simple alternative routes
- plot results on a world map (GeoPandas + Matplotlib) and save PNGs

Notes:
- This module assumes `marnet_geograph` (from scgraph.geographs.marnet) is available and
  provides get_shortest_path(origin_node, destination_node) -> dict with 'coordinate_path'.
- Requires geopandas, shapely, matplotlib, pandas.
- Input file names are parameterized.
"""

from typing import List, Dict, Tuple, Optional, Any
import os
import pickle
import re
import logging

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString

# external (from your environment)
try:
    from scgraph.geographs.marnet import marnet_geograph
except Exception:
    marnet_geograph = None  # will raise later if used

logger = logging.getLogger(__name__)


# ---------- helpers ----------
def load_places(place_csv_path: str) -> pd.DataFrame:
    """Load places CSV with columns place_name, lat, lon (keeps those columns)."""
    df = pd.read_csv(place_csv_path)
    for col in ['place_name', 'lat', 'lon']:
        if col not in df.columns:
            raise ValueError(f"place CSV missing required column '{col}'")
    return df[['place_name', 'lat', 'lon']].dropna()


def load_latlon_pickle(pkl_path: str) -> Dict[str, List[float]]:
    """Load existing place -> [lat, lon] mapping from pickle. If file missing, return empty dict."""
    if not os.path.exists(pkl_path):
        logger.warning("lat/lon pickle does not exist: %s", pkl_path)
        return {}
    with open(pkl_path, 'rb') as f:
        return pickle.load(f)


def update_latlon_map(pl_map: Dict[str, List[float]], places_df: pd.DataFrame) -> Dict[str, List[float]]:
    """
    Update mapping with rows from places_df. places_df rows expected: place_name, lat, lon
    """
    pl = dict(pl_map)
    for _, row in places_df.iterrows():
        pl[row['place_name']] = [float(row['lat']), float(row['lon'])]
    return pl


def parse_steps_text(steps: str) -> List[str]:
    """
    We try to be tolerant of separators like ',', ';', '-', '->', '|'.
    """
    if not isinstance(steps, str):
        raise ValueError("steps must be a string")
    # replace common separators with dash, but keep names intact
    s = steps.strip()
    # unify arrows and pipes to dash
    s = s.replace("->", "-").replace("|", "-").replace(";", "-")
    # replace commas only where they separate items (rough approach)
    s = re.sub(r',\s*', '-', s)
    # now split on dashes, but avoid splitting hyphenated words with letters on both sides joined (approx)
    parts = [p.strip().replace("?", "") for p in re.split(r'\s*-\s*', s) if p.strip()]
    return parts


# ---------- core route building ----------
def get_leg_path(origin: Tuple[float, float], destination: Tuple[float, float]) -> List[Tuple[float, float]]:
    """
    Query marnet_geograph for a shortest path between two coordinates.
    origin/destination: (lat, lon)
    returns: list of (lat, lon) points (coordinate_path).
    """
    if marnet_geograph is None:
        raise RuntimeError("marnet_geograph not available in environment. Import failed.")

    origin_node = {"latitude": float(origin[0]), "longitude": float(origin[1])}
    dest_node = {"latitude": float(destination[0]), "longitude": float(destination[1])}
    res = marnet_geograph.get_shortest_path(origin_node=origin_node, destination_node=dest_node)
    # expected key 'coordinate_path'
    if 'coordinate_path' not in res:
        raise RuntimeError("marnet_geograph response missing 'coordinate_path'")
    return [(float(p[0]), float(p[1])) for p in res['coordinate_path']]


def assemble_full_path_from_stops(
    stops: List[str],
    pl_map: Dict[str, List[float]],
    avoid_polygons: Optional[List[Polygon]] = None,
    suse_alt_try_offset_deg: float = 2.0
) -> Tuple[List[Tuple[float, float]], List[str]]:
    """
    For an ordered list of place names 'stops' build a concatenated coordinate path.
    If a leg intersects any polygon in avoid_polygons (e.g. Suez Canal), attempt a simple alternative:
      - try routing via a waypoint offset north by suse_alt_try_offset_deg
      - if that still intersects, try offset south
      - if still intersects, log and include the original path (no perfect avoidance)
    Returns tuple (path_points, missing_places_list)
    """
    if avoid_polygons is None:
        avoid_polygons = []

    missing = []
    coords_stops: List[Tuple[float, float]] = []
    for name in stops:
        if name not in pl_map:
            missing.append(name)
            coords_stops.append((None, None))
        else:
            coords_stops.append(tuple(pl_map[name]))  # (lat, lon)

    if missing:
        logger.warning("Missing coordinates for places: %s", missing)

    full_output: List[Tuple[float, float]] = []
    # iterate legs
    for i in range(len(coords_stops) - 1):
        origin = coords_stops[i]
        dest = coords_stops[i + 1]
        if origin[0] is None or dest[0] is None:
            logger.warning("Skipping leg %s -> %s due to missing coords", stops[i], stops[i+1])
            continue

        # primary path
        try:
            leg = get_leg_path(origin, dest)
        except Exception as e:
            logger.exception("Error obtaining path for leg %s -> %s: %s", stops[i], stops[i + 1], e)
            continue

        # convert leg to shapely LineString (note coordinate ordering as (lon, lat))
        leg_line = LineString([(p[1], p[0]) for p in leg])

        intersects_any = any(leg_line.intersects(poly) for poly in avoid_polygons)

        if not intersects_any:
            full_output.extend(leg)
            continue

        # if intersects, try alternatives via offset waypoint(s)
        logger.info("Leg %s -> %s intersects avoid polygons, trying alternative via offset waypoints", stops[i], stops[i+1])
        tried = False
        for sign in (+1, -1):
            waypoint_lat = origin[0] + sign * suse_alt_try_offset_deg
            waypoint_lon = (origin[1] + dest[1]) / 2.0  # center longitude between origin/dest
            waypoint = (waypoint_lat, waypoint_lon)
            try:
                first = get_leg_path(origin, waypoint)
                second = get_leg_path(waypoint, dest)
            except Exception:
                continue

            combined_line = LineString([(p[1], p[0]) for p in (first + second)])
            if not any(combined_line.intersects(poly) for poly in avoid_polygons):
                logger.info("Alternative via %s succeeded for leg %s -> %s", waypoint, stops[i], stops[i+1])
                full_output.extend(first)
                full_output.extend(second)
                tried = True
                break
        if not tried:
            # fallback: keep original leg (give up on avoidance)
            logger.warning("Could not find alternative avoiding polygons for leg %s -> %s. Using original path.", stops[i], stops[i+1])
            full_output.extend(leg)

    return full_output, missing


# ---------- plotting ----------
def plot_route_on_world(
    path: List[Tuple[float, float]],
    stops_coords: List[Tuple[float, float]],
    stops_names: List[str],
    shapefile_geojson_path: str,
    voyage_code: str,
    out_path: Optional[str] = None,
    figsize: Tuple[int, int] = (15, 10),
    markersize_points: int = 10,
    route_markersize: int = 2
) -> str:
    """
    Plot the provided path (sequence of (lat, lon) tuples) on the world map provided
    by shapefile_geojson_path (NaturalEarth geojson). Also plot stop points (stops_coords).
    Saves figure to voyage_code + .png by default or returns the path to the saved image.
    """
    world = gpd.read_file(shapefile_geojson_path)
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    world.plot(ax=ax, color='white', edgecolor='black')

    if not path:
        raise ValueError("path is empty")

    lats, lons = zip(*path)
    ax.plot(lons, lats, color='red', linewidth=0, marker='o', markersize=route_markersize)

    # plot stops and index labels
    for i, (lat, lon) in enumerate(stops_coords, start=1):
        ax.plot(lon, lat, color='cyan', marker='o', markersize=markersize_points)
        ax.text(lon, lat, str(i), fontsize=12, ha='center', va='center', color='blue')

    # annotate start and end
    ax.text(lons[0], lats[0], 'Start', fontsize=12, ha='right', color='green')
    ax.text(lons[-1], lats[-1], 'End', fontsize=12, ha='left', color='green')

    plt.title(f'Shortest Path on World Map — {voyage_code}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    file_name = out_path or f"{voyage_code}_vis.png"
    plt.savefig(file_name, dpi=600, bbox_inches='tight')
    plt.close(fig)
    logger.info("Saved visualization to %s", file_name)
    return file_name


# ---------- top-level convenience function ----------
def visualize_voyage_from_files(
    voyage_code: str,
    mother_table_csv: str = "MOTHER_TABLE.csv",
    places_csv: str = "place_202407091342.csv",
    latlon_pkl: str = "lat_lon.pkl",
    shapefile_geojson_path: str = os.path.join("natural_earth_vector", "natural-earth-vector-5.0.1", "geojson", "ne_110m_admin_0_countries.geojson"),
    sues_canal_polygon_coords: Optional[List[Tuple[float, float]]] = None,
    out_prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Returns dictionary with keys:
      - 'path' : final path list of (lat, lon)
      - 'missing_places' : list
      - 'saved_fig' : filename
    """
    # load mother table
    stops_df = pd.read_csv(mother_table_csv).drop(columns=[c for c in ['Unnamed: 0'] if c in pd.read_csv(mother_table_csv).columns], errors='ignore').dropna(how='all', axis=0).dropna(how='all', axis=1)
    places_df = load_places(places_csv)
    pl_map = load_latlon_pickle(latlon_pkl)
    pl_map = update_latlon_map(pl_map, places_df)

    # find steps for voyage code
    if 'voyage_code' not in stops_df.columns:
        raise ValueError("MOTHER_TABLE.csv missing 'voyage_code' column")
    row = stops_df[stops_df['voyage_code'] == voyage_code]
    if row.empty:
        raise ValueError(f"Voyage code '{voyage_code}' not present in {mother_table_csv}")
    steps = list(row['steps'])[0]

    # parse steps
    stops = parse_steps_text(steps)
    logger.info("Voyage steps: %s", stops)

    # build avoid polygons list (Suez)
    avoid_polys = []
    if sues_canal_polygon_coords is None:
        # default Suez sample polygon (user may adjust to real coordinates)
        sues_canal_polygon_coords = [(32.5, 30.0), (32.6, 30.0), (32.6, 31.0), (32.5, 31.0), (32.5, 30.0)]
    sues_poly = Polygon([(lon, lat) for (lon, lat) in sues_canal_polygon_coords])  # shapely expects (x,y) = (lon,lat)
    avoid_polys.append(sues_poly)

    # assemble full path and detect missing places
    full_path, missing = assemble_full_path_from_stops(stops=stops, pl_map=pl_map, avoid_polygons=avoid_polys)

    # prepare stops coords for plotting (only places that exist)
    stops_coords = [tuple(pl_map[s]) for s in stops if s in pl_map]

    out_name = out_prefix or voyage_code
    saved = plot_route_on_world(full_path, stops_coords, stops, shapefile_geojson_path, out_name)

    # Also attempt alternative calculation and save alt image
    alt_path, _ = assemble_full_path_from_stops(stops=stops, pl_map=pl_map, avoid_polygons=avoid_polys, suse_alt_try_offset_deg=3.0)
    saved_alt = plot_route_on_world(alt_path, stops_coords, stops, shapefile_geojson_path, out_name + "_alt")

    return {"path": full_path, "missing_places": missing, "saved_fig": saved, "saved_fig_alt": saved_alt}


if __name__ == "__main__":
    # small demo when run as script (adjust voyage_code)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--voyage", "-v", required=True, help="voyage code to visualize")
    parser.add_argument("--mother", default="MOTHER_TABLE.csv")
    parser.add_argument("--places", default="place_202407091342.csv")
    parser.add_argument("--latlon", default="lat_lon.pkl")
    parser.add_argument("--nepath", default=os.path.join("natural_earth_vector", "natural-earth-vector-5.0.1", "geojson", "ne_110m_admin_0_countries.geojson"))
    parser.add_argument("--out", default=None, help="prefix for output images")
    args = parser.parse_args()

    # run visualization
    res = visualize_voyage_from_files(args.voyage, mother_table_csv=args.mother, places_csv=args.places, latlon_pkl=args.latlon, shapefile_geojson_path=args.nepath, out_prefix=args.out)
    print("Saved images:", res.get('saved_fig'), res.get('saved_fig_alt'))
