import tkinter as tk
from tkinter import ttk
import serial
import customtkinter as ctk
import threading
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables
is_plotting = False
pulses = np.array([])
data_lock = threading.Lock()
ser = None

def update_serial_connection():
    selected_com_port = com_port_combo.get()
    selected_baud_rate = baud_rate_combo.get()
    global ser
    try:
        if ser is not None and ser.is_open:
            ser.close()
        ser = serial.Serial(selected_com_port, int(selected_baud_rate), timeout=1)
        ser.reset_input_buffer()
        print(f"Connection on {selected_com_port} at {selected_baud_rate} successful")
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def send_command(command):
    global ser
    if ser is not None and ser.is_open:
        ser.write(command.encode('utf-8'))
        print(f"Sent: {command}")
    else:
        print("Serial port not initialized.")

def start_plotting():
    global is_plotting
    is_plotting = True
    thread = threading.Thread(target=update_plot)
    thread.daemon = True
    thread.start()

def stop_plotting():
    global is_plotting
    is_plotting = False

def update_plot():
    global is_plotting, pulses
    while is_plotting:
        try:
            if ser is None or not ser.is_open:
                continue
            data = ser.readline().decode('utf-8').strip()
            if data.startswith("CURRENT SPEED:"):
                pwm = int(data.split(":")[1])
                with data_lock:
                    if len(pulses) < 50:
                        pulses = np.append(pulses, pwm)
                    else:
                        pulses[0:49] = pulses[1:50]
                        pulses[49] = pwm
                pwm_label.configure(text=f"PWM: {pwm}")
                root.after(1, update_plot_graph)
        except Exception as e:
            print(f"Error: {e}")

def update_plot_graph():
    with data_lock:
        lines.set_xdata(np.arange(0, len(pulses)))
        lines.set_ydata(pulses)
    canvas.draw()

# GUI Setup
root = ctk.CTk()
root.title("DC Motor Control GUI")
root.configure(background='lightblue')

left_frame = ctk.CTkFrame(root)
right_frame = ctk.CTkFrame(root)

com_port_label = ctk.CTkLabel(left_frame, text="Select COM Port:")
com_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
com_port_combo = ttk.Combobox(left_frame, values=com_ports)
com_port_combo.set("COM6")

baud_rate_label = ctk.CTkLabel(left_frame, text="Select Baud Rate:")
baud_rates = ["9600", "115200"]
baud_rate_combo = ttk.Combobox(left_frame, values=baud_rates)
baud_rate_combo.set("9600")

update_button = ctk.CTkButton(left_frame, text="Update Serial", command=update_serial_connection)
start_button = ctk.CTkButton(left_frame, text="Start", command=lambda: send_command("start"))
stop_button = ctk.CTkButton(left_frame, text="Stop", command=lambda: send_command("stop"))
speed_entry = ctk.CTkEntry(left_frame, placeholder_text="Enter speed (0-255)")
speed_button = ctk.CTkButton(left_frame, text="Set Speed", command=lambda: send_command(f"speed {speed_entry.get()}"))
pwm_label = ctk.CTkLabel(left_frame, text="PWM: 0")

fig = Figure(figsize=(5, 3))
ax = fig.add_subplot(111)
ax.set_title("DC Motor Speed")
ax.set_ylabel("PWM")
ax.set_xlim([0, 50])
ax.set_ylim([0, 260])
ax.grid(True)
lines = ax.plot([], [])[0]
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.draw()

com_port_label.pack(pady=5)
com_port_combo.pack(pady=5)
baud_rate_label.pack(pady=5)
baud_rate_combo.pack(pady=5)
update_button.pack(pady=5)
start_button.pack(pady=5)
stop_button.pack(pady=5)
speed_entry.pack(pady=5)
speed_button.pack(pady=5)
pwm_label.pack(pady=5)
left_frame.pack(side="left", padx=10, pady=10, fill="y")
canvas.get_tk_widget().pack(pady=10)
right_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

start_plotting()
root.mainloop()