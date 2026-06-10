import tkinter as tk
import json
from datetime import datetime
import paho.mqtt.client as mqtt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==========================================
# DATA SENSOR
# ==========================================
suhu = 0
kelembapan = 0
amonia = 0

hist_suhu = []
hist_hum = []
hist_amonia = []

# ==========================================
# MQTT
# ==========================================
BROKER = "broker.hivemq.com"
TOPIC = "kandangayam/data"

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global suhu, kelembapan, amonia
    try:
        data = json.loads(msg.payload.decode())
        suhu = float(data["suhu"])
        kelembapan = float(data["kelembapan"])
        amonia = int(data["amonia"])
    except Exception as e:
        print("MQTT Error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()

# ==========================================
# GUI BASE
# ==========================================
root = tk.Tk()
root.title("Dashboard Monitoring Kandang Ayam")
root.geometry("1300x850")
root.configure(bg="#1E1E2E")

# ==========================================
# HEADER
# ==========================================
judul = tk.Label(
    root,
    text="🐔 Smart Poultry Monitoring System",
    font=("Segoe UI", 24, "bold"),
    bg="#1E1E2E",
    fg="white"
)
judul.pack(pady=10)

lbl_jam = tk.Label(
    root,
    text="",
    font=("Segoe UI", 12),
    bg="#1E1E2E",
    fg="#A0A0B8"
)
lbl_jam.pack()

# ==========================================
# CARD CONTAINER
# ==========================================
frame_card = tk.Frame(root, bg="#1E1E2E")
frame_card.pack(pady=15)

# ==========================================
# CARD SUHU
# ==========================================
card1 = tk.Frame(frame_card, bg="#FF6B6B", padx=25, pady=20)
card1.grid(row=0, column=0, padx=15)

tk.Label(card1, text="🌡 SUHU", font=("Segoe UI", 14, "bold"), bg="#FF6B6B", fg="white").pack()
lbl_suhu = tk.Label(card1, text="0 °C", font=("Segoe UI", 30, "bold"), bg="#FF6B6B", fg="white")
lbl_suhu.pack()

# ==========================================
# CARD KELEMBAPAN
# ==========================================
card2 = tk.Frame(frame_card, bg="#4D96FF", padx=25, pady=20)
card2.grid(row=0, column=1, padx=15)

tk.Label(card2, text="💧 KELEMBAPAN", font=("Segoe UI", 14, "bold"), bg="#4D96FF", fg="white").pack()
lbl_hum = tk.Label(card2, text="0 %", font=("Segoe UI", 30, "bold"), bg="#4D96FF", fg="white")
lbl_hum.pack()

# ==========================================
# CARD AMONIA
# ==========================================
card3 = tk.Frame(frame_card, bg="#6BCB77", padx=25, pady=20)
card3.grid(row=0, column=2, padx=15)

tk.Label(card3, text="☁ AMONIA", font=("Segoe UI", 14, "bold"), bg="#6BCB77", fg="white").pack()
lbl_amonia = tk.Label(card3, text="0", font=("Segoe UI", 30, "bold"), bg="#6BCB77", fg="white")
lbl_amonia.pack()

# ==========================================
# STATUS UTAMA
# ==========================================
lbl_status = tk.Label(
    root,
    text="STATUS : MENUNGGU DATA",
    font=("Segoe UI", 16, "bold"),
    bg="#1E1E2E",
    fg="white"
)
lbl_status.pack(pady=10)

# ==========================================
# STATUS RELAY & UDARA
# ==========================================
lbl_relay = tk.Label(root, text="", font=("Segoe UI", 14, "bold"), bg="#1E1E2E", fg="white")
lbl_relay.pack()

lbl_udara = tk.Label(root, text="", font=("Segoe UI", 14, "bold"), bg="#1E1E2E", fg="white")
lbl_udara.pack(pady=5)

# ==========================================
# GRAFIK MATPLOTLIB (MODERN STYLE)
# ==========================================
fig = Figure(figsize=(11, 6), dpi=100, facecolor="#1E1E2E")

ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

def style_subplot(ax, title):
    """Fungsi helper untuk kustomisasi tampilan chart agar bernuansa dark dashboard"""
    ax.set_facecolor("#252538")  # Warna background chart agak terang dari background root
    ax.set_title(title, color="white", fontsize=11, fontweight="bold", loc="left", pad=8)
    ax.tick_params(colors="#B3B3B3", labelsize=9)  # Mengubah warna teks angka sumbu X & Y
    ax.grid(True, color="#3A3A50", linestyle="--", linewidth=0.5)  # Grid tipis transparan
    
    # Menghapus bingkai kotak (spines) luar grafik biar clean
    for spine in ax.spines.values():
        spine.set_visible(False)

# ==========================================
# UPDATE DASHBOARD (LOOPING)
# ==========================================
def update_dashboard():
    # Update teks pada Card
    lbl_suhu.config(text=f"{suhu:.1f} °C")
    lbl_hum.config(text=f"{kelembapan:.1f} %")
    lbl_amonia.config(text=f"{amonia}")
    lbl_jam.config(text=datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

    # Logika Status Suhu
    if suhu < 28:
        lbl_status.config(text="🔵 SUHU RENDAH", fg="deepskyblue")
    elif suhu > 32:
        lbl_status.config(text="🔴 SUHU TINGGI", fg="red")
    else:
        lbl_status.config(text="🟢 KONDISI NORMAL", fg="lime")

    # Logika Status Relay Aktuator
    lampu = "ON" if suhu < 28 else "OFF"
    kipas = "ON" if suhu > 32 else "OFF"
    lbl_relay.config(text=f"💡 Lampu : {lampu}      🌪 Kipas : {kipas}")

    # Logika Status Kualitas Udara (MQ135)
    if amonia < 1000:
        lbl_udara.config(text="🟢 Kualitas Udara Baik", fg="lime")
    else:
        lbl_udara.config(text="🔴 Amonia Tinggi", fg="red")

    # Manajemen Riwayat Data (Maksimal 30 Data)
    hist_suhu.append(suhu)
    hist_hum.append(kelembapan)
    hist_amonia.append(amonia)

    if len(hist_suhu) > 30:
        hist_suhu.pop(0)
        hist_hum.pop(0)
        hist_amonia.pop(0)

    x = range(len(hist_suhu))

    # --- RENDER GRAFIK SUHU ---
    ax1.clear()
    style_subplot(ax1, "Grafik Tren Suhu (°C)")
    ax1.plot(x, hist_suhu, color="#FF6B6B", linewidth=2.5, marker="o", markersize=4, markerfacecolor="white")
    if hist_suhu:
        # Efek gradient fill di bawah garis
        base_y = min(hist_suhu) - 0.5 if min(hist_suhu) else 0
        ax1.fill_between(x, hist_suhu, base_y, color="#FF6B6B", alpha=0.15)

    # --- RENDER GRAFIK KELEMBAPAN ---
    ax2.clear()
    style_subplot(ax2, "Grafik Tren Kelembapan (%)")
    ax2.plot(x, hist_hum, color="#4D96FF", linewidth=2.5, marker="o", markersize=4, markerfacecolor="white")
    if hist_hum:
        base_y = min(hist_hum) - 2 if min(hist_hum) else 0
        ax2.fill_between(x, hist_hum, base_y, color="#4D96FF", alpha=0.15)

    # --- RENDER GRAFIK AMONIA ---
    ax3.clear()
    style_subplot(ax3, "Grafik Tren Gas Amonia (PPM)")
    ax3.plot(x, hist_amonia, color="#6BCB77", linewidth=2.5, marker="o", markersize=4, markerfacecolor="white")
    if hist_amonia:
        base_y = min(hist_amonia) - 5 if min(hist_amonia) else 0
        ax3.fill_between(x, hist_amonia, base_y, color="#6BCB77", alpha=0.15)

    # Mengatur jarak aman antar subplot agar teks title tidak menumpuk
    fig.tight_layout(pad=2.0)
    canvas.draw()

    # Perbarui data setiap 3 detik
    root.after(3000, update_dashboard)

# Jalankan fungsi update pertama kali
update_dashboard()

# Mulai aplikasi Tkinter
root.mainloop()
