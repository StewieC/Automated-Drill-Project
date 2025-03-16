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
# force=np.array([])
vibration = np.array([])


# Lock for synchronizing access to shared data
data_lock = threading.Lock()


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
