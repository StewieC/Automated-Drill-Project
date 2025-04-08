import tkinter as tk
from tkinter import ttk
import serial
import customtkinter as ctk
import threading
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables
is_monitoring = False
ser = None
stepper_speeds = np.array([])  # For stepper speed graph
dc_status = np.array([])       # For DC motor status graph (0 = off, 1 = on)
data_lock = threading.Lock()

# Functions
def update_serial_connection():
    selected_com_port = com_port_combo.get()
    selected_baud_rate = baud_rate_combo.get()
    global ser
    try:
        if ser is not None and ser.is_open:
            ser.close()
        ser = serial.Serial(selected_com_port, int(selected_baud_rate), timeout=1)
        ser.reset_input_buffer()
        start_button.configure(state="normal")  # Enable Start button after connection
        print(f"Connection on {selected_com_port} at {selected_baud_rate} successful")
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        start_button.configure(state="disabled")  # Disable if connection fails
    except Exception as e:
        print(f"Unexpected Error: {e}")
        start_button.configure(state="disabled")

def send_command(command):
    global ser
    if ser is not None and ser.is_open:
        ser.write((command + "\n").encode('utf-8'))  # Add newline as expected by Arduino
        print(f"Sent: {command}")
    else:
        print("Serial port not initialized.")

def start_monitoring():
    global is_monitoring
    is_monitoring = True
    thread = threading.Thread(target=monitor_status)
    thread.daemon = True
    thread.start()

def stop_monitoring():
    global is_monitoring
    is_monitoring = False

def monitor_status():
    global is_monitoring, stepper_speeds, dc_status
    while is_monitoring:
        try:
            if ser is None or not ser.is_open:
                continue
            data = ser.readline().decode('utf-8').strip()
            print(f"Raw: {data}")  # Debug raw output
            if "speed set to:" in data:
                speed = int(data.split(":")[1].strip())
                with data_lock:
                    if len(stepper_speeds) < 50:
                        stepper_speeds = np.append(stepper_speeds, speed)
                    else:
                        stepper_speeds[0:49] = stepper_speeds[1:50]
                        stepper_speeds[49] = speed
                stepper_speed_label.configure(text=f"Stepper Speed: {speed} steps/sec")
            elif "Drilling started" in data:
                with data_lock:
                    if len(dc_status) < 50:
                        dc_status = np.append(dc_status, 1)  # DC on
                    else:
                        dc_status[0:49] = dc_status[1:50]
                        dc_status[49] = 1
                dc_speed_label.configure(text="DC Motor: ON")
            elif "Drilling stopped" in data or "Retraction complete" in data:
                with data_lock:
                    if len(dc_status) < 50:
                        dc_status = np.append(dc_status, 0)  # DC off
                    else:
                        dc_status[0:49] = dc_status[1:50]
                        dc_status[49] = 0
                dc_speed_label.configure(text="DC Motor: OFF")
            root.after(1, update_graphs)
        except Exception as e:
            print(f"Error: {e}")

def update_graphs():
    with data_lock:
        stepper_line.set_xdata(np.arange(0, len(stepper_speeds)))
        stepper_line.set_ydata(stepper_speeds)
        dc_line.set_xdata(np.arange(0, len(dc_status)))
        dc_line.set_ydata(dc_status)
    stepper_canvas.draw()
    dc_canvas.draw()

# GUI Setup
root = ctk.CTk()
root.title("Drilling System Control GUI")
root.configure(background='lightblue')

# Frames
left_frame = ctk.CTkFrame(root)
right_frame = ctk.CTkFrame(root)

# Left Frame Widgets
com_port_label = ctk.CTkLabel(left_frame, text="Select COM Port:")
com_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
com_port_combo = ttk.Combobox(left_frame, values=com_ports)
com_port_combo.set("COM7")  # Your port

baud_rate_label = ctk.CTkLabel(left_frame, text="Select Baud Rate:")
baud_rates = ["9600", "115200"]
baud_rate_combo = ttk.Combobox(left_frame, values=baud_rates)
baud_rate_combo.set("9600")

update_button = ctk.CTkButton(left_frame, text="Update Serial", command=update_serial_connection)
start_button = ctk.CTkButton(left_frame, text="Start", command=lambda: send_command("START"), state="disabled")
stop_button = ctk.CTkButton(left_frame, text="Stop", command=lambda: send_command("STOP"))
fast_feed_button = ctk.CTkButton(left_frame, text="Fast Feed (1000 steps/sec)", command=lambda: send_command("SPEED:1000"))
slow_feed_button = ctk.CTkButton(left_frame, text="Slow Feed (500 steps/sec)", command=lambda: send_command("SPEED:500"))

stepper_speed_label = ctk.CTkLabel(left_frame, text="Stepper Speed: 500 steps/sec")  # Default from Arduino
dc_speed_label = ctk.CTkLabel(left_frame, text="DC Motor: OFF")

# Right Frame Graphs
# Stepper Speed Graph
stepper_fig = Figure(figsize=(5, 2.5))
stepper_ax = stepper_fig.add_subplot(111)
stepper_ax.set_title("Stepper Speed")
stepper_ax.set_ylabel("Steps/sec")
stepper_ax.set_xlim([0, 50])
stepper_ax.set_ylim([0, 1100])
stepper_ax.grid(True)
stepper_line = stepper_ax.plot([], [])[0]
stepper_canvas = FigureCanvasTkAgg(stepper_fig, master=right_frame)
stepper_canvas.draw()

# DC Motor Status Graph
dc_fig = Figure(figsize=(5, 2.5))
dc_ax = dc_fig.add_subplot(111)
dc_ax.set_title("DC Motor Status")
dc_ax.set_ylabel("On/Off (1/0)")
dc_ax.set_xlim([0, 50])
dc_ax.set_ylim([-0.5, 1.5])
dc_ax.grid(True)
dc_ax.set_yticks([0, 1])
dc_line = dc_ax.plot([], [])[0]
dc_canvas = FigureCanvasTkAgg(dc_fig, master=right_frame)
dc_canvas.draw()

# Layout
com_port_label.pack(pady=5)
com_port_combo.pack(pady=5)
baud_rate_label.pack(pady=5)
baud_rate_combo.pack(pady=5)
update_button.pack(pady=5)
start_button.pack(pady=5)
stop_button.pack(pady=5)
fast_feed_button.pack(pady=5)
slow_feed_button.pack(pady=5)
stepper_speed_label.pack(pady=5)
dc_speed_label.pack(pady=5)
left_frame.pack(side="left", padx=10, pady=10, fill="y")

stepper_canvas.get_tk_widget().pack(pady=5)
dc_canvas.get_tk_widget().pack(pady=5)
right_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

start_monitoring()
root.mainloop()