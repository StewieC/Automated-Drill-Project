import tkinter as tk
from tkinter import ttk
import serial
import customtkinter as ctk
import threading

# Variables
is_monitoring = False
ser = None

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
    global is_monitoring
    while is_monitoring:
        try:
            if ser is None or not ser.is_open:
                continue
            data = ser.readline().decode('utf-8').strip()
            if data.startswith("DC_SPEED:"):
                parts = data.split(",")
                dc_speed = int(parts[0].split(":")[1])
                step_running = int(parts[1].split(":")[1])
                dc_speed_label.configure(text=f"DC Speed: {dc_speed}")
                status_label.configure(text="Status: Running" if step_running else "Status: Stopped")
        except Exception as e:
            print(f"Error: {e}")

# GUI Setup
root = ctk.CTk()
root.title("Dual Motor Control GUI")
root.configure(background='lightblue')

frame = ctk.CTkFrame(root)

com_port_label = ctk.CTkLabel(frame, text="Select COM Port:")
com_ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
com_port_combo = ttk.Combobox(frame, values=com_ports)
com_port_combo.set("COM6")  # Your port

baud_rate_label = ctk.CTkLabel(frame, text="Select Baud Rate:")
baud_rates = ["9600", "115200"]
baud_rate_combo = ttk.Combobox(frame, values=baud_rates)
baud_rate_combo.set("9600")

update_button = ctk.CTkButton(frame, text="Update Serial", command=update_serial_connection)
start_button = ctk.CTkButton(frame, text="Start", command=lambda: send_command("start"))
stop_button = ctk.CTkButton(frame, text="Stop", command=lambda: send_command("stop"))

dc_speed_entry = ctk.CTkEntry(frame, placeholder_text="DC Speed (0-255)")
dc_speed_button = ctk.CTkButton(frame, text="Set DC Speed", command=lambda: send_command(f"dc_speed {dc_speed_entry.get()}"))
step_speed_entry = ctk.CTkEntry(frame, placeholder_text="Step Speed (500-5000 us)")
step_speed_button = ctk.CTkButton(frame, text="Set Step Speed", command=lambda: send_command(f"step_speed {step_speed_entry.get()}"))

dc_speed_label = ctk.CTkLabel(frame, text="DC Speed: 0")
status_label = ctk.CTkLabel(frame, text="Status: Stopped")

com_port_label.pack(pady=5)
com_port_combo.pack(pady=5)
baud_rate_label.pack(pady=5)
baud_rate_combo.pack(pady=5)
update_button.pack(pady=5)
start_button.pack(pady=5)
stop_button.pack(pady=5)
dc_speed_entry.pack(pady=5)
dc_speed_button.pack(pady=5)
step_speed_entry.pack(pady=5)
step_speed_button.pack(pady=5)
dc_speed_label.pack(pady=5)
status_label.pack(pady=5)
frame.pack(padx=10, pady=10)

start_monitoring()
root.mainloop()