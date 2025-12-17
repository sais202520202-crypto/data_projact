import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="공공자전거 공간분석", layout="wide")

st.title("🚲 공공자전거 이용량과 공원 접근성 분석")

# =========================
# 데이터 불러오기
# =========================
@st.cache_data
def load_data():
    stations = pd.read_csv("bike_station.csv")
    rent = pd.read_csv("bike_rent.csv")
    parks = pd.read_csv("park.csv")
    return stations, rent, parks

stations, rent, parks = load_data()

# =========================
# 결측치 처리
# =========================
stations = stations.dropna(subset=["latitude", "longitude"])
rent = rent.dropna(subset=["rent_station_id"])
parks = parks.dropna(subset=["latitude", "longitude"])

# =========================
# 대여소별 이용량 계산
# =========================
rent_count = (
    rent.groupby("rent_station_id")
    .size()
    .reset_index(name="rent_cnt")
)

stations = stations.merge(
    rent_count,
    left_on="station_id",
    right_on="rent_station_id",
    how="left"
)

stations["rent_cnt"] = stations["rent_cnt"].fillna(0)

# =========================
# GeoDataFrame 변환
# =========================
stations_gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(
        stations.longitude,
        stations.latitude
    ),
    crs="EPSG:4326"
)

parks_gdf = gpd.GeoDataFrame(
    parks,
    geometry=gpd.points_from_xy(
        parks.longitude,
        parks.latitude
    ),
    crs="EPSG:4326"
)

# 거리 계산용 좌표계 변환
stations_gdf = stations_gdf.to_crs(epsg=5179)
parks_gdf = parks_gdf.to_crs(epsg=5179)

# =========================
# 공원까지 최소 거리 계산
# =========================
stations_gdf["dist_park_m"] = stations_gdf.geometry.apply(
    lambda x: parks_gdf.distance(x).min()
)

# =========================
# 지도 시각화 (히트맵)
# =========================
st.subheader("📍 공공자전거 이용량 히트맵")

m = folium.Map(
    location=[
        stations.latitude.mean(),
        stations.longitude.mean()
    ],
    zoom_start=12
)

heat_data = [
    [row.latitude, row.longitude, row.rent_cnt]
    for _, row in stations.iterrows()
]

HeatMap(heat_data).add_to(m)

st_folium(m, width=1000, height=600)

# =========================
# 결과 요약
# =========================
st.subheader("📊 분석 요약")

col1, col2, col3 = st.columns(3)

col1.metric("대여소 수", len(stations))
col2.metric(
    "평균 공원까지 거리 (m)",
    f"{stations_gdf['dist_park_m'].mean():.1f}"
)
col3.metric(
    "평균 대여 횟수",
    f"{stations['rent_cnt'].mean():.1f}"
)

