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
import customtkinter as ctk
import ctypes

#variables
is_plotting = False
max_data_points = 50
data_counter = 0  # Counter for unique data files
csv_data = []  # List to hold the data
pulses = np.array([])

# Lock for synchronizing access to shared data
data_lock = threading.Lock()

# Connect to Arduino (Update this with correct COM port)
def connect_arduino():
    selected_com_port = com_port_combo.get()
    selected_baud_rate = baud_rate_combo.get()

    global ser
    try:
        ser.close()
        ser = serial.Serial(selected_com_port, int(selected_baud_rate))
        ser.reset_input_buffer() #Allow time for Arduino to reset
        status_label.config(text=f"Connected to {selected_com_port}", fg="green")
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
def toggle_dark_mode():
    global dark_mode    
    dark_mode=not dark_mode
    update_Theme()


def update_Theme():
    theme = "dark" if dark_mode else "light"
    root.configure(background='black' if dark_mode else 'light')
    ctk.set_appearance_mode(theme)
    print(f"SWitching to {theme} Mode")
    switch_1.configure(text='Light Mode' if dark_mode else 'Dark Mode')

    # update the canvas themes
    canvas3.get_tk_widget().configure(bg = 'black' if dark_mode else 'white')

# start and stop plotting function
def start_plotting():
    global is_plotting
    is_plotting = True
    thread = threading.Thread(target=update_plot)
    thread.daemon = True
    thread.start()
    ser.reset_input_buffer()

# Function to stop reading data from Arduino
def stop_plotting():
    global is_plotting
    is_plotting = False

# # Graph PWM Data (Simulated as random values)
# def update_graph():
#     global pwm_values, time_values
#     pwm_values.append(dc_speed_var.get())
#     time_values.append(len(time_values))
#     ax.clear()
#     ax.plot(time_values, pwm_values, marker='o', linestyle='-')
#     ax.set_title("PWM Speed Over Time")
#     canvas.draw()
#     root.after(1000, update_graph)

# Function to update the first plot
def update_plot():
    global is_plotting,pulses,csv_data, data_counter
    while is_plotting:
        try:
            data = ser.readline().decode('utf-8').strip()
            comb_data= data.split(',')
            #if(len(comb_data)==3):
            
            pwm = comb_data[0]
            
            with data_lock:
                if len(pulses) < 50:
                    pulses = np.append(pulses, int(pwm[0:4]))                              
                else:
                    pulses[0:49] = pulses[1:50]
                    pulses[49] = float(pwm[0:4])

            # pwm_label.ure(text=f'PWM: {pwm}')
            pwm_label.configure(text=f'PWM: {pwm}')

                        # Append data to csv_data
            csv_data.append([pwm])

            # Check if data exceeds 200 points and save to a new CSV file
            if len(csv_data) >= max_data_points:
                save_data_to_csv(data_counter)
                data_counter += 1
                csv_data = []
            root.after(1, update_plot3)
        except Exception as e:
          print(e)

# Function to save data to a CSV file with a unique identifier
def save_data_to_csv(counter):
    filename = f'datapwm{counter}.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['PWM'])
        for data_point in csv_data:
            csvwriter.writerow(data_point)

# Start a separate thread to continuously update data and plots
data_thread = threading.Thread(target=update_plot)
data_thread.daemon = True
data_thread.start()

# Function to update the third plot
def update_plot3():
    with data_lock:
        lines3.set_xdata(np.arange(0, len(pulses)))
        lines3.set_ydata(pulses)
    canvas3.draw()

# GUI Setup
root = tk.Tk()
root.title(" Motor Control GUI")
root.configure(background='light')
# dark_mode = False

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
