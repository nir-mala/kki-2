import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from collections import deque

st.set_page_config(page_title="monitoring-kki-2025", page_icon="🌍", layout="wide")

# CSS
with open("new.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Back4App credentials
BASE_URL = "https://parseapi.back4app.com/classes/kki_25"
HEADERS = {
    "X-Parse-Application-Id": 'vuYjV2nmBIiKkc1AbXx2f8qJmTyPQF8MkBDAHbr7',
    "X-Parse-REST-API-Key": 'ae47mM5ZIj9NXvUUADNa0wYWhLibdBL5PuTCuVJ4',
}

#Endpoint Backend
def backend_data():
    resp = requests.get(BASE_URL, headers=HEADERS, params={"order": "-createdAt", "limit": 1}, timeout=6)
    if resp.status_code == 200:
        return resp.json().get("results", [])
    else:
        st.error(f"Failed fetch: {resp.status_code}")
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
    st.session_state.last_id = None

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

# Gambar lintasan jika tidak ada data
def gambar_lintasan_lomba():
    st.image('./images/lintasan.png')

# -------------------------
# Ambil data backend tiap 2 detik
# -------------------------
if st.session_state.run:
    st_autorefresh(interval=2000, key="main_refresh")

    latest_list = backend_data()
    if latest_list:
        latest = latest_list[0]
        unique_id = latest.get("objectId") or latest.get("createdAt")
        if unique_id and unique_id != st.session_state.last_id:
            st.session_state.last_id = unique_id
            st.session_state.data.append(latest)

            def safe_float(v):
                try:
                    return float(v)
                except Exception:
                    return None

            x = safe_float(latest.get("Position_X"))
            y = safe_float(latest.get("Position_Y"))
            if x is not None and y is not None:
                st.session_state.trajectory_x.append(x)
                st.session_state.trajectory_y.append(y)

# -------------------------
# Bola lintasan
# -------------------------
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

# -------------------------
# Plot koordinat lintasan
# -------------------------
def koordinat_kartesius(path):
    fig, ax = plt.subplots(figsize=(13, 13))
    ax.set_xlim(0, 2600)
    ax.set_ylim(0, 2600)
    ax.set_xticks(range(0, 2600, 200))
    ax.set_yticks(range(0, 2600, 200))
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.set_title(f"Trajectory Map - {path}", fontsize=16, fontweight="bold")

    if path == "Lintasan A ⚓":
        red_positions, green_positions = posisi_floating_ball("A")
        ax.add_patch(plt.Rectangle((2100, 65), 170, 100, color='red', fill=True))
        ax.add_patch(plt.Rectangle((520, 300), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((300, 620), 100, 50, color='green', fill=True))

    elif path == "Lintasan B ⚓":
        red_positions, green_positions = posisi_floating_ball("B")
        ax.add_patch(plt.Rectangle((250, 65), 170, 100, color='green', fill=True))
        ax.add_patch(plt.Rectangle((1880, 300), 100, 50, color='blue', fill=True))
        ax.add_patch(plt.Rectangle((2100, 620), 100, 50, color='green', fill=True))

    # Tambahkan bola merah dan hijau
    for pos in red_positions:
        ax.add_patch(plt.Circle(pos, 25, color='red'))
    for pos in green_positions:
        ax.add_patch(plt.Circle(pos, 25, color='green'))

    # Tambahkan trajectory (jalur kapal)
    if len(st.session_state.trajectory_x) > 1:
        ax.plot(
            st.session_state.trajectory_x,
            st.session_state.trajectory_y,
            color='black', linestyle='--', marker='o', markersize=2
        )

    return fig

# -------------------------
# Layout utama
# -------------------------
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
        pos_ph.metric("Position [x,y]", f"{last.get('Position_X', '—')}, {last.get('Position_Y', '—')}")

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
            'Day', 'Date', 'Time', 'Position_X', 'Position_Y', 'Yaw',
            'COG', 'SOG_Knot', 'SOG_kmperhours', 'Latitude', 'Longitude'
        ]

        # Tampilkan hanya kolom yang tersedia di df
        available_cols = [c for c in cols if c in df.columns]

        # Menampilkan 20 data terakhir dengan kolom terbatas
        st.dataframe(df[available_cols].tail(20), width='stretch')
    else:
        st.info("Belum ada data yang ditampilkan. Tekan START untuk memulai monitoring.")


# Part 3: IMAGES
with part3:
    st.markdown('<div class="judul-text">SURFACE IMAGE</div>', unsafe_allow_html=True)
    try:
        st.image('./images/surface.jpg', width=330)
        st.markdown('<div class="judul-text">UNDERWATER IMAGE</div>', unsafe_allow_html=True)
        st.image('./images/underwater.jpg', width=330)
    except:
        st.info("Image not found.")
