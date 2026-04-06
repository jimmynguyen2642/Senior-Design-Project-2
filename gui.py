import tkinter as tk
from tkinter import messagebox
import random

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
        self.root.geometry("700x500")

        self.running = False
        self.display_frame = None

        self.make_main_menu()

    def make_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)

        title = tk.Label(frame, text="Localization Device GUI", font=("Arial", 20, "bold"))
        title.pack(pady=20)

        start_btn = tk.Button(frame, text="Start Display", width=20, command=self.start_display)
        start_btn.pack(pady=10)

        quit_btn = tk.Button(frame, text="Quit", width=20, command=self.root.quit)
        quit_btn.pack(pady=10)

    def start_display(self):
        try:
            self.running = True
            self.make_display_screen()
            self.update_display()
        except Exception as e:
            messagebox.showerror("Connection Error", f"No USB stream available.\n{e}")
            self.make_main_menu()

    def make_display_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.display_frame = tk.Frame(self.root, padx=20, pady=20)
        self.display_frame.pack(fill="both", expand=True)

        title = tk.Label(self.display_frame, text="Real-Time Sensor Data", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=10)

        gps_title = tk.Label(self.display_frame, text="GPS Data", font=("Arial", 14, "bold"))
        gps_title.grid(row=1, column=0, columnspan=2, pady=10)

        imu_title = tk.Label(self.display_frame, text="IMU Data", font=("Arial", 14, "bold"))
        imu_title.grid(row=1, column=2, columnspan=2, pady=10)

        self.labels = {}

        gps_fields = ["latitude", "longitude", "elevation", "satellites"]
        imu_fields = [
            "ang_vel_x", "ang_vel_y", "ang_vel_z",
            "accel_x", "accel_y", "accel_z",
            "mag_x", "mag_y", "mag_z"
        ]

        for i, field in enumerate(gps_fields, start=2):
            tk.Label(self.display_frame, text=field.replace("_", " ").title() + ":").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            self.labels[field] = tk.Label(self.display_frame, text="---", width=15, anchor="w")
            self.labels[field].grid(row=i, column=1, sticky="w", padx=5, pady=5)

        for i, field in enumerate(imu_fields, start=2):
            tk.Label(self.display_frame, text=field.replace("_", " ").title() + ":").grid(row=i, column=2, sticky="e", padx=5, pady=5)
            self.labels[field] = tk.Label(self.display_frame, text="---", width=15, anchor="w")
            self.labels[field].grid(row=i, column=3, sticky="w", padx=5, pady=5)

        end_btn = tk.Button(self.display_frame, text="End Display", width=20, command=self.end_display)
        end_btn.grid(row=12, column=0, columnspan=4, pady=20)

    def update_display(self):
        if not self.running:
            return

        data = get_mock_data()

        for key, value in data.items():
            if key in self.labels:
                self.labels[key].config(text=value)

        self.root.after(1000, self.update_display)

    def end_display(self):
        self.running = False
        self.make_main_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.mainloop()