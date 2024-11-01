# gc_core.py
import math
import random
from gc_ui import COLORS


class GCParameters:
    """Physical and chemical parameters for GC simulation"""

    def __init__(self):
        # Fundamental constants
        self.R = 8.314  # Universal gas constant (J/mol·K)
        self.default_delta_H = 20000  # Reduced enthalpy change for more moderate temperature effects

        # Carrier gas properties
        self.carrier_gases = {
            'He': {
                'viscosity': 1.0,  # Relative viscosity
                'density': 0.1786,  # g/L at STP
                'diffusivity': 0.7,  # Relative diffusion coefficient
                'thermal_conductivity': 0.151,  # W/(m·K)
            },
            'H2': {
                'viscosity': 0.7,
                'density': 0.0899,
                'diffusivity': 1.0,
                'thermal_conductivity': 0.187,
            },
            'N2': {
                'viscosity': 1.3,
                'density': 1.251,
                'diffusivity': 0.5,
                'thermal_conductivity': 0.026,
            }
        }

    def calculate_temp_program(self, current_time, start_temp, end_temp, ramp_rate,
                               initial_hold, final_hold):
        """Calculate temperature with more gradual changes"""
        if current_time < initial_hold * 60:
            return start_temp, False, False

        ramp_time = current_time - (initial_hold * 60)
        current_temp = start_temp + (ramp_rate * ramp_time / 60)

        if current_temp >= end_temp:
            current_temp = end_temp
            final_hold_started = True
        else:
            final_hold_started = False

        return current_temp, True, final_hold_started

    def calculate_van_t_hoff(self, temp, ref_temp):
        """Modified van't Hoff calculation for smoother temperature effects"""
        # Convert to Kelvin
        T = temp + 273.15
        T_ref = ref_temp + 273.15

        # Calculate temperature factor with dampened effect
        temp_factor = math.exp((self.default_delta_H / self.R) * (1 / T_ref - 1 / T))

        # Normalize the temperature factor to prevent extreme values
        temp_factor = max(0.5, min(2.0, temp_factor))

        return temp_factor

    def calculate_flow_parameters(self, pressure_psi, carrier_gas, column_length):
        """Calculate flow parameters with increased base velocity"""
        gas_properties = self.carrier_gases[carrier_gas]

        # Convert units with increased flow
        column_radius = 0.125 / 1000  # mm to meters
        column_length = column_length * 15  # Reduced effective length for faster movement
        viscosity = gas_properties['viscosity'] * 1e-5  # to Pa·s
        pressure_pa = pressure_psi * 6894.76  # psi to Pa

        # Calculate velocity with higher base rate
        velocity = (pressure_pa * math.pi * column_radius ** 4) / (8 * viscosity * column_length)
        velocity *= 2  # Double the base velocity

        # Calculate diffusion coefficient
        diffusion_base = gas_properties['diffusivity'] * 1e-5

        return velocity, diffusion_base


class Particle:
    """Represents a single analyte particle in the GC column"""

    def __init__(self, x, y, retention_factor, particle_type, base_velocity, diffusion_coeff):
        self.x = x
        self.y = y
        self.retention_factor = retention_factor
        self.particle_type = particle_type
        self.time = 0
        self.detected = False
        self.base_velocity = base_velocity * 1000  # Increase base velocity for better visualization
        self.diffusion_coeff = diffusion_coeff
        self.peak_width = 1.0

    def get_color(self):
        """Get particle color based on type"""
        return COLORS[self.particle_type]

    def calculate_van_deemter(self, velocity):
        """Calculate HETP using simplified van Deemter equation"""
        # Simplified coefficients for better visualization
        A = 0.1  # Reduced eddy diffusion
        B = 0.2 * self.diffusion_coeff  # Reduced longitudinal diffusion
        C = 0.01  # Reduced mass transfer resistance

        hetp = A + (B / velocity) + (C * velocity)
        return hetp

    def move(self, dt, temp_factor, current_temp, column_y):
        """Update particle position with modified movement parameters"""
        self.time += dt

        # Calculate effective velocity with reduced retention effect
        velocity = self.base_velocity / (self.retention_factor ** 0.5)  # Square root to reduce retention effect
        hetp = self.calculate_van_deemter(velocity)

        # Increase temperature factor influence and overall speed
        effective_velocity = (velocity / (1 + hetp)) * (temp_factor ** 0.5) * 2

        # Update position with guaranteed minimum speed
        min_speed = self.base_velocity * 0.1  # Minimum speed to prevent stalling
        self.x += max(effective_velocity * dt, min_speed * dt)

        # Calculate more pronounced peak broadening
        temp_contribution = math.sqrt(current_temp / 323.15)
        time_contribution = math.sqrt(self.time / 10)
        diffusion_contribution = math.sqrt(2 * self.diffusion_coeff * self.time)

        self.peak_width = (1.0 + diffusion_contribution) * temp_contribution * time_contribution

        # More pronounced vertical movement
        amplitude = 30 * (1 / temp_factor) * math.exp(-self.time / 200)  # Increased amplitude, slower decay
        random_offset = random.gauss(0, self.peak_width)
        self.y = column_y + amplitude * math.sin(0.02 * self.x) + random_offset


class ParticleManager:
    """Manages creation and behavior of particle groups"""

    def __init__(self, gc_params):
        self.gc_params = gc_params

    def create_particle_group(self, count, particle_type, x_pos, y_pos, injection_width,
                              base_velocity, diffusion_base, retention_factor, temp_factor):
        """Create a group of particles with similar properties"""
        particles = []

        for _ in range(count):
            # Add variation to injection position
            x = x_pos + random.gauss(0, injection_width)
            y = random.gauss(y_pos, injection_width / 2)

            # Add variation to retention factor
            rf = retention_factor * temp_factor
            rf_variation = random.gauss(0, 0.05 * rf)  # 5% variation
            final_rf = rf + rf_variation

            # Calculate diffusion coefficient based on molecular size
            diffusion_coeff = diffusion_base * (1 / final_rf)

            particles.append(Particle(x, y, final_rf, particle_type,
                                      base_velocity, diffusion_coeff))

        return particles