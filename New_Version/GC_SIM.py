# gc_simulation.py
import pygame
import math
import random
from gc_ui import *
from gc_core import GCParameters, ParticleManager


class GCMSSimulation:
    """Main simulation class for GC/MS"""

    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Create display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GCMS Simulation ALPHA 0.1")

        # Initialize core components
        self.gc_params = GCParameters()
        self.particle_manager = ParticleManager(self.gc_params)

        # Column parameters
        self.BASE_COLUMN_START_X = 300
        self.BASE_COLUMN_END_X = 800
        self.column_start_x = self.BASE_COLUMN_START_X
        self.column_end_x = self.BASE_COLUMN_END_X
        self.column_y = 700  # Base Y position for column

        # Initialize UI components
        self.init_ui_components()

        # Initialize simulation state
        self.particles = []
        self.chromatogram = []
        self.detector_counts = {
            'solvent': [], 'nonpolar1': [], 'nonpolar2': [], 'semipolar1': [],
            'semipolar2': [], 'polar1': [], 'polar2': [], 'verypolar': []
        }

        # Simulation control
        self.running = False
        self.paused = False
        self.simulation_time = 0
        self.initial_hold_complete = False
        self.final_hold_started = False
        self.chromatogram_display = ChromatogramDisplay()

    def init_ui_components(self):
        """Initialize all UI components"""
        self.sliders = {
            'count': Slider(50, 50, 200, 20, 100, 1000, 500, "Particle Count"),
            'solvent': Slider(50, 100, 200, 20, 0.05, 1.0, .1, "Solvent RF"),
            'nonpolar1': Slider(50, 150, 200, 20, 0.1, 1.0, .5, "Nonpolar 1 RF"),
            'nonpolar2': Slider(50, 200, 200, 20, .2, 1.2, .7, "Nonpolar 2 RF"),
            'semipolar1': Slider(50, 250, 200, 20, 1.0, 2, 1.2, "Semipolar 1 RF"),
            'semipolar2': Slider(50, 300, 200, 20, 1.5, 3.5, 2.5, "Semipolar 2 RF"),
            'polar1': Slider(50, 350, 200, 20, 2.0, 4.0, 2.8, "Polar 1 RF"),
            'polar2': Slider(50, 400, 200, 20, 2.0, 4.0, 3.2, "Polar 2 RF"),
            'verypolar': Slider(50, 450, 200, 20, 2.5, 5.0, 3.5, "Very Polar RF"),
            'column_length': Slider(50, 500, 200, 20, 0.1, 1.25, 1.0, "Column Length"),
            'start_temp': Slider(300, 50, 200, 20, 50, 300, 60, "Start Temp (°C)"),
            'end_temp': Slider(300, 100, 200, 20, 50, 300, 280, "End Temp (°C)"),
            'ramp_rate': Slider(300, 150, 200, 20, 1, 20, 10, "Ramp Rate (°C/min)"),
            'carrier_pressure': Slider(300, 200, 200, 20, 10, 60, 30, "Carrier Gas (psi)"),
            'split_ratio': Slider(300, 250, 200, 20, 1, 100, 50, "Split Ratio"),
            'initial_hold': Slider(300, 300, 200, 20, 0, 5, 1, "Initial Hold (min)"),
            'final_hold': Slider(300, 350, 200, 20, 0, 5, 1, "Final Hold (min)")
        }

        # Create buttons
        self.inject_button = Button(50, 550, 100, 40, "Inject")
        self.pause_button = Button(160, 550, 100, 40, "Pause")
        self.reset_button = Button(270, 550, 100, 40, "Reset")
        self.uniform_toggle = ToggleButton(380, 550, 100, 40, "Uniform", False)

    def inject_particles(self):
        """Initialize particle injection"""
        # Calculate base parameters
        base_velocity, diffusion_base = self.gc_params.calculate_flow_parameters(
            self.sliders['carrier_pressure'].value,
            'He',  # Default to Helium
            self.sliders['column_length'].value
        )

        # Get temperature factors
        temp_factor = self.calculate_temp_factor()[0]

        # Calculate injection band width
        injection_width = 20 / self.sliders['split_ratio'].value

        self.particles = []
        count = int(self.sliders['count'].value)
        particle_types = list(self.detector_counts.keys())

        if self.uniform_toggle.state:
            # Uniform distribution
            per_type = count // len(particle_types)
            remainder = count % len(particle_types)
            for p_type in particle_types:
                type_count = per_type + (1 if remainder > 0 else 0)
                remainder -= 1

                particles = self.particle_manager.create_particle_group(
                    type_count, p_type, self.column_start_x, self.column_y,
                    injection_width, base_velocity, diffusion_base,
                    self.sliders[p_type].value, temp_factor
                )
                self.particles.extend(particles)
        else:
            # Random distribution
            for _ in range(count):
                p_type = random.choice(particle_types)
                particles = self.particle_manager.create_particle_group(
                    1, p_type, self.column_start_x, self.column_y,
                    injection_width, base_velocity, diffusion_base,
                    self.sliders[p_type].value, temp_factor
                )
                self.particles.extend(particles)

        # Reset simulation parameters
        self.reset_simulation_parameters()

    def reset_simulation_parameters(self):
        """Reset all simulation parameters"""
        self.chromatogram = []
        self.detector_counts = {k: [] for k in self.detector_counts.keys()}
        self.running = True
        self.paused = False
        self.simulation_time = 0
        self.initial_hold_complete = False
        self.final_hold_started = False

    def calculate_temp_factor(self):
        """Calculate temperature factor and current temperature"""
        current_temp, initial_complete, final_started = self.gc_params.calculate_temp_program(
            self.simulation_time,
            self.sliders['start_temp'].value,
            self.sliders['end_temp'].value,
            self.sliders['ramp_rate'].value,
            self.sliders['initial_hold'].value,
            self.sliders['final_hold'].value
        )

        temp_factor = self.gc_params.calculate_van_t_hoff(
            current_temp,
            self.sliders['start_temp'].value
        )

        return temp_factor, current_temp

    def update(self, dt):
        """Update simulation state"""
        # Update column dimensions based on length
        length_factor = self.sliders['column_length'].value
        self.column_start_x = int(self.BASE_COLUMN_START_X * length_factor)
        self.column_end_x = int(self.BASE_COLUMN_END_X * length_factor)

        if not self.running or self.paused:
            return

        self.simulation_time += dt
        temp_factor, current_temp = self.calculate_temp_factor()

        # Update particles
        for particle in self.particles:
            if not particle.detected:
                particle.move(dt, temp_factor, current_temp, self.column_y)
                if (self.column_end_x <= particle.x <= self.column_end_x + DETECTOR_WIDTH and
                        not particle.detected):
                    particle.detected = True
                    self.detector_counts[particle.particle_type].append(particle.time)

        self.update_chromatogram()

    def update_chromatogram(self):
        """Update chromatogram data"""
        if not self.running:
            return

        current_time = max([p.time for p in self.particles]) if self.particles else 0
        time_window = 1.0
        max_time = current_time + 1
        histogram = {t: 0 for t in range(int(max_time / time_window) + 1)}

        for particle_type, times in self.detector_counts.items():
            for t in times:
                bin_index = int(t / time_window)
                histogram[bin_index] = histogram.get(bin_index, 0) + 1

        self.chromatogram = []
        smoothing_window = 3
        for t in sorted(histogram.keys()):
            start_idx = max(0, t - smoothing_window)
            end_idx = t + smoothing_window + 1
            count = sum(histogram.get(i, 0) for i in range(start_idx, end_idx))
            count = count / (end_idx - start_idx)
            self.chromatogram.append((t * time_window, count))

    def draw(self):
        """Draw all simulation components"""
        self.screen.fill(WHITE)

        # Draw UI components
        for slider in self.sliders.values():
            slider.draw(self.screen)
        self.inject_button.draw(self.screen)
        self.pause_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        self.uniform_toggle.draw(self.screen)

        # Draw column
        pygame.draw.line(self.screen, BLACK,
                         (self.column_start_x, self.column_y),
                         (self.column_end_x, self.column_y), 2)

        # Draw detector
        pygame.draw.rect(self.screen, BLACK,
                         (self.column_end_x, self.column_y - DETECTOR_HEIGHT / 2,
                          DETECTOR_WIDTH, DETECTOR_HEIGHT))

        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.get_color(),
                               (int(particle.x), int(particle.y)), 3)

        # Draw chromatogram
        self.chromatogram_display.draw(self.screen, self.chromatogram)
        pygame.display.flip()

    def run(self):
        """Main simulation loop"""
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle UI events
                for slider in self.sliders.values():
                    slider.handle_event(event)

                if self.inject_button.handle_event(event):
                    self.inject_particles()
                elif self.pause_button.handle_event(event):
                    self.paused = not self.paused
                elif self.reset_button.handle_event(event):
                    self.particles = []
                    self.reset_simulation_parameters()
                self.uniform_toggle.handle_event(event)

            dt = 0.5
            self.update(dt)
            self.draw()
            clock.tick(60)

        pygame.quit()