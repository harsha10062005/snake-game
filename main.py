import pygame
import json
import os
import sys
from settings import *
from snake import Snake
from food import Food, Particle
from ui import (
    Button, Transition, Countdown, load_fonts, draw_grid,
    draw_header_hud, draw_title_logo, draw_paused_overlay,
    draw_game_over_screen
)

class GameController:
    """Central controller that runs the main game loop and manages state transitions."""
    def __init__(self):
        # Initialize Pygame subsystems
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Warning: Could not initialize pygame.mixer: {e}")

        # Setup screen and window caption
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Modern Snake Game")
        self.clock = pygame.Clock()

        # Load resources
        self.fonts = load_fonts()
        
        # State variables
        self.state = 'MENU'  # MENU, DIFFICULTY, INSTRUCTIONS, COUNTDOWN, PLAYING, PAUSED, GAME_OVER
        self.difficulty = 'Medium'
        self.score = 0
        self.speed_level = 1
        
        # Load high scores
        self.high_scores = self.load_high_score()
        
        # Audio setup
        self.music_muted = False
        self.load_sounds()

        # UI Sub-components
        self.transition = Transition()
        self.countdown = Countdown()

        # Game Objects
        self.snake = Snake()
        self.food = Food()
        self.particles = []

        # Tick handling for grid movement
        self.last_move_time = 0

        # Setup UI buttons
        self.setup_buttons()

        # Start ambient music loop
        self.play_music()

        # Initial screen fade in
        self.transition.fade_in()

    def load_high_score(self):
        """Loads scores from highscore.json with strict error checking and default fallbacks."""
        default_scores = {diff: 0 for diff in DIFFICULTY_SPEEDS}
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return {diff: data.get(diff, 0) for diff in DIFFICULTY_SPEEDS}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load highscore file ({e}). Starting fresh.")
        return default_scores

    def save_high_score(self):
        """Saves current difficulty score to highscore.json."""
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f, indent=4)
        except IOError as e:
            print(f"Warning: Could not write highscore to file ({e}).")

    def load_sounds(self):
        """Loads and sets volumes for game audio effects."""
        self.sound_food = None
        self.sound_gameover = None
        
        try:
            if os.path.exists(PATH_SOUND_FOOD):
                self.sound_food = pygame.mixer.Sound(PATH_SOUND_FOOD)
                self.sound_food.set_volume(0.3)
            if os.path.exists(PATH_SOUND_GAMEOVER):
                self.sound_gameover = pygame.mixer.Sound(PATH_SOUND_GAMEOVER)
                self.sound_gameover.set_volume(0.3)
        except Exception as e:
            print(f"Warning: Sound files could not be loaded: {e}")

    def play_music(self):
        """Starts looping the synthesized background track."""
        try:
            if os.path.exists(PATH_SOUND_MUSIC):
                pygame.mixer.music.load(PATH_SOUND_MUSIC)
                pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.15)
                pygame.mixer.music.play(-1)  # -1 loops indefinitely
        except Exception as e:
            print(f"Warning: Music could not be loaded or played: {e}")

    def toggle_mute(self):
        """Toggles audio mute state for music and sounds."""
        self.music_muted = not self.music_muted
        try:
            pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.15)
        except Exception:
            pass

    def setup_buttons(self):
        """Initializes menu and overlay buttons with specific callbacks."""
        # Start Menu
        self.menu_buttons = [
            Button(300, 260, 200, 45, "Play", 
                   callback=lambda: self.transition_to_state('PLAYING', self.start_gameplay)),
            Button(300, 320, 200, 45, "Difficulty", 
                   callback=lambda: self.transition_to_state('DIFFICULTY')),
            Button(300, 380, 200, 45, "Instructions", 
                   callback=lambda: self.transition_to_state('INSTRUCTIONS')),
            Button(300, 440, 200, 45, "Exit", 
                   callback=self.quit_game)
        ]

        # Difficulty Selector
        self.difficulty_buttons = {
            'Easy': Button(300, 240, 200, 45, "Easy", 
                           callback=lambda: self.set_difficulty('Easy')),
            'Medium': Button(300, 300, 200, 45, "Medium", 
                             callback=lambda: self.set_difficulty('Medium')),
            'Hard': Button(300, 360, 200, 45, "Hard", 
                           callback=lambda: self.set_difficulty('Hard')),
            'Back': Button(300, 440, 200, 45, "Back", 
                           callback=lambda: self.transition_to_state('MENU'))
        }

        # Instructions screen Back Button
        self.instructions_back_btn = Button(300, 460, 200, 45, "Back", 
                                            callback=lambda: self.transition_to_state('MENU'))

        # Game Over Screen Buttons
        self.gameover_buttons = [
            Button(190, 400, 200, 45, "Play Again", 
                   callback=lambda: self.transition_to_state('PLAYING', self.start_gameplay)),
            Button(410, 400, 200, 45, "Main Menu", 
                   callback=lambda: self.transition_to_state('MENU'))
        ]

    def set_difficulty(self, diff):
        """Sets selected difficulty level."""
        self.difficulty = diff

    def transition_to_state(self, target_state, action_callback=None):
        """Triggers a black-fade transition before executing the state change."""
        def peak_fade():
            self.state = target_state
            if action_callback:
                action_callback()
            self.transition.fade_in()
            
        self.transition.fade_to(peak_fade)

    def start_gameplay(self):
        """Resets variables and spawns elements to start a new match."""
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.score = 0
        self.speed_level = 1
        self.particles.clear()
        self.last_move_time = pygame.time.get_ticks()
        
        # Stop gameover noises and resume clean loops
        try:
            if self.sound_gameover:
                self.sound_gameover.stop()
        except Exception:
            pass
        self.play_music()
        
        self.countdown.start()
        self.state = 'COUNTDOWN'

    def handle_game_over(self):
        """Triggered when snake crashes. Evaluates high score and plays audio."""
        self.state = 'GAME_OVER'
        
        # Check highscore
        current_hs = self.high_scores[self.difficulty]
        if self.score > current_hs:
            self.high_scores[self.difficulty] = self.score
            self.save_high_score()

        # Stop music and play game over crash
        try:
            pygame.mixer.music.stop()
            if self.sound_gameover and not self.music_muted:
                self.sound_gameover.play()
        except Exception:
            pass

    def quit_game(self):
        """Safely shuts down pygame and exits the program."""
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Processes OS inputs and updates menu UI click focus."""
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()

        # Update button hover positions
        if not self.transition.active:
            if self.state == 'MENU':
                for btn in self.menu_buttons:
                    btn.update(mouse_pos)
            elif self.state == 'DIFFICULTY':
                for btn in self.difficulty_buttons.values():
                    btn.update(mouse_pos)
            elif self.state == 'INSTRUCTIONS':
                self.instructions_back_btn.update(mouse_pos)
            elif self.state == 'GAME_OVER':
                for btn in self.gameover_buttons:
                    btn.update(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()

            # Ignore input changes during transition fades
            if self.transition.active:
                continue

            # Mute toggle is global
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.toggle_mute()

            # 1. State: MENU Keyboard Shortcuts
            if self.state == 'MENU':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.menu_buttons:
                        if btn.check_click(mouse_pos, event):
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_game()
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.transition_to_state('PLAYING', self.start_gameplay)

            # 2. State: DIFFICULTY Selection Click handler
            elif self.state == 'DIFFICULTY':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.difficulty_buttons.values():
                        if btn.check_click(mouse_pos, event):
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.transition_to_state('MENU')

            # 3. State: INSTRUCTIONS Back click
            elif self.state == 'INSTRUCTIONS':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.instructions_back_btn.check_click(mouse_pos, event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.transition_to_state('MENU')

            # 4. State: PLAYING controls
            elif self.state == 'PLAYING':
                self.snake.handle_input(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = 'PAUSED'
                    elif event.key == pygame.K_ESCAPE:
                        self.transition_to_state('MENU', lambda: pygame.mixer.music.stop())

            # 5. State: PAUSED controls
            elif self.state == 'PAUSED':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = 'PLAYING'
                        self.last_move_time = pygame.time.get_ticks()  # prevent sudden jump
                    elif event.key == pygame.K_ESCAPE:
                        self.transition_to_state('MENU', lambda: pygame.mixer.music.stop())

            # 6. State: GAME OVER controls
            elif self.state == 'GAME_OVER':
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in self.gameover_buttons:
                        if btn.check_click(mouse_pos, event):
                            break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.transition_to_state('PLAYING', self.start_gameplay)
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_game()

    def update(self):
        """Updates game state timers, particle animations, and snake grid updates."""
        # 1. Update Transitions
        self.transition.update()

        # 2. Update particle lists globally (updates both during PLAYING and COUNTDOWN/MENU if spawned)
        for p in self.particles[:]:
            p.update()
            if p.life <= 0 or p.size <= 0:
                self.particles.remove(p)

        # 3. Update active game states
        if self.state == 'COUNTDOWN':
            done = self.countdown.update()
            if done:
                self.state = 'PLAYING'
                self.last_move_time = pygame.time.get_ticks()

        elif self.state == 'PLAYING':
            # Dynamic pulse on food
            self.food.update()

            # Dynamic speed levels based on score
            self.speed_level = 1 + (self.score // SPEED_INCREMENT_INTERVAL)
            
            # Calculate actual move interval (milliseconds)
            base_interval = DIFFICULTY_SPEEDS[self.difficulty]
            move_interval = max(
                MIN_TICK_INTERVAL, 
                base_interval - (self.speed_level - 1) * SPEED_INCREMENT_AMOUNT
            )
            
            now = pygame.time.get_ticks()
            if now - self.last_move_time >= move_interval:
                self.last_move_time = now
                
                # Move snake, check collisions
                alive = self.snake.update()
                if not alive:
                    self.handle_game_over()
                    return

                # Check if food is eaten
                if self.snake.body[0] == self.food.position:
                    self.snake.grow()
                    self.score += 1
                    
                    # Play food crunch audio
                    try:
                        if self.sound_food and not self.music_muted:
                            self.sound_food.play()
                    except Exception:
                        pass
                    
                    # Spawn particles burst at food pixel location
                    food_px = self.food.position[0] * GRID_SIZE + GRID_SIZE // 2
                    food_py = self.food.position[1] * GRID_SIZE + GRID_SIZE // 2
                    for _ in range(15):
                        self.particles.append(Particle(food_px, food_py))
                        
                    # Spawn next food in safe location
                    self.food.spawn(self.snake.body)

    def draw(self):
        """Draws current state elements to the Pygame screen buffer."""
        # Clear screen
        self.screen.fill(COLOR_BG)
        
        # Always draw grid in background
        draw_grid(self.screen)

        # Draw states
        if self.state in ('PLAYING', 'COUNTDOWN', 'PAUSED'):
            # Draw game objects
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            
            # Draw particle effects
            for p in self.particles:
                p.draw(self.screen)
                
            # Draw HUD
            draw_header_hud(
                self.screen, self.score, self.high_scores[self.difficulty],
                self.speed_level, self.difficulty, self.music_muted, self.fonts
            )
            
            if self.state == 'PAUSED':
                draw_paused_overlay(self.screen, self.fonts)
            elif self.state == 'COUNTDOWN':
                self.countdown.draw(self.screen, self.fonts)

        elif self.state == 'MENU':
            # Pulsing Title Logo
            draw_title_logo(self.screen, self.fonts, pygame.time.get_ticks())
            
            # Menu buttons
            for btn in self.menu_buttons:
                btn.draw(self.screen, self.fonts)
                
            # Render visual details in menu background (e.g. particles float)
            for p in self.particles:
                p.draw(self.screen)

        elif self.state == 'DIFFICULTY':
            self.screen.fill(COLOR_BG)
            draw_grid(self.screen)
            
            # Title
            t_surf = self.fonts['large'].render("Select Difficulty", True, COLOR_TEXT)
            t_rect = t_surf.get_rect(center=(WINDOW_WIDTH // 2, 160))
            self.screen.blit(t_surf, t_rect)
            
            # Render difficulty buttons
            for name, btn in self.difficulty_buttons.items():
                if name == self.difficulty:
                    # Highlight border / draw selected dot
                    dot_center = (btn.rect.left - 20, btn.rect.centery)
                    pygame.draw.circle(self.screen, COLOR_ACCENT, dot_center, 6)
                    
                    # Highlight outline
                    glow_rect = btn.rect.inflate(6, 6)
                    pygame.draw.rect(self.screen, COLOR_ACCENT, glow_rect, width=1, border_radius=10)
                    
                btn.draw(self.screen, self.fonts)

        elif self.state == 'INSTRUCTIONS':
            self.screen.fill(COLOR_BG)
            draw_grid(self.screen)
            
            t_surf = self.fonts['large'].render("Instructions", True, COLOR_TEXT)
            t_rect = t_surf.get_rect(center=(WINDOW_WIDTH // 2, 100))
            self.screen.blit(t_surf, t_rect)
            
            # Box container
            box_w, box_h = 520, 290
            box_rect = pygame.Rect((WINDOW_WIDTH - box_w) // 2, 150, box_w, box_h)
            pygame.draw.rect(self.screen, COLOR_BUTTON, box_rect, border_radius=12)
            pygame.draw.rect(self.screen, COLOR_BUTTON_BORDER, box_rect, width=2, border_radius=12)
            
            instructions = [
                ("Movement Controls", "WASD or Arrow Keys"),
                ("Pause / Resume", "P"),
                ("Mute / Unmute Music", "M"),
                ("Exit to Menu", "ESC (during gameplay)"),
                ("Quit Application", "ESC (on Game Over / Main Menu)"),
                ("Objective", "Eat the glowing red apples, grow, and avoid"),
                ("", "colliding with the walls or your own body!")
            ]
            
            y = 175
            for label, action in instructions:
                if label:
                    l_surf = self.fonts['medium'].render(label + ":", True, COLOR_ACCENT)
                    self.screen.blit(l_surf, (box_rect.left + 30, y))
                    a_surf = self.fonts['medium'].render(action, True, COLOR_TEXT)
                    self.screen.blit(a_surf, (box_rect.left + 210, y))
                else:
                    a_surf = self.fonts['medium'].render(action, True, COLOR_TEXT)
                    self.screen.blit(a_surf, (box_rect.left + 30, y))
                y += 33
                
            self.instructions_back_btn.draw(self.screen, self.fonts)

        elif self.state == 'GAME_OVER':
            draw_game_over_screen(
                self.screen, self.score, self.high_scores[self.difficulty],
                self.gameover_buttons, self.fonts
            )

        # Transition drawing overlays everything
        self.transition.draw(self.screen)

        # Double-buffer render
        pygame.display.flip()

    def run(self):
        """Runs the main game execution loop capped at the system FPS limit."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    game = GameController()
    game.run()

if __name__ == "__main__":
    main()
