import serial
import tkinter as tk
from tkinter import messagebox
import threading

# Set up serial communication with Arduino (adjust COM port)
arduino = serial.Serial('COM3', 9600, timeout=1)

# Function to send command to Arduino
def send_command(command):
    arduino.write((command + '\n').encode())

# Function to set motor speed
def set_speed():
    speed = speed_entry.get()
    if speed.isdigit() and 0 <= int(speed) <= 255:
        send_command(f"setSpeed{speed}")
        feedback_label.config(text=f"Speed set to {speed}")
    else:
        messagebox.showerror("Invalid Input", "Enter a value between 0 and 255")

# Function to start machine
def start_machine():
    send_command("startmachine")
    feedback_label.config(text="Machine Started")

# Function to stop machine
def stop_machine():
    send_command("stopmachine")
    feedback_label.config(text="Machine Stopped")

# Function to continuously read data from Arduino
def read_arduino_data():
    while True:
        try:
            data = arduino.readline().decode().strip()
            if data:
                feedback_label.config(text=f"Arduino: {data}")
        except:
            break

# Create GUI
root = tk.Tk()
root.title("Automated Drill Control")

# Speed Input
tk.Label(root, text="Set Speed (0-255):").pack()
speed_entry = tk.Entry(root)
speed_entry.pack()
tk.Button(root, text="Set Speed", command=set_speed).pack()

# Control Buttons
tk.Button(root, text="Start Machine", command=start_machine, bg="green").pack()
tk.Button(root, text="Stop Machine", command=stop_machine, bg="red").pack()

# Feedback Display
feedback_label = tk.Label(root, text="Waiting for Arduino...")
feedback_label.pack()

# Start background thread to read Arduino data
threading.Thread(target=read_arduino_data, daemon=True).start()

# Run GUI loop
root.mainloop()
