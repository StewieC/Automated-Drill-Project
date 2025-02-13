import tkinter as tk
from tkinter import ttk
import serial
# import matplotlib.pyplot as plt
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
force=np.array([])
displacement = np.array([])

# temperature= np.array([])
# vibration = np.array([])

# Lock for synchronizing access to shared data
data_lock = threading.Lock()

# Function to start reading data from Arduino

#checking the theme of the system
dark_mode = False
try:
    value = ctypes.windll.uxtheme.IsThemeActive()
    if value == 1:
        dark_mode = True
    else:
        dark_mode = False
except Exception as e:
    print (f'A Theme Error has occurred: {e}')
    dark_mode =  False

#theme toggle function

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
    # canvas1.get_tk_widget().configure(bg = 'black' if dark_mode else 'white')

#start and stop plotting function
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

# Function to update the first plot
def update_plot():
    global is_plotting, displacement,force,csv_data, data_counter
    while is_plotting:
        try:
            data = ser.readline().decode('utf-8').strip()
            comb_data= data.split(',')
            #if(len(comb_data)==3):
            disp = comb_data[0]
            foc = comb_data[1]
            with data_lock:
                if len(force) < 50:
                    displacement=np.append(displacement,float(disp))
                    force=np.append(force,float(foc[0:4]))
                    
                else:
                    displacement[0:49] = displacement[1:50]
                    displacement[49] = float(disp[0:4])
                    # pulses[0:49] = pulses[1:50]
                    # pulses[49] = int(pwm[0:4])
                    force[0:49] = force[1:50]
                    force[49] = float(foc[0:4])
            
            
            #pwm_label.config(text=f'PWM: {pwm}')
            disp_label.configure(text=f'Displacement: {vib}')
            force_label.configure(text=f'Force: {foc}')
                        # Append data to csv_data
            csv_data.append([disp, foc])

            # Check if data exceeds 200 points and save to a new CSV file
            if len(csv_data) >= max_data_points:
                save_data_to_csv(data_counter)
                data_counter += 1
                csv_data = []
            root.after(1, updateplots)
        except Exception as e:
          print(e)
        #root.update()
