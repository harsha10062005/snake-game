import os

# Window & Grid Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_SIZE = 20

# Calculated grid dimensions
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE   # 40
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE  # 30

# Colors (Modern Dark Palette)
COLOR_BG = (15, 23, 42)          # Slate 900
COLOR_GRID = (30, 41, 59)        # Slate 800
COLOR_TEXT = (241, 245, 249)     # Slate 100
COLOR_TEXT_MUTED = (148, 163, 184) # Slate 400
COLOR_ACCENT = (56, 189, 248)    # Sky 400 (Cyan)

# Snake Colors
COLOR_SNAKE_HEAD = (14, 165, 233)  # Sky 500
COLOR_SNAKE_BODY_START = (2, 132, 199) # Sky 600
COLOR_SNAKE_BODY_END = (125, 211, 252)  # Sky 300

# Food Colors
COLOR_FOOD = (239, 68, 68)       # Red 500
COLOR_FOOD_GLOW = (252, 165, 165) # Red 300

# UI Colors
COLOR_BUTTON = (30, 41, 59)      # Slate 800
COLOR_BUTTON_HOVER = (51, 65, 85) # Slate 700
COLOR_BUTTON_BORDER = (71, 85, 105) # Slate 600

# Particle Colors
PARTICLE_COLORS = [
    (239, 68, 68),   # Red
    (249, 115, 22),  # Orange
    (245, 158, 11),  # Amber
    (253, 224, 71)   # Yellow 300
]

# Difficulty Settings (Movement tick interval in milliseconds)
DIFFICULTY_SPEEDS = {
    "Easy": 140,
    "Medium": 90,
    "Hard": 60
}

# Speed progression: decrease tick interval by this much for every 5 points scored
SPEED_INCREMENT_INTERVAL = 5     # Every 5 points
SPEED_INCREMENT_AMOUNT = 5       # Subtract 5ms (faster)
MIN_TICK_INTERVAL = 35           # Speed floor to prevent game from becoming impossible

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# Sound File Paths
PATH_SOUND_FOOD = os.path.join(SOUNDS_DIR, "food.wav")
PATH_SOUND_GAMEOVER = os.path.join(SOUNDS_DIR, "gameover.wav")
PATH_SOUND_MUSIC = os.path.join(SOUNDS_DIR, "music.wav")
