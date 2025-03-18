import tkinter as tk
from tkinter import ttk
import serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import numpy as np
from matplotlib.figure import Figure
import csv
import customtkinter as ctk
import ctypes

# Variables
is_plotting = False
max_data_points = 50
data_counter = 0  # Counter for unique data files
csv_data = []  # List to hold the data
vibration = np.array([])

# Lock for synchronizing access to shared data
data_lock = threading.Lock()

dark_mode = False
try:
    value = ctypes.windll.uxtheme.IsThemeActive()
    if value == 1:
        dark_mode = True
    else:
        dark_mode = False
except Exception as e:
    print(f'A Theme Error has occurred: {e}')
    dark_mode = False

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    update_Theme()

def update_Theme():
    theme = "dark" if dark_mode else "light"
    root.configure(background='black' if dark_mode else 'light')
    ctk.set_appearance_mode(theme)
    switch_1.configure(text='Light Mode' if dark_mode else 'Dark Mode')

def start_plotting():
    global is_plotting
    is_plotting = True
    thread = threading.Thread(target=update_plot)
    thread.daemon = True
    thread.start()
    ser.reset_input_buffer()

def stop_plotting():
    global is_plotting
    is_plotting = False

def update_plot():
    global is_plotting, vibration, csv_data, data_counter
    while is_plotting:
        try:
            data = ser.readline().decode('utf-8').strip()
            comb_data = data.split(',')
            vib = comb_data[1]  # Assuming vibration is the second value in the data string
            with data_lock:
                if len(vibration) < 50:
                    vibration = np.append(vibration, float(vib[0:4]))
                else:
                    vibration[0:49] = vibration[1:50]
                    vibration[49] = float(vib[0:4])
            
            vib_label.configure(text=f'Vibration: {vib}')
            csv_data.append([vib])

            if len(csv_data) >= max_data_points:
                save_data_to_csv(data_counter)
                data_counter += 1
                csv_data = []
            root.after(1, update_plot1)
        except Exception as e:
            print(e)

def save_data_to_csv(counter):
    filename = f'vibration_data{counter}.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Vibration'])
        for data_point in csv_data:
            csvwriter.writerow(data_point)

def update_plot1():
    with data_lock:
        lines1.set_xdata(np.arange(0, len(vibration)))
        lines1.set_ydata(vibration)
    canvas1.draw()

def update_serial_connection():
    selected_com_port = com_port_combo.get()
    selected_baud_rate = baud_rate_combo.get()
    global ser
    try:
        ser.close()
        ser = serial.Serial(selected_com_port, int(selected_baud_rate))
        ser.reset_input_buffer()
        print(f'Connection on {ser} successful')
    except serial.SerialException as e:
        print(f'Error: {e}. Connection on {selected_com_port} not found.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

# Initialize tkinter window
root = ctk.CTk()
root.title("VIBRATION SENSOR GUI")
root.configure(background='lightblue')

# Serial communication setup
ser = serial.Serial()

# Create GUI components
combined_halves = ctk.CTkFrame(root)
left_half = ctk.CTkFrame(combined_halves)
right_half = ctk.CTkFrame(combined_halves)

group_1 = ctk.CTkFrame(left_half)
group_1b = ctk.CTkFrame(group_1)

group_2 = ctk.CTkFrame(left_half)
group_2a = ctk.CTkFrame(group_2)
group_2b = ctk.CTkFrame(group_2)
group_2c = ctk.CTkFrame(group_2)
group_2d = ctk.CTkFrame(group_2)
group_2e = ctk.CTkFrame(group_2)

group_4 = ctk.CTkFrame(left_half)
group_4b = ctk.CTkFrame(group_4)

group_r_1 = ctk.CTkFrame(right_half)
group_r_1a = ctk.CTkFrame(group_r_1)

group_r_2 = ctk.CTkFrame(right_half)
group_r_2a = ctk.CTkFrame(group_r_2)

start_button = ctk.CTkButton(group_r_1a, text="Start Plot", command=start_plotting)
stop_button = ctk.CTkButton(group_r_1a, text="Stop Plot", command=stop_plotting)
vib_label = ctk.CTkLabel(group_4b, text="Vibration: ", font=("Helvetica", 15))
switch_1 = ctk.CTkSwitch(master=group_1b, text='Light Mode' if dark_mode else 'Dark Mode', command=toggle_dark_mode)

# Dropdown menu for COM port selection
com_port_label = ctk.CTkLabel(group_2a, text="Select COM Port:")
com_port_combo = ttk.Combobox(group_2b, values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6",
                                               "COM7", "COM8", "COM9", "COM10", "COM11", "COM12",
                                               "COM13", "COM14", "COM15", "COM16", "COM17", "COM18",
                                               "COM19", "COM20"])
com_port_combo.set("COM1")

# Dropdown menu for baud rate selection
baud_rate_label = ctk.CTkLabel(group_2c, text="Select Baud Rate:")
baud_rate_combo = ttk.Combobox(group_2d, values=["9600", "115200", "57600", "38400"])
baud_rate_combo.set("9600")

update_button = ctk.CTkButton(group_2e, text="Update Serial Connection", command=update_serial_connection)

# Matplotlib setup for vibration plot
fig1 = Figure(figsize=(5, 3))
ax1 = fig1.add_subplot(111)
ax1.set_title("Vibration")
ax1.set_ylabel("Vibration")
ax1.grid(True)
ax1.set_xlim([0, 50])
ax1.set_ylim([-30, 30])
lines1 = ax1.plot([], [])[0]
canvas1 = FigureCanvasTkAgg(fig1, master=group_r_2a)
canvas1.draw()

# Grid layout
com_port_label.pack(padx=5, pady=5)
com_port_combo.pack(padx=5, pady=5)
baud_rate_label.pack(padx=5, pady=5)
switch_1.pack(padx=10, pady=10)
start_button.pack(side='left', padx=5, pady=5)
stop_button.pack(side='right', padx=5, pady=5)
vib_label.pack(padx=5, pady=5)
baud_rate_combo.pack(padx=5, pady=5)
update_button.pack(padx=5, pady=5)
canvas1.get_tk_widget().pack(side='left', padx=10, pady=10)

group_1b.pack(padx=5, pady=5, fill=ctk.X, expand=True)
group_1.pack(padx=5, pady=10, fill=ctk.X, expand=True)

group_2a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2c.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2d.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2e.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

group_4b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_4.pack(padx=5, pady=10, fill=ctk.X, expand=True)

group_r_1a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_r_1.pack(padx=5, pady=10, fill=ctk.X, expand=True)

group_r_2a.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)
group_r_2.pack(padx=5, pady=10, fill=ctk.X, expand=True)

left_half.pack(side='left', padx=5, pady=5, fill=ctk.BOTH, expand=True)
right_half.pack(side='left', padx=5, pady=5, fill=ctk.BOTH, expand=True)
combined_halves.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

root.mainloop()