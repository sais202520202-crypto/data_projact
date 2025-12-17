pip install pandas geopandas folium matplotlib shapely
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
# ① 따릉이 대여소 정보
stations = pd.read_csv("bike_station.csv")  
# 컬럼 예시: station_id, station_name, latitude, longitude

# ② 따릉이 대여 이력
rent = pd.read_csv("bike_rent.csv")  
# 컬럼 예시: rent_station_id, rent_date

# ③ 공원 위치 정보
parks = pd.read_csv("park.csv")  
# 컬럼 예시: park_name, latitude, longitude
rent_count = rent.groupby("rent_station_id").size().reset_index(name="rent_cnt")

stations = stations.merge(
    rent_count,
    left_on="station_id",
    right_on="rent_station_id",
    how="left"
)

stations["rent_cnt"] = stations["rent_cnt"].fillna(0)
stations_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations.longitude, stations.latitude),
    crs="EPSG:4326"
)

parks_gdf = gpd.GeoDataFrame(
    parks,
    geometry=gpd.points_from_xy(parks.longitude, parks.latitude),
    crs="EPSG:4326"
)
stations_gdf = stations_gdf.to_crs(epsg=5179)
parks_gdf = parks_gdf.to_crs(epsg=5179)

stations_gdf["dist_park_m"] = stations_gdf.geometry.apply(
    lambda x: parks_gdf.distance(x).min()
)
import folium
from folium.plugins import HeatMap
m = folium.Map(
    location=[stations.latitude.mean(), stations.longitude.mean()],
    zoom_start=12
)

heat_data = [
    [row.latitude, row.longitude, row.rent_cnt]
    for _, row in stations.iterrows()
]

HeatMap(heat_data).add_to(m)

m

