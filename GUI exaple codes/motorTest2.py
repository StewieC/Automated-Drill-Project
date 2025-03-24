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
csv_data = []  # List to hold the PWM data
pulses = np.array([])  # For PWM data from DC motor speed

# Lock for synchronizing access to shared data
data_lock = threading.Lock()

# Theme detection
dark_mode = False
try:
    value = ctypes.windll.uxtheme.IsThemeActive()
    dark_mode = bool(value)
except Exception as e:
    print(f'A Theme Error has occurred: {e}')
    dark_mode = False

def toggle_dark_mode():
    global dark_mode    
    dark_mode = not dark_mode
    update_theme()

def update_theme():
    theme = "dark" if dark_mode else "light"
    root.configure(background='black' if dark_mode else 'light')
    ctk.set_appearance_mode(theme)
    switch_1.configure(text='Light Mode' if dark_mode else 'Dark Mode')
    canvas.get_tk_widget().configure(bg='black' if dark_mode else 'white')

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
    global is_plotting, pulses, csv_data, data_counter
    while is_plotting:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data.startswith("CURRENT SPEED:"):
                pwm = int(data.split(":")[1])
                with data_lock:
                    if len(pulses) < 50:
                        pulses = np.append(pulses, pwm)
                    else:
                        pulses[0:49] = pulses[1:50]
                        pulses[49] = pwm
                pwm_label.configure(text=f'PWM: {pwm}')
                csv_data.append([pwm])
                if len(csv_data) >= max_data_points:
                    save_data_to_csv(data_counter)
                    data_counter += 1
                    csv_data = []
                root.after(1, update_plot_graph)
        except Exception as e:
            print(f"Plot update error: {e}")

def save_data_to_csv(counter):
    filename = f'datapwm{counter}.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['PWM'])
        for data_point in csv_data:
            csvwriter.writerow(data_point)

def update_plot_graph():
    with data_lock:
        line.set_xdata(np.arange(0, len(pulses)))
        line.set_ydata(pulses)
    canvas.draw()

def send_command(command):
    try:
        ser.write(command.encode('utf-8'))
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error sending command: {e}")

def update_serial_connection():
    selected_com_port = com_port_combo.get()
    selected_baud_rate = baud_rate_combo.get()
    global ser
    try:
        ser.close()
    except:
        pass  # Ignore if not open yet
    try:
        ser = serial.Serial(selected_com_port, int(selected_baud_rate))
        ser.reset_input_buffer()
        print(f'Connection on {ser} successful')
        send_command("Python Ready")  # Signal to Arduino
    except serial.SerialException as e:
        print(f'Error: {e}. Connection on {selected_com_port} not found.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

def set_custom_speed():
    try:
        speed = int(speed_entry.get())
        if 0 <= speed <= 255:
            send_command(f"setSpeed{speed}")
        else:
            print("Speed must be between 0 and 255")
    except ValueError:
        print("Please enter a valid integer")

# Initialize tkinter window
root = ctk.CTk()
root.title("MOTOR CONTROL GUI: ONE AXIS AUTOMATED DRILL")
root.configure(background='lightblue')

# Serial communication setup
ser = serial.Serial()

# Create GUI components
combined_halves = ctk.CTkFrame(root)
left_half = ctk.CTkFrame(combined_halves)
right_half = ctk.CTkFrame(combined_halves)

# Groups for left half
group_1 = ctk.CTkFrame(left_half)  # Stop and theme
group_1a = ctk.CTkFrame(group_1)   # Stop button
group_1b = ctk.CTkFrame(group_1)   # Theme switch

group_2 = ctk.CTkFrame(left_half)  # Serial settings
group_2a = ctk.CTkFrame(group_2)   # COM port label
group_2b = ctk.CTkFrame(group_2)   # COM port combo
group_2c = ctk.CTkFrame(group_2)   # Baud rate label
group_2d = ctk.CTkFrame(group_2)   # Baud rate combo
group_2e = ctk.CTkFrame(group_2)   # Update button

group_3 = ctk.CTkFrame(left_half)  # Motor controls
group_3a = ctk.CTkFrame(group_3)   # Fast drill
group_3b = ctk.CTkFrame(group_3)   # Slow drill
group_3c = ctk.CTkFrame(group_3)   # High feed rate
group_3d = ctk.CTkFrame(group_3)   # Low feed rate

group_4 = ctk.CTkFrame(left_half)  # PWM label and custom speed
group_4a = ctk.CTkFrame(group_4)   # PWM label
group_4b = ctk.CTkFrame(group_4)   # Custom speed entry and button

# Groups for right half
group_r_1 = ctk.CTkFrame(right_half)  # Start/Stop plotting
group_r_1a = ctk.CTkFrame(group_r_1)  # Buttons

group_r_2 = ctk.CTkFrame(right_half)  # Plot

# Widgets
start_button = ctk.CTkButton(group_r_1a, text="Start Plot", command=start_plotting)
stop_button = ctk.CTkButton(group_r_1a, text="Stop Plot", command=stop_plotting)
pwm_label = ctk.CTkLabel(group_4a, text="PWM: 0", font=("Helvetica", 15))
stop_machine_button = ctk.CTkButton(group_1a, text="STOP MACHINE", command=lambda: send_command('stopmachine'))
switch_1 = ctk.CTkSwitch(master=group_1b, text='Light Mode' if dark_mode else 'Dark Mode', command=toggle_dark_mode)

fast_drill_button = ctk.CTkButton(group_3a, text="FAST DRILL (255)", command=lambda: send_command('fastdrill'))
slow_drill_button = ctk.CTkButton(group_3b, text="SLOW DRILL (100)", command=lambda: send_command('slowdrill'))
high_feedrate_button = ctk.CTkButton(group_3c, text="HIGH FEED (200)", command=lambda: send_command('highFeedRate'))
low_feedrate_button = ctk.CTkButton(group_3d, text="LOW FEED (olkata50)", command=lambda: send_command('slowFeedRate'))

com_port_label = ctk.CTkLabel(group_2a, text="Select COM Port:")
com_ports = [f"COM{i}" for i in range(1, 21)]
com_port_combo = ttk.Combobox(group_2b, values=com_ports)
com_port_combo.set("COM1")

baud_rate_label = ctk.CTkLabel(group_2c, text="Select Baud Rate:")
baud_rates = ["9600", "115200", "57600", "38400"]
baud_rate_combo = ttk.Combobox(group_2d, values=baud_rates)
baud_rate_combo.set("9600")

update_button = ctk.CTkButton(group_2e, text="Update Serial Connection", command=update_serial_connection)

speed_entry = ctk.CTkEntry(group_4b, placeholder_text="Enter Speed (0-255)")
speed_set_button = ctk.CTkButton(group_4b, text="Set Speed", command=set_custom_speed)

# Matplotlib setup for PWM plot
fig = Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
ax.set_title("DC Motor PWM")
ax.set_ylabel("PWM Value")
ax.grid(True)
ax.set_xlim([0, 50])
ax.set_ylim([0, 260])
line, = ax.plot([], [])
canvas = FigureCanvasTkAgg(fig, master=group_r_2)
canvas.draw()

# Layout
com_port_label.pack(padx=5, pady=5)
com_port_combo.pack(padx=5, pady=5)
baud_rate_label.pack(padx=5, pady=5)
baud_rate_combo.pack(padx=5, pady=5)
update_button.pack(padx=5, pady=5)

switch_1.pack(padx=10, pady=10)
stop_machine_button.pack(padx=10, pady=10)

start_button.pack(side='left', padx=5, pady=5)
stop_button.pack(side='right', padx=5, pady=5)

fast_drill_button.pack(padx=10, pady=10)
slow_drill_button.pack(padx=10, pady=10)
high_feedrate_button.pack(padx=10, pady=10)
low_feedrate_button.pack(padx=10, pady=10)

pwm_label.pack(padx=5, pady=5)
speed_entry.pack(side='left', padx=5, pady=5)
speed_set_button.pack(side='left', padx=5, pady=5)

canvas.get_tk_widget().pack(padx=10, pady=10)

group_1a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_1b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_1.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

group_2a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2c.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2d.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2e.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_2.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

group_3a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_3b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_3c.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_3d.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_3.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

group_4a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_4b.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_4.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

group_r_1a.pack(padx=5, pady=5, fill=ctk.BOTH, expand=True)
group_r_1.pack(padx=5, pady=10, fill=ctk.X, expand=True)

group_r_2.pack(padx=5, pady=10, fill=ctk.BOTH, expand=True)

left_half.pack(side='left', padx=5, pady=5, fill=ctk.BOTH, expand=True)
right_half.pack(side='left', padx=5, pady=5, fill=ctk.BOTH, expand=True)
combined_halves.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

# Start the GUI
root.mainloop()