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