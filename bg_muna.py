import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from collections import deque
import os

st.set_page_config(page_title="monitoring Nathara 2025", page_icon="🌍", layout="wide")

# CSS
with open("new.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Back4App endpoint
URL = "https://parseapi.back4app.com/classes/ujikelayakan"
BACK4APP_HEADERS = {
    'X-Parse-Application-Id': 'KKRKxZ4aYnuM7e8h7XhQZPUKDwZqfL9D10Z1G5J2',
    'X-Parse-REST-API-Key': 'XGPv6wGeJ92m7J9giWYxt79bmQIQ9KvxjsFGY2ji',
    'Content-Type': 'application/json',}
#Endpoint Backend
def backend_data():
    try:
        resp = requests.get(URL, headers=BACK4APP_HEADERS, params={"order": "-createdAt", "limit": 1}, timeout=6)
        if resp.status_code == 200:
            return resp.json().get("results", [])
        else:
            st.warning(f"⚠️ Gagal fetch data: {resp.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"backend tidak terhubung {e}")
        return []
        
# -------------------------
# session state init
# -------------------------
if "run" not in st.session_state:
    st.session_state.run = False
if "data" not in st.session_state:
    st.session_state.data = deque(maxlen=200)
if "trajectory_x1" not in st.session_state:
    st.session_state.trajectory_x1 = []
if "trajectory_y1" not in st.session_state:
    st.session_state.trajectory_y1 = []
if "trajectory_x2" not in st.session_state:
    st.session_state.trajectory_x2 = []
if "trajectory_y2" not in st.session_state:
    st.session_state.trajectory_y2 = []
if "last_id" not in st.session_state:
    st.session_state.last_id = None
if "current_path" not in st.session_state:
    st.session_state.current_path = None
if "akusisi_nilai" not in st.session_state:
    st.session_state.akusisi_nilai = None
if "checkpoint_active" not in st.session_state:
    st.session_state.checkpoint_active = False
if "last_checkpoint" not in st.session_state:
    st.session_state.last_checkpoint = 0

# Sidebar    
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-text">NAVIGASI LINTASAN</div>', unsafe_allow_html=True)
path = st.sidebar.radio("--", ["Lintasan A ⚓", "Lintasan B ⚓"], label_visibility="collapsed")

start_monitoring_button = st.sidebar.button("START BUTTON", key="start_monitoring_button")
stop_monitoring_button = st.sidebar.button("STOP BUTTON", key="stop_monitoring_button")

#fungsi button
if start_monitoring_button:
    st.session_state.run = True
    st.session_state.data.clear()
    st.session_state.trajectory_x1.clear()
    st.session_state.trajectory_y1.clear()
    st.session_state.trajectory_x2.clear()
    st.session_state.trajectory_y2.clear()
    st.session_state.akusisi_nilai = 0
    st.session_state.last_checkpoint = 0
    st.session_state.last_id = None
    st.sidebar.success("Monitoring started...")

if stop_monitoring_button:
    st.session_state.run = False
    st.sidebar.warning("Monitoring stopped.")

# Reset data jika path diganti
if st.session_state.current_path != path:
    st.session_state.current_path = path
    st.session_state.data.clear()
    st.session_state.trajectory_x1.clear()
    st.session_state.trajectory_y1.clear()
    st.session_state.trajectory_x2.clear()
    st.session_state.trajectory_y2.clear()
    st.session_state.akusisi_nilai = 0
    st.session_state.last_checkpoint = 0
    st.session_state.last_id = None

    if path == "Lintasan A ⚓":
        st.session_state.start_x1, st.session_state.start_y1 = 2185, 150
        st.session_state.start_x2, st.session_state.start_y2 = 2185, 150

    else:
        st.session_state.start_x1, st.session_state.start_y1 = 335, 150
        st.session_state.start_x2, st.session_state.start_y2 = 335, 150

# Judul Lintasan
if path == "Lintasan A ⚓":
    st.markdown('<div class="judul-text">LINTASAN A</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="judul-text">LINTASAN B</div>', unsafe_allow_html=True)

# Ambil data backend 
if st.session_state.run:
    st_autorefresh(interval=5000, key="main_refresh")   #waktu untuk ngerefresh (5 detik)

    latest_list = backend_data()
    if latest_list:
        latest = latest_list[0]
        unique_id = latest.get("objectId") or latest.get("createdAt")
        if unique_id and unique_id != st.session_state.last_id:
            # === CEK RESET CODE 0125 ===
            reset_code = str(latest.get("code", "")).strip()
            if reset_code == "0125":
                
                # Reset semua data ke kondisi clean
                st.session_state.data.clear()
                st.session_state.trajectory_x1.clear()
                st.session_state.trajectory_y1.clear()
                st.session_state.trajectory_x2.clear()
                st.session_state.trajectory_y2.clear()
                st.session_state.akusisi_nilai = 0
                st.session_state.last_checkpoint = 0
                st.session_state.last_id = None
                st.session_state.checkpoint_active = False
                if "visited_checkpoints" in st.session_state:
                    st.session_state.visited_checkpoints.clear()

                # Pastikan program tetap lanjut berjalan
                st.session_state.run = True
                st.session_state.current_path = path
                st.rerun()
            
            st.session_state.last_id = unique_id
            st.session_state.data.append(latest)

            def safe_float(v): #fungsi mengubah string menjadi float
                try:
                    return float(v)
                except Exception:
                    return None

            #mendefinikan data x y terbaru/ pergeseran yang berasal dari sensor
            x1 = safe_float(latest.get("x"))
            y1 = safe_float(latest.get("y"))
            x2 = safe_float(latest.get("COG"))
            y2 = safe_float(latest.get("SOG_Knot"))
    
            #akan lanjut kesini jika data x y diterima, kalau salah satu tidak ada maka tidak berjalan
            if x1 is not None and y1 is not None:
                # benambhan posisi awal dengan penggeserannya
                x1_abs = st.session_state.start_x1 + x1
                y1_abs = st.session_state.start_y1 + y1

                # Tambahkan hanya jika data berubah signifikan
                if (
                    len(st.session_state.trajectory_x1) == 0
                    or abs(x1_abs - st.session_state.trajectory_x1[-1]) > 1e-3
                    or abs(y1_abs - st.session_state.trajectory_y1[-1]) > 1e-3
                ):  
                    #menyimpan x y ke trajectory
                    st.session_state.trajectory_x1.append(x1_abs)
                    st.session_state.trajectory_y1.append(y1_abs)

            if x2 is not None and y2 is not None:
                # benambhan posisi awal dengan penggeserannya
                x2_abs = st.session_state.start_x2 + x2
                y2_abs = st.session_state.start_y2 + y2

                # Tambahkan hanya jika data berubah signifikan
                if (
                    len(st.session_state.trajectory_x2) == 0
                    or abs(x2_abs - st.session_state.trajectory_x2[-1]) > 1e-3
                    or abs(y2_abs - st.session_state.trajectory_y2[-1]) > 1e-3
                ):  
                    #menyimpan x y ke trajectory
                    st.session_state.trajectory_x2.append(x2_abs)
                    st.session_state.trajectory_y2.append(y2_abs)
# Bola lintasan
def posisi_floating_ball(path):
    if path == "A":
        green_positions = [(330, 960), (330, 1310), (450, 1715), (1040, 2250), (1200, 2250),
                           (1360, 2250), (1520, 2250), (2325, 1465), (2180, 1160), (2260, 855)]
        red_positions = [(180, 960), (180, 1310), (300, 1715), (1040, 2100), (1200, 2100),
                         (1360, 2100), (1520, 2100), (2175, 1465), (2030, 1160), (2110, 855)]
    elif path == "B":
        red_positions = [(390, 855), (470, 1160), (325, 1465), (980, 2170), (1140, 2170),
                         (1300, 2170), (1460, 2170), (2360, 1715), (2480, 1310), (2480, 960)]
        green_positions = [(190, 855), (270, 1160), (125, 1465), (980, 2370), (1140, 2370),
                           (1300, 2370), (1460, 2370), (2160, 1715), (2300, 1310), (2300, 960)]
    return red_positions, green_positions


# Plot koordinat lintasan
def koordinat_kartesius(path):
    fig, ax = plt.subplots(figsize=(13, 13))
    ax.set_xlim(0, 2600)
    ax.set_ylim(0, 2600)
    ax.set_xticks(range(0, 2600, 200))
    ax.set_yticks(range(0, 2600, 200))
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_title(f"Trajectory Map - {path}", fontsize=16, fontweight="bold")

    if path == "Lintasan A ⚓":
        start_x1, start_y1 = 2185, 150     #menetukan titik awal posisi x,y
        start_x2, start_y2 = 2185, 150     #menetukan titik awal posisi x,y
        red_positions, green_positions = posisi_floating_ball("A")
        ax.add_patch(plt.Rectangle((2100, 65), 170, 100, color='red', fill=True))
        ax.add_patch(plt.Rectangle((520, 300), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((300, 620), 100, 50, color='green', fill=True))

    elif path == "Lintasan B ⚓":
        start_x1, start_y1 = 335, 150     #menetukan titik awal posisi x,y
        start_x2, start_y2 = 335, 150     #menetukan titik awal posisi x,y
        red_positions, green_positions = posisi_floating_ball("B")
        ax.add_patch(plt.Rectangle((250, 65), 170, 100, color='green', fill=True))
        ax.add_patch(plt.Rectangle((1880, 200), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((2100, 520), 100, 50, color='green', fill=True))

    # Tambahkan bola merah dan hijau
    for pos in red_positions:
        ax.add_patch(plt.Circle(pos, 15, color='red'))
    for pos in green_positions:
        ax.add_patch(plt.Circle(pos, 15, color='green'))

    # Trajektori kapal 1
    if len(st.session_state.trajectory_x1) > 0:
        ax.plot(
            [start_x1] + st.session_state.trajectory_x1,
            [start_y1] + st.session_state.trajectory_y1,
            color='black', linestyle='--', marker='o', markersize=2
        )
        ax.scatter(st.session_state.trajectory_x1[-1],
                   st.session_state.trajectory_y1[-1],
                   color='yellow', s=200, edgecolors='black', label='Posisi Kapal')
    else:
        ax.scatter(start_x1, start_y1, color='yellow', s=200, edgecolors='black', label='Titik Awal')

     # Trajektori kapal 2
    if len(st.session_state.trajectory_x2) > 0:
        ax.plot(
            [start_x2] + st.session_state.trajectory_x2,
            [start_y2] + st.session_state.trajectory_y2,
            color='blue', linestyle='--', marker='o', markersize=2
        )
        ax.scatter(st.session_state.trajectory_x2[-1],
                   st.session_state.trajectory_y2[-1],
                   color='red', s=200, edgecolors='black', label='Posisi Kapal')
    else:
        ax.scatter(start_x1, start_y1, color='yellow', s=200, edgecolors='black', label='Titik Awal_1')
        ax.scatter(start_x2, start_y2, color='red', s=200, edgecolors='black', label='Titik Awal_2')
        
    ax.legend()

    return fig


part1, part2 = st.columns([1, 1])

with part1:
    st.markdown('<div class="judul-text">GEO-TAG INFO</div>', unsafe_allow_html=True)
    # metric placeholders
    c1, c2, c3, c4 = st.columns(4)
    day_ph = c1.metric("Day", "—")
    date_ph = c2.metric("Date", "—")
    time_ph = c3.metric("Time", "—")
    pos_ph = c4.metric("Position [x,y]", "—")

    c1, c2, c3, c4 = st.columns(4)
    sog_knot_ph = c1.metric("SOG [Knot]", "—")
    sog_kmh_ph = c2.metric("SOG [Km/h]", "—")
    coord_ph = c3.metric("Coordinate", "—")
    cog_ph = c4.metric("COG", "—")

    if len(st.session_state.data) > 0:
        last = st.session_state.data[-1]
        sog_knot_ph.metric("SOG [Knot]", f"{last.get('SOG_Knot', '—')} knot")
        sog_kmh_ph.metric("SOG [Km/h]", f"{last.get('SOG_kmperhours', '—')} km/h")
        cog_ph.metric("COG", f"{last.get('COG', '—')}°")
        day_ph.metric("Day", last.get("Day", last.get("createdAt", "—")))
        date_ph.metric("Date", last.get("Date", last.get("createdAt", "—")))
        time_ph.metric("Time", last.get("Time", last.get("createdAt", "—")))
        coord_ph.metric("Coordinate", f"S{last.get('Lattitude', '—')} E{last.get('Longitude', '—')}")
        pos_ph.metric("Position [x,y]", f"{last.get('x', '—')}, {last.get('y', '—')}")

with part2:
    st.markdown('<div class="judul-text">TRAJECTORY MAP</div>', unsafe_allow_html=True)
    fig = koordinat_kartesius(path)
    st.pyplot(fig)

