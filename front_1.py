import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from collections import deque
import os

#
st.set_page_config(page_title="monitoring kki 2025", page_icon="🌍", layout="wide")

# CSS
with open("new.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Back4App endpoint
BASE_URL = "https://parseapi.back4app.com/classes/Trial"
HEADERS = {
    "X-Parse-Application-Id": '0Sso192eaYKycvvXtqrh4RYC9OCZV4SE1OUpNi8a',
    "X-Parse-REST-API-Key": '3p3PJx6i57cIBZqpxchpbZVjNbkPKoQ8mSR5eGS2',
}

#Endpoint Backend
def backend_data():
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params={"order": "-createdAt", "limit": 1}, timeout=6)
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
if "trajectory_x" not in st.session_state:
    st.session_state.trajectory_x = []
if "trajectory_y" not in st.session_state:
    st.session_state.trajectory_y = []
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
    st.session_state.trajectory_x.clear()
    st.session_state.trajectory_y.clear()
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
    st.session_state.trajectory_x.clear()
    st.session_state.trajectory_y.clear()
    st.session_state.akusisi_nilai = 0
    st.session_state.last_checkpoint = 0
    st.session_state.last_id = None

    if path == "Lintasan A ⚓":
        st.session_state.start_x, st.session_state.start_y = 2185, 150
    else:
        st.session_state.start_x, st.session_state.start_y = 335, 150

# Header
col1, col2, col3, col4 = st.columns([0.6, 4, 4, 1])
with col1:
    st.image('./images/logobmrt.png', width=100)
with col2:
    st.markdown('<div class="header-text">BARELANG MARINE ROBOTICS TEAM</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="header-text">POLITEKNIK NEGERI BATAM</div>', unsafe_allow_html=True)
with col4:
    st.image('./images/logopolibatam.png', width=105)

# Judul Lintasan
if path == "Lintasan A ⚓":
    st.markdown('<div class="judul-text">LINTASAN A</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="judul-text">LINTASAN B</div>', unsafe_allow_html=True)

# Ambil data backend 
if st.session_state.run:
    st_autorefresh(interval=2000, key="main_refresh")   #waktu untuk ngerefresh (5 detik)

    latest_list = backend_data()
    if latest_list:
        latest = latest_list[0]
        unique_id = latest.get("objectId") or latest.get("createdAt")
        if unique_id and unique_id != st.session_state.last_id:
            st.session_state.last_id = unique_id
            st.session_state.data.append(latest)

            def safe_float(v): #fungsi mengubah string menjadi float
                try:
                    return float(v)
                except Exception:
                    return None

            #mendefinikan data x y terbaru/ pergeseran yang berasal dari sensor
            x = safe_float(latest.get("x"))
            y = safe_float(latest.get("y"))

            #akan lanjut kesini jika data x y diterima, kalau salah satu tidak ada maka tidak berjalan
            if x is not None and y is not None:
                # benambhan posisi awal dengan penggeserannya
                x_abs = st.session_state.start_x + x
                y_abs = st.session_state.start_y + y

                # Tambahkan hanya jika data berubah signifikan
                if (
                    len(st.session_state.trajectory_x) == 0
                    or abs(x_abs - st.session_state.trajectory_x[-1]) > 1e-3
                    or abs(y_abs - st.session_state.trajectory_y[-1]) > 1e-3
                ):  
                    #menyimpan x y ke trajectory
                    st.session_state.trajectory_x.append(x_abs)
                    st.session_state.trajectory_y.append(y_abs)

# Bola lintasan
def posisi_floating_ball(path):
    if path == "A":
        green_positions = [(330, 960), (330, 1310), (450, 1715), (1040, 2250), (1200, 2250),
                           (1360, 2250), (1520, 2250), (2325, 1465), (2180, 1160), (2260, 855)]
        red_positions = [(180, 960), (180, 1310), (300, 1715), (1040, 2100), (1200, 2100),
                         (1360, 2100), (1520, 2100), (2175, 1465), (2030, 1160), (2110, 855)]
    elif path == "B":
        red_positions = [(440, 855), (520, 1160), (375, 1465), (980, 2100), (1140, 2100),
                         (1300, 2100), (1460, 2100), (2300, 1715), (2420, 1310), (2420, 960)]
        green_positions = [(240, 855), (320, 1160), (175, 1465), (980, 2300), (1140, 2300),
                           (1300, 2300), (1460, 2300), (2100, 1715), (2220, 1310), (2220, 960)]
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
        start_x, start_y = 2185, 150     #menetukan titik awal posisi x,y
        red_positions, green_positions = posisi_floating_ball("A")
        check_points = [(1800, 900), (1300, 1600), (500, 2000)] # posisi check point lintasan A
        ax.add_patch(plt.Rectangle((2100, 65), 170, 100, color='red', fill=True))
        ax.add_patch(plt.Rectangle((520, 300), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((300, 620), 100, 50, color='green', fill=True))

    elif path == "Lintasan B ⚓":
        start_x, start_y = 335, 150     #menetukan titik awal posisi x,y
        red_positions, green_positions = posisi_floating_ball("B")
        check_points = [(700, 890), (1500, 1300), (2100, 2000)]  # posisi check point lintasan B
        ax.add_patch(plt.Rectangle((250, 65), 170, 100, color='green', fill=True))
        ax.add_patch(plt.Rectangle((1880, 300), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((2100, 620), 100, 50, color='green', fill=True))

    # Tambahkan bola merah dan hijau
    for pos in red_positions:
        ax.add_patch(plt.Circle(pos, 15, color='red'))
    for pos in green_positions:
        ax.add_patch(plt.Circle(pos, 15, color='green'))

    # Trajektori
    if len(st.session_state.trajectory_x) > 0:
        ax.plot(
            [start_x] + st.session_state.trajectory_x,
            [start_y] + st.session_state.trajectory_y,
            color='black', linestyle='--', marker='o', markersize=2
        )
        ax.scatter(st.session_state.trajectory_x[-1],
                   st.session_state.trajectory_y[-1],
                   color='yellow', s=200, edgecolors='black', label='Posisi Kapal')
        ax.legend()
    else:
        ax.scatter(start_x, start_y, color='yellow', s=200, edgecolors='black', label='Titik Awal')
        ax.legend()

    return fig

# Layout utama---
part1, part2, part3 = st.columns([2.1, 1, 0.9])

# Part 1: GEO + MAP
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
        coord_ph.metric("Coordinate", f"S{last.get('Latitude', '—')} E{last.get('Longitude', '—')}")
        pos_ph.metric("Position [x,y]", f"{last.get('x', '—')}, {last.get('y', '—')}")

    st.markdown('<div class="judul-text">TRAJECTORY MAP</div>', unsafe_allow_html=True)
    fig = koordinat_kartesius(path)
    st.pyplot(fig)

# Part 2: POSITION LOG
with part2:
    st.markdown('<div class="judul-text">POSITION-LOG</div>', unsafe_allow_html=True)
    
    if len(st.session_state.data) > 0:
        df = pd.DataFrame(list(st.session_state.data))

        # Pilih hanya kolom dari 'Day' sampai 'Longitude'
        cols = [
            'Day', 'Date', 'Time', 'x', 'y', 'COG', 'SOG_Knot', 'SOG_kmperhours', 'Latitude', 'Longitude'
        ]

        # Tampilkan hanya kolom yang tersedia di df
        available_cols = [c for c in cols if c in df.columns]

        # Menampilkan 20 data terakhir dengan kolom terbatas
        st.dataframe(df[available_cols].tail(20).iloc[::-1].reset_index(drop=True))
    else:
        st.info("Belum ada data yang ditampilkan. Tekan START untuk memulai monitoring.")

    # --- CHECKPOINT INDICATOR ---
    st.markdown('<div class="judul-text">CHECKPOINT</div>', unsafe_allow_html=True)

    checkpoints_A = [
        (2110, 2260, 840, 870),       # A1
        (2030, 2180, 1145, 1175),     # A2
        (2175, 2325, 1400, 1600),     # A3
    ]

    checkpoints_B = [
        (240, 430, 800, 1000),         # B1
        (320, 470, 1145, 1175),       # B2
        (160, 400, 1400, 1500),       # B3
        (900, 1100, 2000, 2400),       # B4
        (1100, 1300, 2000, 2400),       # B5
        (1300, 1500, 2000, 2400),       # B6
        (1500, 1700, 2000, 2400),       # B7
        (2000, 2400, 1600, 1800),       # B8
        (2200, 2450, 1200, 1400),       # B9
        (2200, 2450, 1600, 1800),       # B10
    ]

    # Pilih lintasan aktif dari session_state
    #lintasan_aktif = st.session_state.get("selected_lintasan", "Lintasan A ⚓")
    checkpoints = checkpoints_A if path == "Lintasan A ⚓" else checkpoints_B

    # --- LOGIKA PENINGKATAN NILAI ---
    if len(st.session_state.data) > 0:
        last = st.session_state.data[-1]
        try:
            x_val = float(last.get("x", 0))
            y_val = float(last.get("y", 0))

            # Posisi absolut
            x_abs = st.session_state.start_x + x_val
            y_abs = st.session_state.start_y + y_val

            # Cek checkpoint aktif sekarang
            checkpoint_now = 0
            for i, (xmin, xmax, ymin, ymax) in enumerate(checkpoints, start=1):
                if xmin < x_abs < xmax and ymin < y_abs < ymax:
                    checkpoint_now = i
                    break

            # Jika kapal MASUK ke checkpoint baru
            if checkpoint_now != 0 and not st.session_state.checkpoint_active:
                if checkpoint_now != st.session_state.last_checkpoint:
                    st.session_state.akusisi_nilai += 1
                    st.session_state.last_checkpoint = checkpoint_now
                    st.session_state.checkpoint_active = True

            # Jika kapal KELUAR dari semua checkpoint → reset flag
            elif checkpoint_now == 0:
                st.session_state.checkpoint_active = False
                st.session_state.last_checkpoint = 0

        except Exception:
            pass
    
    # Tampilkan hasil
    st.write(f'<div class="ind-text"> POINT = {st.session_state.akusisi_nilai}</div>', unsafe_allow_html=True)


# Part 3: IMAGES
with part3:
        # SURFACE IMAGE
    st.markdown('<div class="judul-text">SURFACE IMAGE</div>', unsafe_allow_html=True)
    surface_path = './images/sbox1.jpg'
    if os.path.exists(surface_path):
        st.image(surface_path)
    else:
        st.image('./images/surface.jpg')  # gambar cadangan

    # UNDERWATER IMAGE
    st.markdown('<div class="judul-text">UNDERWATER IMAGE</div>', unsafe_allow_html=True)
    underwater_path = './images/ubox.jpg'
    if os.path.exists(underwater_path):
        st.image(underwater_path)
    else:
        st.image('./images/underwater.jpg')  # gambar cadangan
