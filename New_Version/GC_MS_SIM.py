"""
GC/MS Simulation Main Runner
Version: ALPHA 0.1

This is the main file for the GC/MS Simulation. It will run the simulation and display the results.
Currently a WIP and may not be fully functional.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from GC_SIM import GCMSSimulation
import pygame

# Global simulation instance
global_simulation = None

class DebugController:
    def __init__(self, simulation):
        self.simulation = simulation
        self.settings = {
            "efficiency": 50,
            "speed": 5,
            "temperature": 250
        }

    def apply_settings(self, settings):
        """Apply debug settings to simulation"""
        self.settings.update(settings)

        if self.simulation:
            # Update simulation parameters based on debug settings
            speed_factor = settings["speed"] / 5.0  # normalize to base speed of 5

            # Modify simulation parameters
            if 'start_temp' in self.simulation.sliders:
                self.simulation.sliders['start_temp'].value = settings["temperature"]

            # Adjust separation efficiency by modifying relevant parameters
            efficiency_factor = settings["efficiency"] / 50.0  # normalize to base efficiency of 50
            if hasattr(self.simulation, 'gc_params'):
                self.simulation.gc_params.default_delta_H *= efficiency_factor

def create_debug_controls(simulation):
    """Create debug control window"""
    debug_window = tk.Toplevel()
    debug_window.title("GC-MS Debug Controls")
    debug_window.geometry("400x300")

    controller = DebugController(simulation)

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
        settings = {
            "efficiency": sep_efficiency.get(),
            "speed": sim_speed.get(),
            "temperature": float(temp_control.get())
        }
        controller.apply_settings(settings)
        print("Debug settings applied:", settings)

    ttk.Button(debug_window, text="Apply Settings", command=apply_settings).pack(pady=10)

    return debug_window

def run_simulation(debug_mode=False):
    """Run the GC/MS simulation"""
    global global_simulation

    if debug_mode:
        print("DEBUG MODE ENABLED")
        root = tk.Tk()
        root.withdraw()

        # Create simulation instance
        global_simulation = GCMSSimulation()

        # Create debug controls
        debug_window = create_debug_controls(global_simulation)

        # Create main window for additional controls if needed
        main_window = tk.Toplevel()
        main_window.title("GC-MS Simulation")
        main_window.geometry("400x200")

        # Add stop button
        def stop_simulation():
            if global_simulation:
                pygame.quit()
                root.quit()

        ttk.Button(main_window, text="Stop Simulation", command=stop_simulation).pack(pady=10)

        # Run simulation in a separate thread
        import threading
        sim_thread = threading.Thread(target=global_simulation.run)
        sim_thread.daemon = True
        sim_thread.start()

        # Start tkinter main loop
        root.mainloop()
    else:
        # Show welcome message
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showinfo('GC/MS Simulation ALPHA 0.1',
                             'Welcome to the GC/MS Simulation! \n \n'
                             'If you would like to run in DEBUG mode, please change the DEBUG '
                             'variable to True. \n\n Press OK to continue.')

        # Run simulation normally
        simulation = GCMSSimulation()
        global_simulation = simulation
        simulation.run()

if __name__ == "__main__":
    DEBUG = False  # Set to True to enable debug mode
    run_simulation(DEBUG)