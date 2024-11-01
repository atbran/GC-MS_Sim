# gc_ui.py
import pygame
import math

# Constants
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
DETECTOR_WIDTH = 20
DETECTOR_HEIGHT = 100
GRAPH_WIDTH = 400
GRAPH_HEIGHT = 300
GRAPH_X = 900
GRAPH_Y = 150

# Colors
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
        label_surface = self.font.render(f"{self.label}: {self.value:.3f}", True, BLACK)
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
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                self.active = False
        return False


class ToggleButton(Button):
    def __init__(self, x, y, width, height, text, initial_state=False):
        super().__init__(x, y, width, height, text)
        self.state = initial_state

    def draw(self, screen):
        color = GRAY if self.state else WHITE
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                return True
        return False


class ChromatogramDisplay:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen, chromatogram):
        if not chromatogram:
            return

        # Draw axes
        pygame.draw.line(screen, BLACK,
                         (GRAPH_X, GRAPH_Y + GRAPH_HEIGHT),
                         (GRAPH_X + GRAPH_WIDTH, GRAPH_Y + GRAPH_HEIGHT))
        pygame.draw.line(screen, BLACK,
                         (GRAPH_X, GRAPH_Y),
                         (GRAPH_X, GRAPH_Y + GRAPH_HEIGHT))

        # Draw labels
        time_label = self.font.render("Time (min)", True, BLACK)
        screen.blit(time_label, (GRAPH_X + GRAPH_WIDTH // 2 - 30,
                                 GRAPH_Y + GRAPH_HEIGHT + 30))

        intensity_label = self.font.render("Intensity", True, BLACK)
        intensity_label = pygame.transform.rotate(intensity_label, 90)
        screen.blit(intensity_label, (GRAPH_X - 40, GRAPH_Y + GRAPH_HEIGHT // 2 - 30))

        # Draw data
        max_time = max([p[0] for p in chromatogram]) if chromatogram else 1
        max_intensity = max([p[1] for p in chromatogram]) if chromatogram else 1

        time_scale = GRAPH_WIDTH / max(max_time, 1)
        intensity_scale = GRAPH_HEIGHT / max(max_intensity, 1)

        points = [(GRAPH_X + min(p[0] * time_scale, GRAPH_WIDTH),
                   GRAPH_Y + GRAPH_HEIGHT - min(p[1] * intensity_scale, GRAPH_HEIGHT))
                  for p in chromatogram]

        if len(points) > 1:
            pygame.draw.lines(screen, BLACK, False, points)

        # Draw time axis marks and labels
        num_markers = 5
        for i in range(num_markers + 1):
            time_value = (max_time * i) / num_markers
            x_pos = GRAPH_X + (GRAPH_WIDTH * i) / num_markers

            pygame.draw.line(screen, BLACK,
                             (x_pos, GRAPH_Y + GRAPH_HEIGHT),
                             (x_pos, GRAPH_Y + GRAPH_HEIGHT + 5))

            time_text = self.font.render(f"{time_value:.1f}", True, BLACK)
            screen.blit(time_text, (x_pos - 15, GRAPH_Y + GRAPH_HEIGHT + 10))