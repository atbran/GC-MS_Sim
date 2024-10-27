from GC_MS_SIM_CLASSES import GCMSSimulation
import tkinter as tk
from tkinter import messagebox

# Welcome message
DEBUG = False

tk.Tk().withdraw()
tk.messagebox.showinfo('GC/MS Simulation ALPHA 0.1',
                       'Welcome to the GC/MS Simulation! \n \n'
                       'If you would like to run in DEBUG mode, please change the DEBUG variable in the GCMSSimulation class to True. \n\n Press OK to continue.')


if __name__ == "__main__":
    simulation = GCMSSimulation()
    simulation.run()