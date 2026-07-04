import pygame
import random
import math
from settings import *

class Particle:
    """A visual particle that bursts outward from the food when eaten, fading and shrinking over time."""
    def __init__(self, x, y):
        # Position in float pixels for smooth sub-pixel movement
        self.x = float(x)
        self.y = float(y)
        
        # Random initial velocity (direction and speed)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # Appearance details
        self.color = random.choice(PARTICLE_COLORS)
        self.size = random.uniform(3.0, 6.0)
        self.life = 1.0  # Starts at 100% life
        self.decay = random.uniform(0.02, 0.05)  # Fades at random rate

    def update(self):
        """Updates particle movement, friction, and decay."""
        self.x += self.vx
        self.y += self.vy
        
        # Apply slight air resistance (drag)
        self.vx *= 0.95
        self.vy *= 0.95
        
        # Fade out and shrink
        self.life -= self.decay
        self.size = max(0.0, self.size - self.decay * 3)

    def draw(self, surface):
        """Draws the particle with a transparent alpha value representing its remaining life."""
        if self.life <= 0 or self.size <= 0:
            return
            
        s_size = int(self.size * 2) + 2
        # Create a temporary surface to draw transparent shapes
        temp_surface = pygame.Surface((s_size, s_size), pygame.SRCALPHA)
        color_with_alpha = (*self.color, int(self.life * 255))
        
        # Draw particle on temp surface and blit it to main screen
        pygame.draw.circle(temp_surface, color_with_alpha, (s_size // 2, s_size // 2), self.size)
        surface.blit(temp_surface, (int(self.x - s_size // 2), int(self.y - s_size // 2)))


class Food:
    """Manages food position, random placement, pulse animations, and detailed graphics."""
    def __init__(self):
        self.position = (0, 0)
        # Animation properties for the glowing outer ring
        self.pulse = 0.0
        self.pulse_dir = 1.0
        
    def spawn(self, snake_body):
        """Places the food in a random cell that does not overlap with the snake."""
        # Standard fast random placement
        attempts = 0
        while attempts < 1000:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in snake_body:
                self.position = (x, y)
                return
            attempts += 1
            
        # Fallback: exact lookup of remaining squares (only when snake covers most of the board)
        empty_cells = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if (x, y) not in snake_body:
                    empty_cells.append((x, y))
        if empty_cells:
            self.position = random.choice(empty_cells)

    def update(self):
        """Animates the pulse of the outer glowing halo."""
        self.pulse += self.pulse_dir * 0.05
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_dir = -1.0
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_dir = 1.0

    def draw(self, surface):
        """Draws the food as a stylized glowing red apple with a stem and leaf."""
        grid_x, grid_y = self.position
        x = grid_x * GRID_SIZE
        y = grid_y * GRID_SIZE
        center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        
        # 1. Glowing outer halo (semi-transparent circle under the apple)
        glow_radius = int(GRID_SIZE // 2 + 1 + self.pulse * 5)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        glow_alpha = int(60 + self.pulse * 40)
        pygame.draw.circle(glow_surf, (*COLOR_FOOD_GLOW, glow_alpha), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (center[0] - glow_radius, center[1] - glow_radius))
        
        # 2. Main Apple Body (Red circle)
        apple_radius = GRID_SIZE // 2 - 2
        pygame.draw.circle(surface, COLOR_FOOD, center, apple_radius)
        
        # 3. Glossy Highlight (Tiny white circle inside, offset slightly)
        hl_center = (center[0] - 2, center[1] - 2)
        pygame.draw.circle(surface, (255, 255, 255), hl_center, 2)
        
        # 4. Brown stem
        stem_start = (center[0], center[1] - apple_radius + 1)
        stem_end = (center[0] + 1, center[1] - apple_radius - 2)
        pygame.draw.line(surface, (120, 80, 40), stem_start, stem_end, 2)
        
        # 5. Green leaf
        leaf_center = (center[0] + 3, center[1] - apple_radius - 2)
        # Small green ellipse
        leaf_surf = pygame.Surface((6, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf_surf, (34, 197, 94), (0, 0, 6, 4))
        # Rotate leaf slightly and blit
        leaf_surf = pygame.transform.rotate(leaf_surf, 30)
        surface.blit(leaf_surf, (leaf_center[0] - 2, leaf_center[1] - 2))
