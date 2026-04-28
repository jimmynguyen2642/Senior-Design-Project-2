import tkinter as tk
from tkinter import messagebox
import random
import serial

BG_COLOR = "#4a4c4d"
CARD_COLOR = "#ffffff"
TITLE_COLOR = "#1f3b5b"
SECTION_COLOR = "#2a5d84"
TEXT_COLOR = "#222222"
VALUE_COLOR = "#0b3d91"

def get_mock_data():
    return {
        "latitude": f"{36.123456 + random.uniform(-0.0001, 0.0001):.6f}",
        "longitude": f"{-97.123456 + random.uniform(-0.0001, 0.0001):.6f}",
        "elevation": f"{287.4 + random.uniform(-0.5, 0.5):.2f}",
        "satellites": str(random.randint(5, 9)),
        "ang_vel_x": f"{random.uniform(0.0, 0.5):.2f}",
        "ang_vel_y": f"{random.uniform(0.0, 0.5):.2f}",
        "ang_vel_z": f"{random.uniform(0.0, 0.5):.2f}",
        "accel_x": f"{9.81 + random.uniform(-0.1, 0.1):.2f}",
        "accel_y": f"{random.uniform(-0.1, 0.1):.2f}",
        "accel_z": f"{random.uniform(-0.1, 0.1):.2f}",
        "mag_x": f"{12.3 + random.uniform(-1.0, 1.0):.2f}",
        "mag_y": f"{-4.5 + random.uniform(-1.0, 1.0):.2f}",
        "mag_z": f"{30.1 + random.uniform(-1.0, 1.0):.2f}",
    }

class SensorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Localization Device Display")
        self.root.geometry("950x650")
        self.root.configure(bg=BG_COLOR)

        self.running = False
        self.display_frame = None
        self.labels = {}

        self.serial_port = "COM5"
        self.baud_rate = 9600
        self.ser = None
        
        # Turn this off when only USB.
        self.use_mock_if_serial_fails = False

        self.make_main_menu()

    def make_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(expand=True)

        card = tk.Frame(main, bg=CARD_COLOR, bd=1, relief="solid", padx=40, pady=40)
        card.pack()

        title = tk.Label(
            card,
            text="Localization Device GUI",
            font=("Arial", 24, "bold"),
            bg=CARD_COLOR,
            fg=TITLE_COLOR
        )
        title.pack(pady=(0, 25))

        start_btn = tk.Button(card, text="Start Display", width=20, font=("Arial", 12), command=self.start_display)
        start_btn.pack(pady=10)

        quit_btn = tk.Button(card, text="Quit", width=20, font=("Arial", 12), command=self.close_app)
        quit_btn.pack(pady=10)

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            return True
        except Exception:
            self.ser = None
            return False

    def parse_csv_line(self, line):
        parts = line.split(",")
        if len(parts) != 14:
            return None

        return {
            "latitude": parts[1],
            "longitude": parts[2],
            "elevation": parts[3],
            "satellites": parts[4],
            "ang_vel_x": parts[5],
            "ang_vel_y": parts[6],
            "ang_vel_z": parts[7],
            "accel_x": parts[8],
            "accel_y": parts[9],
            "accel_z": parts[10],
            "mag_x": parts[11],
            "mag_y": parts[12],
            "mag_z": parts[13],
        }

    def read_usb_data(self):
        if self.ser is None:
            return None

        try:
            line = self.ser.readline().decode("utf-8").strip()
            if not line:
                return None
            return self.parse_csv_line(line)
        except Exception:
            return None

    def start_display(self):
        serial_connected = self.connect_serial()

        if not serial_connected and not self.use_mock_if_serial_fails:
            messagebox.showerror("Connection Error", "No USB stream available.")
            self.make_main_menu()
            return

        self.running = True
        self.make_display_screen()
        self.update_display()

    def add_field(self, parent, row, field, col_label=0, col_value=1):
        pretty = field.replace("_", " ").title() + ":"

        tk.Label(
            parent,
            text=pretty,
            font=("Arial", 13),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).grid(row=row, column=col_label, sticky="e", padx=(10, 15), pady=10)

        self.labels[field] = tk.Label(
            parent,
            text="---",
            font=("Consolas", 13, "bold"),
            bg=CARD_COLOR,
            fg=VALUE_COLOR,
            width=12,
            anchor="w"
        )
        self.labels[field].grid(row=row, column=col_value, sticky="w", padx=(0, 10), pady=10)

    def make_display_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg=BG_COLOR)

        outer = tk.Frame(self.root, bg=BG_COLOR)
        outer.pack(expand=True, fill="both")

        center = tk.Frame(outer, bg=BG_COLOR)
        center.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            center,
            text="Real-Time Sensor Data",
            font=("Arial", 28, "bold"),
            bg=BG_COLOR,
            fg=TITLE_COLOR
        )
        title.pack(pady=(0, 25))

        cards_row = tk.Frame(center, bg=BG_COLOR)
        cards_row.pack()

        gps_card = tk.Frame(cards_row, bg=CARD_COLOR, bd=1, relief="solid", padx=25, pady=20)
        gps_card.grid(row=0, column=0, padx=20, sticky="n")

        imu_card = tk.Frame(cards_row, bg=CARD_COLOR, bd=1, relief="solid", padx=25, pady=20)
        imu_card.grid(row=0, column=1, padx=20, sticky="n")

        gps_title = tk.Label(
            gps_card,
            text="GPS Data",
            font=("Arial", 18, "bold"),
            bg=CARD_COLOR,
            fg=SECTION_COLOR
        )
        gps_title.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        imu_title = tk.Label(
            imu_card,
            text="IMU Data",
            font=("Arial", 18, "bold"),
            bg=CARD_COLOR,
            fg=SECTION_COLOR
        )
        imu_title.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        self.labels = {}

        gps_fields = ["latitude", "longitude", "elevation", "satellites"]
        imu_fields = [
            "ang_vel_x", "ang_vel_y", "ang_vel_z",
            "accel_x", "accel_y", "accel_z",
            "mag_x", "mag_y", "mag_z"
        ]

        for i, field in enumerate(gps_fields, start=1):
            self.add_field(gps_card, i, field)

        for i, field in enumerate(imu_fields, start=1):
            self.add_field(imu_card, i, field)

        button_row = tk.Frame(center, bg=BG_COLOR)
        button_row.pack(pady=30)

        end_btn = tk.Button(
            button_row,
            text="End Display",
            width=18,
            font=("Arial", 12, "bold"),
            command=self.end_display
        )
        end_btn.pack()

    def update_display(self):
        if not self.running:
            return

        data = self.read_usb_data()

        if data is None and self.use_mock_if_serial_fails:
            data = get_mock_data()

        if data is not None:
            for key, value in data.items():
                if key in self.labels:
                    self.labels[key].config(text=value)

        self.root.after(250, self.update_display)

    def end_display(self):
        self.running = False
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None
        self.make_main_menu()

    def close_app(self):
        self.running = False
        if self.ser is not None:
            try:
                self.ser.close()
            except Exception:
                pass
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()