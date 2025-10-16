import streamlit as st
import requests
import matplotlib.pyplot as plt
import time
import os
import numpy as np
import pandas as pd

st.set_page_config( page_title="monitoring-kki-2025", page_icon="🌍", layout="wide")

with open("new.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# dari back4app akun kki
# Back4App credentials
BASE_URL    = "https://parseapi.back4app.com/classes/kki_25"
headers     = {
        "X-Parse-Application-Id"    :'vuYjV2nmBIiKkc1AbXx2f8qJmTyPQF8MkBDAHbr7',
        "X-Parse-REST-API-Key"      :'ae47mM5ZIj9NXvUUADNa0wYWhLibdBL5PuTCuVJ4',
    }

#Endpoint Backend
def backend_data():
    response = requests.get(BASE_URL, headers=headers, params={"order": "-createdAt", "limit": 1})
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error(f"Failed: {response.status_code}")
        return []

# Sidebar    
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)  # kasih spasi ke bawah
st.sidebar.markdown('<div class="sidebar-text">NAVIGASI LINTASAN</div', unsafe_allow_html=True)
st.sidebar.markdown("") #nambahin space kosong
path = st.sidebar.radio("--", ["Lintasan A ⚓", "Lintasan B ⚓"], label_visibility="collapsed")
start_monitoring_button = st.sidebar.button("START BUTTON", key="start_monitoring_button")

#Header
col1, col2, col3, col4 = st.columns([0.6,4,4,1])
with col1:
    st.image('./images/logobmrt.png', width=100)
with col2:
    st.markdown('<div class="header-text">BARELANG MARINE ROBOTICS TEAM</div', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="header-text">POLITEKNIK NEGERI BATAM</div', unsafe_allow_html=True)
with col4:
    st.image('./images/logopolibatam.png', width=105)

#lintasan
if path == "Lintasan A ⚓":
    st.markdown('<div class="judul-text">LINTASAN A</div', unsafe_allow_html=True)
elif path == "Lintasan B ⚓":
    st.markdown('<div class="judul-text">LINTASAN B</div', unsafe_allow_html=True)

#gambar lintasan    
def gambar_lintasan_lomba():
    st.image('./images/lintasan.png')

part1, part2, part3= st.columns([2.1, 1, 0.9])
with part1:
    #Informasi geo-tag
    st.markdown('<div class="judul-text">GEO-TAG INFO</div', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        day_placeholder = col1.metric("Day", "Loading...")
    with col2:
        date_placeholder = col2.metric("Date", "Loading...")
    with col3:
        time_placeholder = col3.metric("Time", "Loading...")
    with col4:
        position_placeholder = col4.metric("Position [x,y]", "Loading...") 
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        sog_knot_placeholder = col1.metric("Coordinate", "Loading...")
    with col2:
        sog_kmh_placeholder = col2.metric("SOG [Knot]", "Loading...")
    with col3:
        coordinate_placeholder = col3.metric("SOG [Km/h]", "Loading...")
    with col4:
        cog_placeholder = col4.metric("COG", "Loading...")  

    st.markdown('<div class="judul-text">TRAJECTORY MAP</div>', unsafe_allow_html=True)

    #gambar map trajectory
    def koordinat_kartesius(path):
        fig, ax = plt.subplots(figsize=(13, 13))
        ax.set_xlim(0, 2500)
        ax.set_ylim(0, 2500)
        ax.set_xticks(range(0, 2600, 100))
        ax.set_yticks(range(0, 2600, 100))
        ax.grid(True)
    
        if path == "Lintasan A ⚓":
            #Titik nol : x = 2185, y = 115
            rectangle = plt.Rectangle((2100, 65), 170, 100, color='red', fill=True)
            red_positions, green_positions = posisi_floating_ball("A")

            rectangle = plt.Rectangle((2100, 65), 170, 100, color='red', fill=True)
            ax.add_patch(rectangle)

            blue_rectangle = plt.Rectangle((520, 300), 100, 50, color='blue', fill=True)
            ax.add_patch(blue_rectangle)

            small_green_rectangle = plt.Rectangle((300, 620), 100, 50, color='green', fill=True)
            ax.add_patch(small_green_rectangle)

        elif path == "Lintasan B ⚓":
            #Titik nol : x = 335, y = 115
            rectangle = plt.Rectangle((250, 65), 170, 100, color='green', fill=True)
            red_positions, green_positions = posisi_floating_ball("B")
            
            rectangle = plt.Rectangle((250, 65), 170, 100, color='green', fill=True)
            ax.add_patch(rectangle)

            blue_rectangle = plt.Rectangle((1880, 300), 100, 50, color='blue', fill=True)
            ax.add_patch(blue_rectangle)

            small_green_rectangle = plt.Rectangle((2100, 620), 100, 50, color='green', fill=True)
            ax.add_patch(small_green_rectangle)
        else:
            gambar_lintasan_lomba()
            return None, None

        ax.add_patch(rectangle)
        for pos in red_positions:
            ax.add_patch(plt.Circle(pos, 25, color='red', fill=True))
        for pos in green_positions:
            ax.add_patch(plt.Circle(pos, 25, color='green', fill=True))

        return fig, ax

    def posisi_floating_ball(path):
        if path == "A":
            green_positions = [(330, 960), (330, 1310), (450, 1715), (1040, 2250), (1200, 2250),
                            (1360, 2250), (1520, 2250), (2325, 1465), (2180, 1160), (2260, 855)]
            red_positions = [(180, 960), (180, 1310), (300, 1715), (1040, 2100), (1200, 2100),
                            (1360, 2100), (1520, 2100), (2175, 1465), (2030, 1160), (2110, 855)]
        elif path == "B":
            red_positions = [(390, 855), (470, 1160), (325, 1465), (980, 2100), (1140, 2100),
                            (1300, 2100), (1460, 2100), (2200, 1715), (2320, 1310), (2320, 960)]
            green_positions = [(240, 855), (320, 1160), (175, 1465), (980, 2250), (1140, 2250),
                            (1300, 2250), (1460, 2250), (2050, 1715), (2170, 1310), (2170, 960)]
        return red_positions, green_positions

    plot_placeholder = st.empty()
    image_placeholder = st.empty()
    fig, ax = koordinat_kartesius(path)

    #Update data
    table_entries = [] 
    trajectory_x = []
    trajectory_y = []
    floating_ball_count = 0
    trajectory_line, = ax.plot([], [], color='black', linestyle='--', marker='o', markersize=3)
    finished = False

    def update_plot():
        global trajectory_x, trajectory_y, floating_ball_count, finished, table_placeholder
        data = backend_data()

        if data:
            for data in data:
                try:
                    nilai_x = data.get('x')
                    nilai_y = data.get('y')
                    knot = data.get('SOG_Knot')
                    km_per_hours = data.get('SOG_kmperhours')
                    cog = data.get('COG')
                    day = data.get('Day')
                    date = data.get('Date')
                    time_value = data.get('Time')
                    latt = data.get('Latitude')
                    lon = data.get('Longitude')
                    yaw = data.get('Yaw')

                    if path == "Lintasan B ⚓":
                        x = data.get('x') + 335
                        y = data.get('y') +115
                        
                    else:
                        x = data.get('x') + 2185
                        y = data.get('y') + 115
                        
                    trajectory_x.append(x)
                    trajectory_y.append(y)
                    trajectory_line.set_data(trajectory_x, trajectory_y)
                    #heading_kapal(ax, x, y, yaw)
                    plot_placeholder.pyplot(fig)

                    sog_knot_placeholder.metric("SOG [Knot]", f"{knot} knot")
                    sog_kmh_placeholder.metric("SOG [Km/h]", f"{km_per_hours} km/h")
                    cog_placeholder.metric("COG", f"{cog}°")
                    day_placeholder.metric("Day", day)
                    date_placeholder.metric("Date", date)
                    time_placeholder.metric("Time", time_value)
                    coordinate_placeholder.metric("Coordinate", f" S{latt}  E{lon}")
                    position_placeholder.metric("Position [x,y]",f"{nilai_x}, {nilai_y}")


                except (TypeError, KeyError) as e:
                    st.error(f"Error processing data: {e}")          
        else:
            st.warning("No data received.")

#Position-log
with part2:
    st.markdown('<div class="judul-text">POSITION-LOG</div', unsafe_allow_html=True)
    table_placeholder = st.empty()  

with part1:
    # Main loop
    if start_monitoring_button:
        st.session_state.monitoring_active = True
        st.sidebar.markdown('<style>div.stButton > button {background-color: #2E7431; color: white;}</style>', unsafe_allow_html=True)
        st.text("Monitoring started...")
        while True:
            update_plot()
            #foto_sbox()
            #foto_ubox()
            time.sleep(1)       
    else:
        gambar_lintasan_lomba()

#image
with part3:
    st.markdown('<div class="judul-text">SURFACE IMAGE</div', unsafe_allow_html=True)
    st.image('./images/surface.jpg', width=330)

    st.markdown('<div class="judul-text">UNDERWATER IMAGE</div', unsafe_allow_html=True)
    st.image('./images/underwater.jpg', width=330)
