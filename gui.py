import tkinter as tk
from tkinter import messagebox
import serial
import threading
import math
import time

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

#  Palette 
BG          = "#0d1117"
PANEL       = "#161b22"
BORDER      = "#21262d"
ACCENT      = "#58a6ff"
ACCENT2     = "#3fb950"
WARN        = "#f78166"
TEXT        = "#e6edf3"
MUTED       = "#8b949e"
CARD_BG     = "#1c2128"

FONT_MONO   = ("Courier New", 11, "bold")
FONT_LABEL  = ("Courier New", 9)
FONT_TITLE  = ("Courier New", 18, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")

#  3-D box helpers 
def _rotation_matrix(roll_deg, pitch_deg, yaw_deg):
    r, p, y = math.radians(roll_deg), math.radians(pitch_deg), math.radians(yaw_deg)
    Rx = np.array([[1,0,0],[0,math.cos(r),-math.sin(r)],[0,math.sin(r),math.cos(r)]])
    Ry = np.array([[math.cos(p),0,math.sin(p)],[0,1,0],[-math.sin(p),0,math.cos(p)]])
    Rz = np.array([[math.cos(y),-math.sin(y),0],[math.sin(y),math.cos(y),0],[0,0,1]])
    return Rz @ Ry @ Rx

def _box_faces(R):
    """Return the 6 faces of a rotated unit box centred at origin."""
    hw, hh, hd = 1.6, 0.4, 0.9          # half-extents  (wide flat device)
    corners = np.array([
        [-hw,-hh,-hd],[ hw,-hh,-hd],[ hw, hh,-hd],[-hw, hh,-hd],
        [-hw,-hh, hd],[ hw,-hh, hd],[ hw, hh, hd],[-hw, hh, hd],
    ])
    c = (R @ corners.T).T
    faces = [
        [c[0],c[1],c[2],c[3]],   # bottom
        [c[4],c[5],c[6],c[7]],   # top
        [c[0],c[1],c[5],c[4]],   # front
        [c[2],c[3],c[7],c[6]],   # back
        [c[0],c[3],c[7],c[4]],   # left
        [c[1],c[2],c[6],c[5]],   # right
    ]
    face_colors = ["#1f6feb","#388bfd","#58a6ff","#1f6feb","#2d7dd2","#2d7dd2"]
    return faces, face_colors


#  Main Application 
class SensorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ECEN 4013 — Localization Device")
        self.root.configure(bg=BG)
        self.root.geometry("1280x820")
        self.root.minsize(1100, 700)

        self.serial_port  = "COM4"
        self.baud_rate    = 115200
        self.ser          = None
        self.running      = False
        self._ser_lock    = threading.Lock()

        # live data dict
        self._data = {k: 0.0 for k in [
            "latitude","longitude","elevation","satellites",
            "ang_vel_x","ang_vel_y","ang_vel_z",
            "accel_x","accel_y","accel_z",
            "mag_x","mag_y","mag_z",
        ]}
        # integrated orientation (simple integration for display)
        self._roll  = 0.0
        self._pitch = 0.0
        self._yaw   = 0.0
        self._last_t = None

        self.labels = {}
        self._build_menu()

    #  Menu screen 
    def _build_menu(self):
        self._clear()
        self.root.geometry("480x360")

        frame = tk.Frame(self.root, bg=BG)
        frame.place(relx=.5, rely=.5, anchor="center")

        tk.Label(frame, text="LOCALIZATION DEVICE", font=("Courier New", 20, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(0, 4))
        tk.Label(frame, text="ECEN 4013  //  Senior Design", font=FONT_LABEL,
                 bg=BG, fg=MUTED).pack(pady=(0, 28))

        # port row
        row = tk.Frame(frame, bg=BG)
        row.pack(pady=6)
        tk.Label(row, text="COM PORT", font=FONT_LABEL, bg=BG, fg=MUTED).pack(side="left", padx=(0,10))
        self._port_var = tk.StringVar(value=self.serial_port)
        e = tk.Entry(row, textvariable=self._port_var, width=10,
                     font=FONT_MONO, bg=CARD_BG, fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     highlightthickness=1, highlightcolor=ACCENT,
                     highlightbackground=BORDER)
        e.pack(side="left")

        # baud row
        row2 = tk.Frame(frame, bg=BG)
        row2.pack(pady=6)
        tk.Label(row2, text="BAUD RATE", font=FONT_LABEL, bg=BG, fg=MUTED).pack(side="left", padx=(0,10))
        self._baud_var = tk.StringVar(value=str(self.baud_rate))
        e2 = tk.Entry(row2, textvariable=self._baud_var, width=10,
                      font=FONT_MONO, bg=CARD_BG, fg=TEXT,
                      insertbackground=TEXT, relief="flat",
                      highlightthickness=1, highlightcolor=ACCENT,
                      highlightbackground=BORDER)
        e2.pack(side="left")

        tk.Frame(frame, bg=BORDER, height=1, width=320).pack(pady=20)

        self._mk_btn(frame, "▶  START DISPLAY", self._start, ACCENT).pack(fill="x", pady=4)
        self._mk_btn(frame, "✕  QUIT",           self._quit,  WARN ).pack(fill="x", pady=4)

    def _mk_btn(self, parent, text, cmd, color):
        b = tk.Button(parent, text=text, command=cmd,
                      font=FONT_HEAD, bg=PANEL, fg=color,
                      activebackground=CARD_BG, activeforeground=color,
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightbackground=color,
                      padx=14, pady=8)
        return b

    #  Start / stop 
    def _start(self):
        self.serial_port = self._port_var.get().strip() or self.serial_port
        try:
            self.baud_rate = int(self._baud_var.get().strip())
        except ValueError:
            pass

        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
        except Exception as exc:
            messagebox.showerror("Connection Error",
                                 f"Cannot open {self.serial_port}:\n{exc}")
            return

        self.running  = True
        self._roll    = 0.0
        self._pitch   = 0.0
        self._yaw     = 0.0
        self._last_t  = None
        self._build_dashboard()

        # serial reader thread
        t = threading.Thread(target=self._serial_reader, daemon=True)
        t.start()
        self._tick()

    def _stop(self):
        self.running = False
        if self.ser:
            try: self.ser.close()
            except: pass
            self.ser = None
        plt.close("all")
        self.root.geometry("480x360")
        self._build_menu()

    def _quit(self):
        self.running = False
        if self.ser:
            try: self.ser.close()
            except: pass
        plt.close("all")
        self.root.quit()

    #  Serial reader (background thread) 
    def _serial_reader(self):
        while self.running:
            try:
                raw = self.ser.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                parts = line.split(",")
                if len(parts) != 14:
                    continue
                with self._ser_lock:
                    keys = ["latitude","longitude","elevation","satellites",
                            "ang_vel_x","ang_vel_y","ang_vel_z",
                            "accel_x","accel_y","accel_z",
                            "mag_x","mag_y","mag_z"]
                    for i, k in enumerate(keys):
                        try:
                            self._data[k] = float(parts[i + 1])
                        except ValueError:
                            pass
            except Exception:
                time.sleep(0.05)

    #  Dashboard layout 
    def _build_dashboard(self):
        self._clear()
        self.root.geometry("1280x820")

        #  top bar 
        top = tk.Frame(self.root, bg=PANEL, height=52)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        tk.Label(top, text="◈  LOCALIZATION DEVICE", font=("Courier New", 14, "bold"),
                 bg=PANEL, fg=ACCENT).pack(side="left", padx=20, pady=14)

        self._status_dot = tk.Label(top, text="●", font=("Courier New", 14),
                                    bg=PANEL, fg=ACCENT2)
        self._status_dot.pack(side="left")
        self._status_lbl = tk.Label(top, text=" RECEIVING", font=FONT_LABEL,
                                    bg=PANEL, fg=ACCENT2)
        self._status_lbl.pack(side="left")

        self._mk_btn(top, "⏹  END", self._stop, WARN).pack(side="right", padx=16, pady=8)

        #  main area 
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=(8,12))

        # left column: GPS + IMU panels
        left = tk.Frame(body, bg=BG, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self._gps_panel(left)
        self._imu_panel(left)

        # right column: 3D plot + mag panel
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(12,0))

        self._orientation_panel(right)
        self._mag_panel(right)

    #  GPS card 
    def _gps_panel(self, parent):
        card = self._card(parent, "GPS  //  GNSS MODULE")
        card.pack(fill="x", pady=(0, 10))

        fields = [
            ("LATITUDE",   "latitude",   "°"),
            ("LONGITUDE",  "longitude",  "°"),
            ("ELEVATION",  "elevation",  " m MSL"),
            ("SATELLITES", "satellites", ""),
        ]
        for label, key, unit in fields:
            self._field_row(card, label, key, unit)

        # satellite lock indicator
        lock_row = tk.Frame(card, bg=CARD_BG)
        lock_row.pack(fill="x", pady=(8, 2))
        tk.Label(lock_row, text="GPS STATUS", font=FONT_LABEL,
                 bg=CARD_BG, fg=MUTED).pack(side="left", padx=8)
        self._lock_dot = tk.Label(lock_row, text="● SEARCHING", font=FONT_LABEL,
                                  bg=CARD_BG, fg=WARN)
        self._lock_dot.pack(side="right", padx=8)

    #  IMU card 
    def _imu_panel(self, parent):
        card = self._card(parent, "IMU  //  BNO055")
        card.pack(fill="x", pady=(0, 10))

        fields = [
            ("ω X", "ang_vel_x", " rad/s"),
            ("ω Y", "ang_vel_y", " rad/s"),
            ("ω Z", "ang_vel_z", " rad/s"),
            ("aX",  "accel_x",   " m/s²"),
            ("aY",  "accel_y",   " m/s²"),
            ("aZ",  "accel_z",   " m/s²"),
        ]
        for label, key, unit in fields:
            self._field_row(card, label, key, unit)

    #  Magnetic card 
    def _mag_panel(self, parent):
        card = self._card(parent, "MAGNETOMETER  //  µT")
        card.pack(fill="x", pady=(10, 0))

        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill="x")

        for col, (label, key) in enumerate([("Bx","mag_x"),("By","mag_y"),("Bz","mag_z")]):
            f = tk.Frame(inner, bg=CARD_BG)
            f.pack(side="left", expand=True, fill="x", padx=6, pady=6)
            tk.Label(f, text=label, font=FONT_LABEL, bg=CARD_BG, fg=MUTED).pack()
            lbl = tk.Label(f, text="---", font=FONT_MONO, bg=CARD_BG, fg=ACCENT)
            lbl.pack()
            self.labels[key] = lbl

    #  3D orientation plot 
    def _orientation_panel(self, parent):
        card = self._card(parent, "ORIENTATION  //  3D VISUALIZER")
        card.pack(fill="both", expand=True)

        self._fig = plt.Figure(figsize=(5, 4), dpi=96, facecolor=CARD_BG)
        self._ax  = self._fig.add_subplot(111, projection="3d")
        self._ax.set_facecolor(CARD_BG)
        self._fig.patch.set_facecolor(CARD_BG)
        self._style_3d_ax()

        canvas = FigureCanvasTkAgg(self._fig, master=card)
        canvas.get_tk_widget().configure(bg=CARD_BG, highlightthickness=0)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        self._canvas = canvas

        # angle readouts below plot
        angle_row = tk.Frame(card, bg=CARD_BG)
        angle_row.pack(fill="x", padx=10, pady=(0,8))
        self._angle_labels = {}
        for name in ("ROLL", "PITCH", "YAW"):
            f = tk.Frame(angle_row, bg=CARD_BG)
            f.pack(side="left", expand=True)
            tk.Label(f, text=name, font=FONT_LABEL, bg=CARD_BG, fg=MUTED).pack()
            lbl = tk.Label(f, text="0.0°", font=FONT_MONO, bg=CARD_BG, fg=ACCENT2)
            lbl.pack()
            self._angle_labels[name] = lbl

    def _style_3d_ax(self):
        ax = self._ax
        ax.set_xlim(-2.2, 2.2); ax.set_ylim(-2.2, 2.2); ax.set_zlim(-2.2, 2.2)
        ax.set_xlabel("X", color=MUTED, fontsize=8, labelpad=2)
        ax.set_ylabel("Y", color=MUTED, fontsize=8, labelpad=2)
        ax.set_zlabel("Z", color=MUTED, fontsize=8, labelpad=2)
        ax.tick_params(colors=MUTED, labelsize=7)
        for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
            pane.fill = False
            pane.set_edgecolor(BORDER)
        ax.grid(True, color=BORDER, linewidth=0.4, alpha=0.5)

    def _update_3d(self, roll, pitch, yaw):
        ax = self._ax
        ax.cla()
        self._style_3d_ax()

        R = _rotation_matrix(roll, pitch, yaw)
        faces, colors = _box_faces(R)

        poly = Poly3DCollection(faces, alpha=0.82, linewidths=0.6,
                                edgecolors=ACCENT)
        poly.set_facecolor(colors)
        ax.add_collection3d(poly)

        # draw axes on device
        origin = np.zeros(3)
        for vec, col, lbl in zip(R.T, [WARN, ACCENT2, ACCENT], ["X","Y","Z"]):
            v = vec * 1.8
            ax.quiver(*origin, *v, color=col, linewidth=1.8, arrow_length_ratio=0.18)
            ax.text(*(vec * 2.0), lbl, color=col, fontsize=8, fontweight="bold",
                    ha="center", va="center")

        self._canvas.draw_idle()

    #  Helpers 
    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.pack_configure()

        inner = tk.Frame(outer, bg=CARD_BG)
        inner.pack(fill="both", expand=True)

        hdr = tk.Frame(inner, bg=PANEL)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, font=("Courier New", 9, "bold"),
                 bg=PANEL, fg=MUTED, anchor="w").pack(side="left", padx=10, pady=5)

        content = tk.Frame(inner, bg=CARD_BG)
        content.pack(fill="both", expand=True, padx=2, pady=2)
        return content

    def _field_row(self, parent, label, key, unit):
        row = tk.Frame(parent, bg=CARD_BG)
        row.pack(fill="x", padx=8, pady=3)

        tk.Label(row, text=label, font=FONT_LABEL, bg=CARD_BG, fg=MUTED,
                 width=10, anchor="w").pack(side="left")

        lbl = tk.Label(row, text="---", font=FONT_MONO, bg=CARD_BG, fg=TEXT,
                       anchor="e", width=12)
        lbl.pack(side="right")
        self.labels[key] = lbl

        if unit:
            tk.Label(row, text=unit, font=FONT_LABEL, bg=CARD_BG, fg=MUTED,
                     width=6, anchor="w").pack(side="right")

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.labels = {}

    #  Main UI tick (runs on main thread) 
    def _tick(self):
        if not self.running:
            return

        with self._ser_lock:
            d = dict(self._data)

        now = time.time()

        # integrate gyro → Euler angles
        if self._last_t is not None:
            dt = now - self._last_t
            self._roll  += math.degrees(d["ang_vel_x"]) * dt
            self._pitch += math.degrees(d["ang_vel_y"]) * dt
            self._yaw   += math.degrees(d["ang_vel_z"]) * dt
        self._last_t = now

        # update label values
        fmt = {
            "latitude":   f"{d['latitude']:.6f}",
            "longitude":  f"{d['longitude']:.6f}",
            "elevation":  f"{d['elevation']:.2f}",
            "satellites": f"{int(d['satellites'])}",
            "ang_vel_x":  f"{d['ang_vel_x']:+.4f}",
            "ang_vel_y":  f"{d['ang_vel_y']:+.4f}",
            "ang_vel_z":  f"{d['ang_vel_z']:+.4f}",
            "accel_x":    f"{d['accel_x']:+.3f}",
            "accel_y":    f"{d['accel_y']:+.3f}",
            "accel_z":    f"{d['accel_z']:+.3f}",
            "mag_x":      f"{d['mag_x']:+.2f}",
            "mag_y":      f"{d['mag_y']:+.2f}",
            "mag_z":      f"{d['mag_z']:+.2f}",
        }
        for key, val in fmt.items():
            if key in self.labels:
                self.labels[key].config(text=val)

        # GPS lock indicator
        sats = int(d["satellites"])
        if sats >= 3:
            self._lock_dot.config(text=f"● LOCKED  ({sats} sats)", fg=ACCENT2)
        else:
            self._lock_dot.config(text="● SEARCHING…", fg=WARN)

        # 3D plot (update every 4 ticks → ~250 ms)
        self._tick_count = getattr(self, "_tick_count", 0) + 1
        if self._tick_count % 4 == 0:
            self._update_3d(self._roll, self._pitch, self._yaw)
            for name, val in zip(("ROLL","PITCH","YAW"),
                                 (self._roll, self._pitch, self._yaw)):
                self._angle_labels[name].config(text=f"{val % 360:.1f}°")

        self.root.after(65, self._tick)   # ~15 Hz UI refresh


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()