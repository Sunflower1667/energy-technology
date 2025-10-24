from urllib.parse import quote
import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="우리 주변의 전기차 충전소가 얼마나 있는가", layout="wide")
st.title("🔌 우리 주변의 전기차 충전소가 얼마나 있는가")

st.write("원하시는 지역을 입력하세요. (예: 서울특별시 강남구)")
user_input = st.text_input("지역 입력:", "서울특별시")

if user_input:
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(user_input)
    if location:
        lat, lon = location.latitude, location.longitude
        st.success(f"입력 위치: {user_input} (위도: {lat:.4f}, 경도: {lon:.4f})")

        API_KEY = quote("YOUR_API_KEY")  # 반드시 인코딩
        url = f"http://apis.data.go.kr/B552584/EvCharger/getChargerInfo?serviceKey={API_KEY}&numOfRows=100&pageNo=1&zcode=11&_type=json"

        response = requests.get(url)
        st.write("응답 코드:", response.status_code)

        # 먼저 JSON 파싱 시도
        try:
            data = response.json()
        except Exception:
            st.error("⚠️ JSON 응답이 아닙니다. 아래 내용을 확인하세요.")
            st.code(response.text[:500])
            st.stop()

        if "items" in data.get("items", {}):
            items = data["items"]["item"]
            df = pd.DataFrame(items)
            df["lat"] = df["lat"].astype(float)
            df["lng"] = df["lng"].astype(float)

            def within_radius(lat1, lon1, lat2, lon2, radius_km=5):
                from geopy.distance import geodesic
                return geodesic((lat1, lon1), (lat2, lon2)).km <= radius_km

            df_nearby = df[df.apply(lambda row: within_radius(lat, lon, row["lat"], row["lng"]), axis=1)]

            st.write(f"📍 {user_input} 주변 5km 이내 충전소 수: {len(df_nearby)}개")

            m = folium.Map(location=[lat, lon], zoom_start=13)
            folium.Marker([lat, lon], tooltip="현재 위치", icon=folium.Icon(color="blue")).add_to(m)

            for _, row in df_nearby.iterrows():
                folium.Marker(
                    [row["lat"], row["lng"]],
                    tooltip=f"{row['statNm']} ({row['addr']})",
                    icon=folium.Icon(color="green", icon="plug")
                ).add_to(m)

            st_folium(m, width=700, height=500)
        else:
            st.error("⚠️ API 응답에 충전소 정보가 없습니다.")
    else:
        st.error("❌ 위치를 찾을 수 없습니다. 지역명을 다시 입력해 주세요.")
