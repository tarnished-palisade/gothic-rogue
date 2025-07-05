# main.py
# The foundational script for the Untitled Gothic Horror Roguelike.
# This initial implementation focuses on creating a robust, doctrine-driven
# main menu system.

import random
import pygame
import sys
from enum import Enum, auto
import json
import os
import math

# ==============================================================================
# I. Settings Manager (Principle: Preservation Axiom)
# ==============================================================================

class SettingsManager:
    """Manages loading and saving game settings to a JSON file."""

    def __init__(self):
        self.filepath = "gothic_rogue_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file, or returns defaults."""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {
            "resolution_index": 0
        }

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value

# ==============================================================================
# II. Configuration and Constants (Principle: Change-Resilient)
# ==============================================================================

settings_manager = SettingsManager()

resolutions = [(800, 600), (1024, 768), (1200, 900), (1600, 1200), (1920, 1080)]
current_resolution_index = settings_manager.get("resolution_index")
SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]

INTERNAL_WIDTH, INTERNAL_HEIGHT = 800, 600

COLOR_NEAR_BLACK = (10, 10, 10)
COLOR_WHITE = (255, 255, 255)
COLOR_BLOOD_RED = (139, 0, 0)

FONT_NAME = 'Consolas'

TILE_SIZE = 16 # Each grid cell will be 16x16 pixels

# ==============================================================================
# III. State Management (Principle: Coherence)
# ==============================================================================

class GameState(Enum):
    QUIT = auto()
    MAIN_MENU = auto()
    OPTIONS_MENU = auto()
    GAME_RUNNING = auto()

# ==============================================================================
# IV. UI Classes (Principle: Modularity)
# ==============================================================================

class Button:
    """Represents a single, selectable button."""

    def __init__(self, y, text, font, action):
        self.rect = pygame.Rect(INTERNAL_WIDTH / 2 - 150, y, 300, 50)
        self.text = text
        self.font = font
        self.action = action
        self.is_selected = False

    def draw(self, surface):
        color = COLOR_BLOOD_RED if self.is_selected else COLOR_WHITE
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Menu:
    """Manages the main menu."""

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 50)
        self.button_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 30)

        self.buttons = [
            Button(250, "Start Game", self.button_font, GameState.GAME_RUNNING),
            Button(310, "Options", self.button_font, GameState.OPTIONS_MENU),
            Button(370, "Quit", self.button_font, GameState.QUIT)
        ]
        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True
        self.title_flicker_timer = 0.0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index].action
        return None

    def update(self, delta_time):
        self.title_flicker_timer += delta_time

    def draw(self, surface):
        flicker = 190 + 65 * math.sin(self.title_flicker_timer * 5)
        title_color = (int(flicker), int(flicker), int(flicker))

        title_text = "Gothic Rogue"
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 150))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

class OptionsMenu:
    """Manages the options screen."""

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 40)
        self.button_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 28)

        self.buttons = []
        for i, (w, h) in enumerate(resolutions):
            action = {"type": "resolution", "index": i}
            button = Button(200 + i * 50, f"{w} x {h}", self.button_font, action)
            self.buttons.append(button)

        self.buttons.append(Button(200 + len(resolutions) * 50, "Back", self.button_font, {"type": "back"}))

        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True

    def update(self, delta_time):
        pass

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.buttons[self.selected_index].is_selected = False
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.buttons[self.selected_index].is_selected = True
            elif event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index].action
        return None

    def draw(self, surface):
        title_surface = self.title_font.render("Screen Resolution", True, COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 100))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

# ==============================================================================
# V. Entity-Component System (ECS) (Principle: Modularity)
# ==============================================================================

class Component:
    """A base class for all components. Does not do anything on its own."""
    def __init__(self):
        pass

class PositionComponent(Component):
    """Stores the grid-based (tile) x, y coordinates of an entity."""
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

class RenderComponent(Component):
    """Stores the visual representation of an entity."""

    def __init__(self, char, color):
        super().__init__()  # Call the parent's __init__ method
        self.char = char
        self.color = color

class Entity:
    """A generic container for components."""

    def __init__(self):
        self.components = {}

    def add_component(self, component):
        self.components[type(component)] = component

    def get_component(self, component_type):
        return self.components.get(component_type)

# ==============================================================================
# VI. Game World (Principle: Scalability)
# Contains classes that manage the game world, map, and level data.
# ==============================================================================

class ProceduralCaveGenerator:
    """Handles the creation of organic cave-like maps using Cellular Automata."""

    @staticmethod
    def _get_neighbor_wall_count(x, y, tiles):
        """Counts the number of wall tiles in the 8 surrounding neighbors."""
        wall_count = 0
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if i < 0 or i >= len(tiles) or j < 0 or j >= len(tiles[0]):

                    # Treat out-of-bounds as a wall to enforce edges
                    wall_count += 1
                elif (i, j) != (y, x) and tiles[i][j] == '#':
                    wall_count += 1
        return wall_count

    @staticmethod
    def _simulation_step(old_tiles):
        """Runs a single step of the Cellular Automata simulation."""
        width, height = len(old_tiles[0]), len(old_tiles)
        new_tiles = [['.' for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                wall_neighbors = ProceduralCaveGenerator._get_neighbor_wall_count(x, y, old_tiles)
                # The core rule: A tile becomes a wall if it has 5 or more wall neighbors.
                if wall_neighbors > 4:
                    new_tiles[y][x] = '#'
                else:
                    new_tiles[y][x] = '.'
        return new_tiles

    @staticmethod
    def generate_map(width, height):
        """Generates a complete cave map."""
        # Step 1: Create initial random noise (45% walls)
        tiles = [['.' for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if random.randint(1, 100) < 45:
                    tiles[y][x] = '#'

        # Step 2: Run the simulation 4 times to smooth out the noise
        for _ in range(4):
            tiles = ProceduralCaveGenerator._simulation_step(tiles)

        # Step 3: Ensure a solid border around the entire map
        for y in range(height):
            tiles[y][0] = '#'
            tiles[y][width - 1] = '#'
        for x in range(width):
            tiles[0][x] = '#'
            tiles[height - 1][x] = '#'

        # Step 4: Add floor texture (rubble)
        # Iterate through the final map and add details to floor tiles.
        for y in range(height):
            for x in range(width):
                if tiles[y][x] == '.':
                    if random.randint(1, 100) <= 5:  # 5% chance to have rubble rocks
                        tiles[y][x] = ','

        return tiles

class Map:
    """
    Manages the game map, including its tiles and rendering.
    - Necessity: To create a persistent world for the player to exist in.
    - Function: Holds a 2D array representing the level's layout.
    - Effect: A visible, static game world is created on screen.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # --- OPTION 1: Original Static Map (Commented Out) ---
        # This was the original, hand-designed map for testing.
        # To use this map, uncomment these lines and comment out OPTION 2.
        #
        # Create a simple map: a floor of '.' surrounded by walls of '#'
        # self.tiles = [['#' for _ in range(width)] for _ in range(height)]
        # for y in range(1, height - 1):
        #    for x in range(1, width - 1):
        #        # 95% chance of being a floor, 5% chance of being rubble
        #        if random.randint(1, 100) > 5:
        #            self.tiles[y][x] = '.' # Floor
        #        else:
        #            self.tiles[y][x] = ',' # Rubble/Debris
        # ---------------------------------------------------------

        # --- OPTION 2: Procedural Generation (Active) ---
        # This uses a generator class to create a new, random map every time.
        # To use the static map instead, comment out these lines.
        self.tiles = ProceduralCaveGenerator.generate_map(self.width, self.height)
        # ---------------------------------------------------------

        self.spawn_point = self.find_spawn_point()

    def find_spawn_point(self):
        """Finds the first available floor tile starting from the center."""
        center_x, center_y = self.width // 2, self.height // 2
        if self.tiles[center_y][center_x] == '.':
            return center_x, center_y

        # Simple spiral search if center is a wall
        for radius in range(1, max(center_x, center_y)):
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    x, y = center_x + j, center_y + i
                    if self.tiles[y][x] == '.':
                        return x, y
        return None # Should not happen on a valid map

    def draw(self, surface, font):
        # Define colors for different tile types
        tile_colors = {
            '#': (100, 100, 100), # Grey walls
            '.': (50, 50, 50),   # Dark grey floor
            ',': (40, 40, 40)    # Darker rubble
        }

        for y, row in enumerate(self.tiles):
            for x, tile_char in enumerate(row):

                # Use the tile character to look up its color
                color = tile_colors.get(tile_char, COLOR_WHITE)
                text_surface = font.render(tile_char, True, color)

                # We draw the map based on TILE_SIZE grid coordinates
                surface.blit(text_surface, (x * TILE_SIZE, y * TILE_SIZE))

class Camera:
    """
    Manages the game's viewport.
    - Necessity: To allow the game world to be larger than the screen,
                 and to control what portion of it is visible.
    - Function: Tracks a target entity (the player) and centers the view on it.
    - Effect: A scrollable view of the game map.
    """
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity_rect):
        """Applies the camera offset to a given rect."""
        return entity_rect.move(self.rect.topleft)

    def update(self, target_entity):
        """Updates the camera's position to center on the target entity."""
        target_pos = target_entity.get_component(PositionComponent)
        if not target_pos: return

        # Convert target's grid position to pixel position
        target_pixel_x = target_pos.x * TILE_SIZE + TILE_SIZE // 2
        target_pixel_y = target_pos.y * TILE_SIZE + TILE_SIZE // 2

        # Center the camera on the target's pixel position
        x = -target_pixel_x + int(INTERNAL_WIDTH / 2)
        y = -target_pixel_y + int(INTERNAL_HEIGHT / 2)

        self.rect = pygame.Rect(x, y, self.width, self.height)

# ==============================================================================
# VII. Main Game Class
# ==============================================================================

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        pygame.display.set_caption("Untitled Gothic Horror Roguelike")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MAIN_MENU

        self.menus = {
            GameState.MAIN_MENU: Menu(),
            GameState.OPTIONS_MENU: OptionsMenu()
        }
        self.game_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 16)

        # Debug Instance
        self.debug_overlay = DebugOverlay()

        # Camera Creation
        self.camera = Camera(INTERNAL_WIDTH, INTERNAL_HEIGHT)

        # Map Creation - Let's make the map bigger to test the camera
        map_width = 100  # New larger width
        map_height = 100  # New larger height
        self.game_map = Map(map_width, map_height)

        # Player Creation
        self.player = Entity()
        spawn_x, spawn_y = self.game_map.spawn_point
        self.player.add_component(PositionComponent(spawn_x, spawn_y))
        self.player.add_component(RenderComponent('@', COLOR_WHITE))

    def run(self):
        while self.game_state != GameState.QUIT:
            delta_time = self.clock.tick(60) / 1000.0

            self.handle_events()
            self.update(delta_time)
            self.draw()

        pygame.quit()
        sys.exit()

    def change_resolution(self, index):
        """Changes the window size and saves the setting."""
        global SCREEN_WIDTH, SCREEN_HEIGHT, current_resolution_index
        current_resolution_index = index
        SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        settings_manager.set("resolution_index", index)
        settings_manager.save_settings()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return

            # Debug Overlay Toggle Key Handler
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.debug_overlay.toggle()

            # Menu Input Handling
            if self.game_state in self.menus:
                action = self.menus[self.game_state].handle_input(event)
                if action:
                    if isinstance(action, GameState):
                        self.game_state = action
                    elif isinstance(action, dict):
                        if action["type"] == "resolution":
                            self.change_resolution(action["index"])
                        elif action["type"] == "back":
                            self.game_state = GameState.MAIN_MENU


            elif self.game_state == GameState.GAME_RUNNING:
                if event.type == pygame.KEYDOWN:
                    pos = self.player.get_component(PositionComponent)
                    if not pos: return

                    # Calculate potential new position
                    next_x, next_y = pos.x, pos.y
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        next_y -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        next_y += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        next_x -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        next_x += 1

                    # --- COLLISION CHECK ---
                    # Check if the target tile is walkable before moving.
                    # The '#' character represents a non-walkable wall.
                    if self.game_map.tiles[next_y][next_x] != '#':
                        pos.x = next_x
                        pos.y = next_y

    def update(self, delta_time):
        if self.game_state in self.menus:
            self.menus[self.game_state].update(delta_time)
        elif self.game_state == GameState.GAME_RUNNING:
            self.camera.update(self.player)

    def draw(self):
        self.internal_surface.fill(COLOR_NEAR_BLACK)

        if self.game_state in self.menus:
            self.menus[self.game_state].draw(self.internal_surface)
            # In Game.draw
        elif self.game_state == GameState.GAME_RUNNING:
            # We now use the camera to offset the drawing of all world objects.

            # Draw the map through the camera
            for y, row in enumerate(self.game_map.tiles):
                for x, tile_char in enumerate(row):
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    visible_rect = self.camera.apply(tile_rect)

                    # Simple culling: only draw if it's on screen
                    if self.internal_surface.get_rect().colliderect(visible_rect):
                        color = COLOR_WHITE
                        text_surface = self.game_font.render(tile_char, True, color)
                        self.internal_surface.blit(text_surface, visible_rect)

            # Render the player through the camera
            pos = self.player.get_component(PositionComponent)
            render = self.player.get_component(RenderComponent)
            if pos and render:
                player_rect = pygame.Rect(pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                visible_rect = self.camera.apply(player_rect)

                text_surface = self.game_font.render(render.char, True, render.color)
                # Center the character within the visible rect
                text_draw_rect = text_surface.get_rect(center=visible_rect.center)
                self.internal_surface.blit(text_surface, text_draw_rect)

        # Draw the debug overlay on top of everything else on the internal surface
        debug_data = {
            "FPS": f"{self.clock.get_fps():.1f}",
            "State": self.game_state.name,
            "Player Pos": f"({self.player.get_component(PositionComponent).x}, {self.player.get_component(PositionComponent).y})"
        }
        self.debug_overlay.draw(self.internal_surface, debug_data)

        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

# ==============================================================================
# VIII. Development Tools
# ==============================================================================

class DebugOverlay:
    """
    A toggleable overlay for displaying real-time development information.
    - Necessity: To provide developers with immediate insight into the game's
                 internal state for performance tuning and debugging.
    - Function: Renders key game data, such as FPS and player coordinates.
    - Effect: A non-intrusive, powerful tool for live diagnostics.
    """
    def __init__(self):
        self.font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 14)
        self.enabled = False # The overlay is off by default

    def toggle(self):
        """Switches the overlay's visibility on or off."""
        self.enabled = not self.enabled

    def draw(self, surface, data):
        """Draws the debug information onto the provided surface."""
        if not self.enabled:
            return

        y_offset = 5
        for key, value in data.items():
            text = f"{key}: {value}"
            text_surface = self.font.render(text, True, (255, 255, 0)) # Yellow text
            surface.blit(text_surface, (5, y_offset))
            y_offset += 15

# ==============================================================================
# IX. Entry Point
# ==============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()