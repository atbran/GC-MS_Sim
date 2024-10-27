import pygame
import random
import math

pygame.init()
pygame.font.init()

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
DETECTOR_WIDTH = 20
DETECTOR_HEIGHT = 100
GRAPH_WIDTH = 400
GRAPH_HEIGHT = 300
GRAPH_X = 900
GRAPH_Y = 150
column_start_y = 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
COLORS = {
    'solvent': (255, 0, 0),
    'nonpolar1': (0, 255, 0),
    'nonpolar2': (0, 0, 255),
    'semipolar1': (255, 255, 0),
    'semipolar2': (255, 0, 255),
    'polar1': (0, 255, 255),
    'polar2': (128, 0, 0),
    'verypolar': (0, 128, 0)
}


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.handle_rect = pygame.Rect(0, 0, 10, height + 4)
        self.active = False
        self.font = pygame.font.SysFont(None, 24)
        self.update_handle()

    def update_handle(self):
        val_range = self.max_val - self.min_val
        pos = ((self.value - self.min_val) / val_range) * self.rect.width
        self.handle_rect.centerx = self.rect.left + pos
        self.handle_rect.centery = self.rect.centery

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.handle_rect)
        label_surface = self.font.render(f"{self.label}: {self.value:.1f}", True, BLACK)
        screen.blit(label_surface, (self.rect.left, self.rect.top - 20))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False
        elif event.type == pygame.MOUSEMOTION and self.active:
            rel_x = min(max(event.pos[0], self.rect.left), self.rect.right)
            val_range = self.max_val - self.min_val
            self.value = self.min_val + ((rel_x - self.rect.left) / self.rect.width) * val_range
            self.update_handle()


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, 24)
        self.active = False

    def draw(self, screen):
        color = GRAY if self.active else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
        return False


class Particle:
    def __init__(self, x, y, retention_factor, particle_type):
        self.x = x
        self.y = y
        self.retention_factor = retention_factor
        self.particle_type = particle_type
        self.time = 0
        self.detected = False

    def get_color(self):
        return COLORS[self.particle_type]

    def move(self, dt):
        self.time += dt
        self.x += (2.0 / self.retention_factor) * dt
        amplitude = 50
        frequency = 0.05
        self.y = column_start_y + amplitude * math.sin(frequency * self.x)


class GCMSSimulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("GCMS Simulation")

        self.BASE_COLUMN_START_X = 300
        self.BASE_COLUMN_END_X = 800

        self.column_start_x = self.BASE_COLUMN_START_X
        self.column_end_x = self.BASE_COLUMN_END_X

        self.sliders = {
            'count': Slider(50, 50, 200, 20, 100, 1000, 500, "Particle Count"),
            'solvent': Slider(50, 100, 200, 20, 1.0, 5.0, 1.0, "Solvent RF"),
            'nonpolar1': Slider(50, 150, 200, 20, 1.0, 5.0, 1.2, "Nonpolar 1 RF"),
            'nonpolar2': Slider(50, 200, 200, 20, 1.0, 5.0, 1.4, "Nonpolar 2 RF"),
            'semipolar1': Slider(50, 250, 200, 20, 1.0, 5.0, 1.6, "Semipolar 1 RF"),
            'semipolar2': Slider(50, 300, 200, 20, 1.0, 5.0, 1.8, "Semipolar 2 RF"),
            'polar1': Slider(50, 350, 200, 20, 1.0, 5.0, 2.0, "Polar 1 RF"),
            'polar2': Slider(50, 400, 200, 20, 1.0, 5.0, 2.2, "Polar 2 RF"),
            'verypolar': Slider(50, 450, 200, 20, 1.0, 5.0, 2.5, "Very Polar RF"),
            'column_length': Slider(50, 500, 200, 20, 0.1, 1.25, 1.0, "Column Length")
        }

        self.inject_button = Button(50, 550, 100, 40, "Inject")
        self.pause_button = Button(160, 550, 100, 40, "Pause")

        self.particles = []
        self.chromatogram = []
        self.detector_counts = {
            'solvent': [], 'nonpolar1': [], 'nonpolar2': [], 'semipolar1': [],
            'semipolar2': [], 'polar1': [], 'polar2': [], 'verypolar': []
        }

        self.running = False
        self.paused = False

    def inject_particles(self):
        self.particles = []
        count = int(self.sliders['count'].value)
        particle_types = list(self.detector_counts.keys())

        for _ in range(count):
            particle_type = random.choice(particle_types)
            x = random.uniform(self.column_start_x - 20, self.column_start_x)
            y = random.uniform(column_start_y - 50, column_start_y + 50)
            retention_factor = self.sliders[particle_type].value
            self.particles.append(Particle(x, y, retention_factor, particle_type))

        self.chromatogram = []
        self.detector_counts = {k: [] for k in particle_types}
        self.running = True
        self.paused = False

    def update(self, dt):
        length_factor = self.sliders['column_length'].value
        self.column_start_x = int(self.BASE_COLUMN_START_X * length_factor)
        self.column_end_x = int(self.BASE_COLUMN_END_X * length_factor)

        if not self.running or self.paused:
            return

        for particle in self.particles:
            if not particle.detected:
                particle.move(dt)
                if (self.column_end_x <= particle.x <= self.column_end_x + DETECTOR_WIDTH and
                        not particle.detected):
                    particle.detected = True
                    self.detector_counts[particle.particle_type].append(particle.time)

        if self.running:
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

    def draw_chromatogram(self):
        if not self.chromatogram:
            return

        pygame.draw.line(self.screen, BLACK,
                         (GRAPH_X, GRAPH_Y + GRAPH_HEIGHT),
                         (GRAPH_X + GRAPH_WIDTH, GRAPH_Y + GRAPH_HEIGHT))
        pygame.draw.line(self.screen, BLACK,
                         (GRAPH_X, GRAPH_Y),
                         (GRAPH_X, GRAPH_Y + GRAPH_HEIGHT))

        font = pygame.font.SysFont(None, 24)
        time_label = font.render("Time", True, BLACK)
        self.screen.blit(time_label, (GRAPH_X + GRAPH_WIDTH // 2 - 20,
                                      GRAPH_Y + GRAPH_HEIGHT + 10))
        intensity_label = font.render("Intensity", True, BLACK)
        intensity_label = pygame.transform.rotate(intensity_label, 90)
        self.screen.blit(intensity_label, (GRAPH_X - 40, GRAPH_Y + GRAPH_HEIGHT // 2))

        max_time = max([p[0] for p in self.chromatogram]) if self.chromatogram else 1
        max_intensity = max([p[1] for p in self.chromatogram]) if self.chromatogram else 1
        time_scale = GRAPH_WIDTH / max(max_time, 1)
        intensity_scale = GRAPH_HEIGHT / max(max_intensity, 1)

        points = [(GRAPH_X + min(p[0] * time_scale, GRAPH_WIDTH),
                   GRAPH_Y + GRAPH_HEIGHT - min(p[1] * intensity_scale, GRAPH_HEIGHT))
                  for p in self.chromatogram]
        if len(points) > 1:
            pygame.draw.lines(self.screen, BLACK, False, points)

        num_markers = 5
        for i in range(num_markers + 1):
            time_value = (max_time * i) / num_markers
            x_pos = GRAPH_X + (GRAPH_WIDTH * i) / num_markers
            pygame.draw.line(self.screen, BLACK,
                             (x_pos, GRAPH_Y + GRAPH_HEIGHT),
                             (x_pos, GRAPH_Y + GRAPH_HEIGHT + 5))
            time_text = font.render(f"{time_value:.1f}", True, BLACK)
            self.screen.blit(time_text, (x_pos - 15, GRAPH_Y + GRAPH_HEIGHT + 20))

    def draw(self):
        self.screen.fill(WHITE)

        for slider in self.sliders.values():
            slider.draw(self.screen)
        self.inject_button.draw(self.screen)
        self.pause_button.draw(self.screen)

        pygame.draw.line(self.screen, BLACK,
                         (self.column_start_x, column_start_y),
                         (self.column_end_x, column_start_y), 2)

        pygame.draw.rect(self.screen, BLACK,
                         (self.column_end_x, column_start_y - DETECTOR_HEIGHT / 2,
                          DETECTOR_WIDTH, DETECTOR_HEIGHT))

        for particle in self.particles:
            pygame.draw.circle(self.screen, particle.get_color(),
                               (int(particle.x), int(particle.y)), 3)

        self.draw_chromatogram()
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                for slider in self.sliders.values():
                    slider.handle_event(event)

                if self.inject_button.handle_event(event):
                    self.inject_particles()
                elif self.pause_button.handle_event(event):
                    self.paused = not self.paused

            dt = 0.5
            self.update(dt)
            self.draw()
            clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    simulation = GCMSSimulation()
    simulation.run()