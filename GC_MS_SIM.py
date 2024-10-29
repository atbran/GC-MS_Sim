""""This is the main file for the GC/MS Simulation. It will run the simulation and display the results.
It currently is a WIP and may not be fully functional. It is currently in ALPHA 0.1. """""


# TODO Add more functionality to the simulation, including more options for the user to input data.
# TODO Add error handling to the simulation.
# TODO FIX issues with actual GC controls (IE temperature, ramp rate, etc.)
# TODO Add documentation to the code.
# TODO make it look pretty


from GC_MS_SIM_CLASSES import GCMSSimulation
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Welcome message
DEBUG = False


def create_debug_controls():
    debug_window = tk.Toplevel()
    debug_window.title("GC-MS Debug Controls")
    debug_window.geometry("400x300")

    # Create frames for organization
    controls_frame = ttk.LabelFrame(debug_window, text="Simulation Parameters", padding=10)
    controls_frame.pack(fill="x", padx=5, pady=5)

    # Separation efficiency slider
    ttk.Label(controls_frame, text="Separation Efficiency:").pack()
    sep_efficiency = ttk.Scale(controls_frame, from_=0, to=100, orient="horizontal")
    sep_efficiency.set(50)
    sep_efficiency.pack(fill="x")

    # Simulation speed slider
    ttk.Label(controls_frame, text="Simulation Speed:").pack()
    sim_speed = ttk.Scale(controls_frame, from_=1, to=10, orient="horizontal")
    sim_speed.set(5)
    sim_speed.pack(fill="x")

    # Temperature control
    ttk.Label(controls_frame, text="Temperature (°C):").pack()
    temp_control = ttk.Entry(controls_frame)
    temp_control.insert(0, "250")
    temp_control.pack(fill="x")

    # Apply button
    def apply_settings():
        # Add your settings application logic here
        settings = {
            "efficiency": sep_efficiency.get(),
            "speed": sim_speed.get(),
            "temperature": float(temp_control.get())
        }
        print("Debug settings applied:", settings)

    ttk.Button(debug_window, text="Apply Settings", command=apply_settings).pack(pady=10)

    return debug_window


if DEBUG:
    print("DEBUG MODE ENABLED")
    root = tk.Tk()  # Create the root window
    root.withdraw()  # Hide the root window

    debug_window = create_debug_controls()

    # Create your main simulation window here
    main_window = tk.Toplevel()
    main_window.title("GC-MS Simulation")
    main_window.geometry("800x600")

    # Start the main event loop
    root.mainloop()
else:
    tk.Tk().withdraw()
    tk.messagebox.showinfo('GC/MS Simulation ALPHA 0.1',
                           'Welcome to the GC/MS Simulation! \n \n'
                           'If you would like to run in DEBUG mode, please change the DEBUG variable in the GCMSSimulation class to True. \n\n Press OK to continue.')












if __name__ == "__main__":
    simulation = GCMSSimulation()
    simulation.run()