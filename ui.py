import pygame
import math
from settings import *

def lerp_color(c1, c2, t):
    """Linearly interpolates between two colors."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def load_fonts():
    """Loads modern system fonts with fallbacks."""
    font_names = ["Segoe UI", "Arial", "Helvetica", "sans-serif"]
    return {
        'small': pygame.font.SysFont(font_names, 18),
        'medium': pygame.font.SysFont(font_names, 24),
        'large': pygame.font.SysFont(font_names, 36),
        'xlarge': pygame.font.SysFont(font_names, 68, bold=True)
    }

class Button:
    """A premium interactive UI button with smooth hover fade and click scale effects."""
    def __init__(self, x, y, width, height, text, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        
        # Animation properties
        self.hover_t = 0.0
        self.is_hovered = False

    def update(self, mouse_pos):
        """Updates hover states and processes smooth transitions."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered:
            self.hover_t = min(1.0, self.hover_t + 0.15)  # Fade in
        else:
            self.hover_t = max(0.0, self.hover_t - 0.15)  # Fade out

    def check_click(self, mouse_pos, event):
        """Checks if a left-click event occurred inside the button boundaries."""
        if self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.callback:
                self.callback()
            return True
        return False

    def draw(self, surface, fonts):
        """Renders the button with rounded corners, interactive borders, and text."""
        # Interpolate background color on hover
        bg_color = lerp_color(COLOR_BUTTON, COLOR_BUTTON_HOVER, self.hover_t)
        
        # Inflate rect slightly when hovered for a 3D scaling effect
        inflate_amount = int(self.hover_t * 2)
        draw_rect = self.rect.inflate(inflate_amount * 2, inflate_amount * 2)
        
        # Draw background and border
        pygame.draw.rect(surface, bg_color, draw_rect, border_radius=8)
        border_color = lerp_color(COLOR_BUTTON_BORDER, COLOR_ACCENT, self.hover_t)
        pygame.draw.rect(surface, border_color, draw_rect, width=2, border_radius=8)
        
        # Render text centered
        text_surf = fonts['medium'].render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)


class Transition:
    """Handles smooth fading transitions between different game states."""
    def __init__(self):
        self.alpha = 0
        self.target_alpha = 0
        self.speed = 15
        self.on_complete_callback = None
        self.active = False
        
    def fade_to(self, callback):
        """Triggers a fade-out to black, running the callback at peak opacity."""
        self.alpha = 0
        self.target_alpha = 255
        self.on_complete_callback = callback
        self.active = True
        self.speed = 15
        
    def fade_in(self):
        """Triggers a fade-in from black to transparency."""
        self.alpha = 255
        self.target_alpha = 0
        self.on_complete_callback = None
        self.active = True
        self.speed = -15
        
    def update(self):
        """Advances transition progress."""
        if not self.active:
            return
            
        self.alpha += self.speed
        if self.speed > 0:  # Fading to black
            if self.alpha >= 255:
                self.alpha = 255
                self.active = False
                if self.on_complete_callback:
                    self.on_complete_callback()
        else:  # Fading to transparent
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False

    def draw(self, surface):
        """Blits a full-screen alpha overlay to perform the fade."""
        if self.alpha > 0:
            fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            fade_surf.fill(COLOR_BG)
            fade_surf.set_alpha(self.alpha)
            surface.blit(fade_surf, (0, 0))


class Countdown:
    """Smooth scaling and fading 3-2-1 countdown sequence before game starts."""
    def __init__(self):
        self.count = 3
        self.timer = 0
        self.scale = 2.0
        self.alpha = 255
        self.active = False
        
    def start(self):
        self.count = 3
        self.timer = pygame.time.get_ticks()
        self.scale = 2.0
        self.alpha = 255
        self.active = True
        
    def update(self):
        """Updates numbers every second and sets scale/fade curves."""
        if not self.active:
            return False
            
        now = pygame.time.get_ticks()
        elapsed = now - self.timer
        
        if elapsed >= 1000:
            self.count -= 1
            self.timer = now
            self.scale = 2.0
            self.alpha = 255
            if self.count <= 0:
                self.active = False
                return True  # Countdown ended
        else:
            # Animate scaling down and fading out
            t = elapsed / 1000.0
            self.scale = 2.0 - t * 1.5
            self.alpha = int(255 * (1.0 - t))
            
        return False

    def draw(self, surface, fonts):
        """Draws the scaling countdown text."""
        if not self.active:
            return
            
        text_str = str(self.count) if self.count > 0 else "GO!"
        text_surf = fonts['xlarge'].render(text_str, True, COLOR_ACCENT)
        
        w, h = text_surf.get_size()
        scaled_w = int(w * self.scale)
        scaled_h = int(h * self.scale)
        
        if scaled_w > 0 and scaled_h > 0:
            scaled_surf = pygame.transform.smoothscale(text_surf, (scaled_w, scaled_h))
            
            # Apply alpha transparency via temporary Surface
            alpha_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
            alpha_surf.blit(scaled_surf, (0, 0))
            alpha_surf.set_alpha(self.alpha)
            
            rect = alpha_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            surface.blit(alpha_surf, rect)


def draw_grid(surface):
    """Draws a subtle modern grid background."""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (WINDOW_WIDTH, y), 1)


def draw_header_hud(surface, score, high_score, speed_level, difficulty, music_muted, fonts):
    """Draws a beautiful translucent HUD bar at the top of the screen."""
    hud_height = 45
    
    # Glassmorphic HUD background
    hud_surf = pygame.Surface((WINDOW_WIDTH, hud_height), pygame.SRCALPHA)
    pygame.draw.rect(hud_surf, (15, 23, 42, 200), (0, 0, WINDOW_WIDTH, hud_height)) # semi-transparent Slate 900
    pygame.draw.line(hud_surf, COLOR_GRID, (0, hud_height - 1), (WINDOW_WIDTH, hud_height - 1), 1)
    surface.blit(hud_surf, (0, 0))
    
    # Draw Score (Left)
    score_surf = fonts['medium'].render(f"Score: {score}", True, COLOR_TEXT)
    surface.blit(score_surf, (20, 10))
    
    # Draw High Score (Center)
    hs_surf = fonts['medium'].render(f"High Score: {high_score}", True, COLOR_ACCENT)
    hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, 22))
    surface.blit(hs_surf, hs_rect)
    
    # Draw Speed / Difficulty Info (Right)
    diff_text = f"[{difficulty}] Speed: Lvl {speed_level}"
    info_surf = fonts['medium'].render(diff_text, True, COLOR_TEXT_MUTED)
    info_rect = info_surf.get_rect(topright=(WINDOW_WIDTH - 20, 10))
    surface.blit(info_surf, info_rect)
    
    # Mute indicator in bottom-left corner of screen during gameplay
    mute_status = "MUTED" if music_muted else "ON"
    mute_color = COLOR_FOOD if music_muted else COLOR_TEXT_MUTED
    mute_surf = fonts['small'].render(f"Music: {mute_status} [M]", True, mute_color)
    surface.blit(mute_surf, (20, WINDOW_HEIGHT - 30))


def draw_title_logo(surface, fonts, time_ms):
    """Draws an animated pulsing game logo with glowing effects."""
    # Sinusoidal hover animation
    y_offset = int(math.sin(time_ms * 0.003) * 6)
    title_y = 130 + y_offset
    
    # Neo-glow outline effect
    glow_surf = fonts['xlarge'].render("S N A K E", True, COLOR_SNAKE_HEAD)
    glow_rect = glow_surf.get_rect(center=(WINDOW_WIDTH // 2, title_y))
    
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
        surface.blit(glow_surf, glow_rect.move(dx, dy))
        
    # Main foreground text
    main_surf = fonts['xlarge'].render("S N A K E", True, COLOR_TEXT)
    surface.blit(main_surf, glow_rect)


def draw_paused_overlay(surface, fonts):
    """Draws a blur-like overlay and Paused text when the game is paused."""
    # Semi-transparent backdrop
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (15, 23, 42, 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    surface.blit(overlay, (0, 0))
    
    # Draw Paused box
    box_w, box_h = 280, 120
    box_rect = pygame.Rect((WINDOW_WIDTH - box_w) // 2, (WINDOW_HEIGHT - box_h) // 2, box_w, box_h)
    pygame.draw.rect(surface, COLOR_BUTTON, box_rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_ACCENT, box_rect, width=2, border_radius=12)
    
    # Text
    p_surf = fonts['large'].render("PAUSED", True, COLOR_TEXT)
    p_rect = p_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 15))
    surface.blit(p_surf, p_rect)
    
    r_surf = fonts['small'].render("Press P to Resume", True, COLOR_TEXT_MUTED)
    r_rect = r_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
    surface.blit(r_surf, r_rect)


def draw_game_over_screen(surface, score, high_score, buttons, fonts):
    """Draws the final game-over results and interactive action buttons."""
    # Semi-transparent dark overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (8, 12, 21, 200), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    surface.blit(overlay, (0, 0))
    
    # Game Over Title
    go_surf = fonts['xlarge'].render("GAME OVER", True, COLOR_FOOD)
    go_rect = go_surf.get_rect(center=(WINDOW_WIDTH // 2, 140))
    surface.blit(go_surf, go_rect)
    
    # Stats Panel
    panel_w, panel_h = 320, 140
    panel_rect = pygame.Rect((WINDOW_WIDTH - panel_w) // 2, 210, panel_w, panel_h)
    pygame.draw.rect(surface, COLOR_BUTTON, panel_rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_BUTTON_BORDER, panel_rect, width=2, border_radius=12)
    
    # Scores
    score_surf = fonts['medium'].render(f"Final Score: {score}", True, COLOR_TEXT)
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, 245))
    surface.blit(score_surf, score_rect)
    
    hs_surf = fonts['medium'].render(f"High Score: {high_score}", True, COLOR_ACCENT)
    hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, 285))
    surface.blit(hs_surf, hs_rect)
    
    # Direct Key Prompts
    prompt_surf = fonts['small'].render("Press R to Restart   |   Press ESC to Main Menu", True, COLOR_TEXT_MUTED)
    prompt_rect = prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, 325))
    surface.blit(prompt_surf, prompt_rect)
    
    # Render Buttons (Play Again, Main Menu)
    for btn in buttons:
        btn.draw(surface, fonts)
