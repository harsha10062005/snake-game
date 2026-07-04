import pygame
from settings import *

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Resets the snake to starting conditions."""
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        
        # Start with a body of 3 segments in the center of the grid, moving right
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = (1, 0)
        self.direction_queue = []  # Buffers inputs to prevent fast double-key self-collision
        self.grow_pending = False
        self.alive = True

    def handle_input(self, event):
        """Processes keystrokes and queues direction changes."""
        if event.type != pygame.KEYDOWN:
            return
            
        target_dir = None
        if event.key in (pygame.K_UP, pygame.K_w):
            target_dir = (0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            target_dir = (0, 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            target_dir = (-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            target_dir = (1, 0)
            
        if target_dir is not None:
            # We compare the target direction against the last direction in the queue (or current direction)
            ref_dir = self.direction_queue[-1] if self.direction_queue else self.direction
            
            # Prevent reversing directly (180 degree turn)
            # Two directions are opposite if their components add up to 0 (e.g., (1,0) and (-1,0))
            if (target_dir[0] + ref_dir[0] != 0) or (target_dir[1] + ref_dir[1] != 0):
                # Queue the input (allow up to 2 buffered turns in advance)
                if len(self.direction_queue) < 2:
                    self.direction_queue.append(target_dir)

    def update(self):
        """Updates the snake's position. Returns True if alive, False if collided."""
        if not self.alive:
            return False
            
        # Process the next buffered direction change
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)
            
        dx, dy = self.direction
        head_x, head_y = self.body[0]
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            self.alive = False
            return False
            
        # Check self collision
        # If growing, the tail remains, so check all segments. Otherwise, the tail will move, so check all except the tail.
        collision_body = self.body if self.grow_pending else self.body[:-1]
        if new_head in collision_body:
            self.alive = False
            return False
            
        # Insert the new head position
        self.body.insert(0, new_head)
        
        # Handle growth
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()  # Remove tail segment if not growing
            
        return True

    def grow(self):
        """Flags the snake to grow on the next movement update."""
        self.grow_pending = True

    def draw(self, surface):
        """Draws the snake with rounded segments and a smooth gradient from head to tail."""
        for i, segment in enumerate(self.body):
            # Convert grid coordinate to pixel coordinate
            x = segment[0] * GRID_SIZE
            y = segment[1] * GRID_SIZE
            center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
            
            if i == 0:
                # Head: Slightly larger circle
                radius = GRID_SIZE // 2 - 1
                pygame.draw.circle(surface, COLOR_SNAKE_HEAD, center, radius)
                self._draw_eyes(surface, center)
            else:
                # Body: Interpolated color from start to end colors
                t = i / len(self.body)
                color = (
                    int(COLOR_SNAKE_BODY_START[0] + (COLOR_SNAKE_BODY_END[0] - COLOR_SNAKE_BODY_START[0]) * t),
                    int(COLOR_SNAKE_BODY_START[1] + (COLOR_SNAKE_BODY_END[1] - COLOR_SNAKE_BODY_START[1]) * t),
                    int(COLOR_SNAKE_BODY_START[2] + (COLOR_SNAKE_BODY_END[2] - COLOR_SNAKE_BODY_START[2]) * t)
                )
                # Taper the tail slightly for a smooth, organic shape
                radius = max(4, int((GRID_SIZE // 2 - 2) * (1.0 - 0.3 * t)))
                pygame.draw.circle(surface, color, center, radius)

    def _draw_eyes(self, surface, center):
        """Draws cute animated eyes looking in the direction of movement."""
        cx, cy = center
        dx, dy = self.direction
        
        eye_radius = 3
        pupil_radius = 1.5
        
        # Offset eye positions and pupil gaze direction based on movement vector
        if dx == 1:    # Moving Right
            eyes = [(cx + 2, cy - 4), (cx + 2, cy + 4)]
            pupil_offset = (1, 0)
        elif dx == -1:  # Moving Left
            eyes = [(cx - 2, cy - 4), (cx - 2, cy + 4)]
            pupil_offset = (-1, 0)
        elif dy == 1:   # Moving Down
            eyes = [(cx - 4, cy + 2), (cx + 4, cy + 2)]
            pupil_offset = (0, 1)
        else:           # Moving Up (dy == -1)
            eyes = [(cx - 4, cy - 2), (cx + 4, cy - 2)]
            pupil_offset = (0, -1)
            
        for ex, ey in eyes:
            # Draw eye white
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), eye_radius)
            # Draw pupil
            px, py = ex + pupil_offset[0], ey + pupil_offset[1]
            pygame.draw.circle(surface, (0, 0, 0), (px, py), pupil_radius)
