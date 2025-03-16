import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#variables
is_plotting = False
max_data_points = 50
data_counter = 0  # Counter for unique data files
csv_data = []  # List to hold the data
pulses = np.array([])



# Connect to Arduino (Update this with correct COM port)
def connect_arduino():
    global ser
    port = port_var.get()
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Allow time for Arduino to reset
        status_label.config(text=f"Connected to {port}", fg="green")
    except Exception as e:
        status_label.config(text=f"Failed to connect: {e}", fg="red")

# Send command to Arduino
def send_command(command):
    if ser and ser.is_open:
        ser.write((command + "\n").encode())

# Set DC Motor Speed
def set_dc_speed():
    speed = dc_speed_var.get()
    send_command(f"setSpeed{speed}")

# Set Stepper Motor Feed Rate
def set_stepper_feed(feed):
    if feed == "Fast":
        send_command("highFeedRate")
    else:
        send_command("slowFeedRate")

# Emergency Stop
def stop_machine():
    send_command("stopmachine")

# Toggle Theme
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    theme_color = "#333" if dark_mode else "#fff"
    fg_color = "#fff" if dark_mode else "#000"
    root.configure(bg=theme_color)
    for widget in root.winfo_children():
        widget.configure(bg=theme_color, fg=fg_color)

# start and stop plotting function
def start_plotting():
    global is_plotting
    is_plotting = True
    thread = threading.Thread(target=update_graph)
    thread.daemon = True
    thread.start()
    ser.reset_input_buffer()

# Function to stop reading data from Arduino
def stop_plotting():
    global is_plotting
    is_plotting = False

# Graph PWM Data (Simulated as random values)
def update_graph():
    global pwm_values, time_values
    pwm_values.append(dc_speed_var.get())
    time_values.append(len(time_values))
    ax.clear()
    ax.plot(time_values, pwm_values, marker='o', linestyle='-')
    ax.set_title("PWM Speed Over Time")
    canvas.draw()
    root.after(1000, update_graph)


# Function to save data to a CSV file with a unique identifier
def save_data_to_csv(counter):
    filename = f'datapwm{counter}.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['PWM'])
        for data_point in csv_data:
            csvwriter.writerow(data_point)



# GUI Setup
root = tk.Tk()
root.title("Arduino Motor Control")
root.geometry("500x500")
dark_mode = False

# Serial Port Selection
port_var = tk.StringVar()
ports = [port.device for port in serial.tools.list_ports.comports()]
port_menu = ttk.Combobox(root, textvariable=port_var, values=ports)
port_menu.pack(pady=5)
ttk.Button(root, text="Connect", command=connect_arduino).pack(pady=5)
status_label = tk.Label(root, text="Not Connected", fg="red")
status_label.pack()

# DC Motor Speed Control
tk.Label(root, text="DC Motor Speed:").pack()
dc_speed_var = tk.IntVar(value=100)
dc_speed_menu = ttk.Combobox(root, textvariable=dc_speed_var, values=[0, 50, 100, 150, 200, 255])
dc_speed_menu.pack()
ttk.Button(root, text="Set Speed", command=set_dc_speed).pack(pady=5)

# Stepper Motor Feed Rate
tk.Label(root, text="Stepper Feed Rate:").pack()
ttk.Button(root, text="Slow", command=lambda: set_stepper_feed("Slow")).pack()
ttk.Button(root, text="Fast", command=lambda: set_stepper_feed("Fast")).pack()

# Stop Button
ttk.Button(root, text="Emergency Stop", command=stop_machine, style="Red.TButton").pack(pady=10)

# Theme Toggle
ttk.Button(root, text="Toggle Dark/Light", command=toggle_theme).pack()

# Graph Setup
fig, ax = plt.subplots()
pwm_values, time_values = [], []
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()
update_graph()

# Start GUI Loop
root.mainloop()
