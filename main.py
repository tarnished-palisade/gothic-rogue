# main.py
# The foundational script for the Untitled Gothic Horror Roguelike.

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

# An instance of the SettingsManager to handle loading saved preferences.
settings_manager = SettingsManager()

# --- Display Settings ---
# A list of all available screen resolutions for the player to choose from.
resolutions = [(800, 600), (1024, 768), (1200, 900), (1600, 1200), (1920, 1080)]
# Load the player's previously saved resolution choice.
current_resolution_index = settings_manager.get("resolution_index")
# Set the initial screen dimensions based on the loaded setting.
SCREEN_WIDTH, SCREEN_HEIGHT = resolutions[current_resolution_index]

# The fixed internal resolution. The game is always rendered to this size,
# and then scaled up to the player's chosen screen resolution. This ensures
# visual consistency across all display sizes.
INTERNAL_WIDTH, INTERNAL_HEIGHT = 800, 600

# --- Color Palette ---
# This palette defines all colors used in the game, allowing for easy
# aesthetic changes. Each color's name describes its intended use.

# General UI Colors
COLOR_NEAR_BLACK = (10, 10, 10)  # Used for the main background of menu screens.
COLOR_WHITE = (255, 255, 255)  # Default text color, unselected menu items.
COLOR_BLOOD_RED = (139, 0, 0)  # Highlight color for selected menu items.

# In-Game "Earthen Cave" Palette
COLOR_DARK_BROWN = (110, 80, 50)  # The color of cave walls ('#').
COLOR_MEDIUM_BROWN = (30, 25, 20)  # The color of the cave's background fill.
COLOR_DARK_GREY = (90, 90, 90)  # The color of the floor character ('.').
COLOR_DARKER_BROWN = (80, 70, 60)  # The color of rubble or debris (',').

# --- Font and Tile Settings ---
# The name of the monospaced font to be used for all game text.
# 'Consolas' is chosen for its clarity and classic roguelike feel.
FONT_NAME = 'Consolas'

# The pixel dimension of a single map tile. This value is crucial for
# converting grid-based coordinates (e.g., x=5, y=3) into pixel-based
# screen positions for rendering.
TILE_SIZE = 16

# ==============================================================================
# III. State Management (Principle: Coherence)
# ==============================================================================

class GameState(Enum):
    """
    An enumeration that defines the possible states of the game.
    This governs what logic is currently active, from menus to gameplay.
    """
    QUIT = auto()  # State to signal the application should close.
    MAIN_MENU = auto()  # State for when the main menu is displayed.
    OPTIONS_MENU = auto()  # State for when the options menu is displayed.

    # The original GAME_RUNNING state has been replaced by a more granular
    # turn-based system to provide more precise control over game flow.
    PLAYER_TURN = auto()  # The game is waiting for the player to act.
    ENEMY_TURN = auto()  # The game is processing the actions of all enemies.

# ==============================================================================
# IV. UI Classes (Principle: Modularity)
# ==============================================================================

class Button:
    """Represents a single, selectable button in a UI menu."""

    def __init__(self, y, text, font, action):
        self.rect = pygame.Rect(INTERNAL_WIDTH / 2 - 150, y, 300, 50)
        self.text = text
        self.font = font
        self.action = action  # The GameState or command this button triggers.
        self.is_selected = False

    def draw(self, surface):
        """Draws the button, highlighting it if it is selected."""
        color = COLOR_BLOOD_RED if self.is_selected else COLOR_WHITE
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Menu:
    """Manages the main menu, its title, and its buttons."""

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 50)
        self.button_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 30)

        self.buttons = [
            Button(250, "Start Game", self.button_font, GameState.PLAYER_TURN),
            Button(310, "Options", self.button_font, GameState.OPTIONS_MENU),
            Button(370, "Quit", self.button_font, GameState.QUIT)
        ]
        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True
        self.title_flicker_timer = 0.0

    def handle_input(self, event):
        """Processes keyboard input for menu navigation."""
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
        """Updates the menu's state, such as animations."""
        self.title_flicker_timer += delta_time  # Drive the title flicker effect.

    def draw(self, surface):
        """Draws all elements of the main menu."""
        # Calculate a flickering color for the title using a sine wave.
        flicker = 190 + 65 * math.sin(self.title_flicker_timer * 5)
        title_color = (int(flicker), int(flicker), int(flicker))

        title_text = "Gothic Rogue"
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 150))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

class OptionsMenu:
    """Manages the options screen for changing settings like resolution."""

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
        pass  # No dynamic elements in the options menu yet.

    def handle_input(self, event):
        """Processes keyboard input for menu navigation."""
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
        """Draws all elements of the options menu."""
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
        # This allows a component to know which entity it belongs to.
        # It is set automatically when the component is added to an entity.
        self.owner = None

class PositionComponent(Component):
    """Stores the grid-based (tile) x, y coordinates of an entity."""

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

class RenderComponent(Component):
    """Stores the visual representation (character and color) of an entity."""

    def __init__(self, char, color):
        super().__init__()
        self.char = char
        self.color = color

class TurnTakerComponent(Component):
    """
    A marker component for any entity that should participate in the turn order.
    - Necessity: To distinguish entities that act (player, enemies) from
                 inanimate objects or environmental effects.
    - Function: Acts as a flag for the TurnManager to identify actors.
    - Effect: Allows the TurnManager to build a list of all entities that
              get a turn, ensuring the game processes actions correctly.
    """

    def __init__(self):
        super().__init__()

class AIComponent(Component):
    """
    A placeholder for AI logic. Will eventually handle enemy behavior.
    - Necessity: To give non-player entities a way to decide their actions.
    - Function: Contains the logic for what an entity does on its turn.
    - Effect: Enables enemies to move, attack, or perform other actions,
              bringing the game world to life.
    """

    def take_turn(self, turn_manager):
        """This method is called by the TurnManager for the enemy's turn."""
        # For now, enemies do nothing. This is where their logic will go.
        # The 'turn_manager' parameter gives the AI context about the game world,
        # such as the player's location or the state of the map.
        pass

class Entity:
    """A generic container for components. Represents any object in the game."""

    def __init__(self):
        self.components = {}

    def add_component(self, component):
        """Adds a component to the entity and sets its owner."""
        # This line establishes a crucial link, allowing any component
        # to access its parent entity and, through it, its sibling components.
        component.owner = self
        self.components[type(component)] = component

    def get_component(self, component_type):
        """Retrieves a component of a specific type from the entity."""
        return self.components.get(component_type)

# ==============================================================================
# VI. Game World (Principle: Scalability)
# ==============================================================================

class ProceduralCaveGenerator:
    """Handles the creation of organic cave-like maps using Cellular Automata."""

    @staticmethod
    def _get_neighbor_wall_count(x, y, tiles):
        wall_count = 0
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if i < 0 or i >= len(tiles) or j < 0 or j >= len(tiles[0]):
                    wall_count += 1
                elif (i, j) != (y, x) and tiles[i][j] == '#':
                    wall_count += 1
        return wall_count

    @staticmethod
    def _simulation_step(old_tiles):
        width, height = len(old_tiles[0]), len(old_tiles)
        new_tiles = [['.' for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                wall_neighbors = ProceduralCaveGenerator._get_neighbor_wall_count(x, y, old_tiles)
                if wall_neighbors > 4:
                    new_tiles[y][x] = '#'
                else:
                    new_tiles[y][x] = '.'
        return new_tiles

    @staticmethod
    def generate_map(width, height):
        tiles = [['.' for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if random.randint(1, 100) < 45:
                    tiles[y][x] = '#'
        for _ in range(4):
            tiles = ProceduralCaveGenerator._simulation_step(tiles)
        for y in range(height):
            tiles[y][0] = '#'
            tiles[y][width - 1] = '#'
        for x in range(width):
            tiles[0][x] = '#'
            tiles[height - 1][x] = '#'
        for y in range(height):
            for x in range(width):
                if tiles[y][x] == '.':
                    if random.randint(1, 100) <= 5:
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
        self.tiles = ProceduralCaveGenerator.generate_map(self.width, self.height)
        self.spawn_point = self.find_spawn_point()
        self.tile_colors = {
            '#': COLOR_DARK_BROWN,
            '.': COLOR_DARK_GREY,
            ',': COLOR_DARKER_BROWN
        }

    def find_spawn_point(self):
        """Finds the first available floor tile, searching outwards from the center."""
        center_x, center_y = self.width // 2, self.height // 2
        if self.tiles[center_y][center_x] == '.':
            return center_x, center_y
        # If the center is a wall, this performs a simple square-based spiral search.
        # It checks progressively larger squares around the center point.
        for radius in range(1, max(center_x, center_y)):
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    x, y = center_x + j, center_y + i
                    if 0 <= y < self.height and 0 <= x < self.width and self.tiles[y][x] == '.':
                        return x, y
        return None  # Should not happen on a valid map

    def is_walkable(self, x, y):
        """Checks if a given tile is walkable (i.e., not a wall)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False  # Out of bounds is not walkable
        return self.tiles[y][x] != '#'

class Camera:
    """
    Manages the game's viewport.
    - Necessity: To allow the game world to be larger than the screen.
    - Function: Tracks a target entity (the player) and centers the view on it.
    - Effect: A scrollable view of the game map.
    """

    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity_rect):
        """Applies the camera's offset to a given rect, making it visible."""
        return entity_rect.move(self.rect.topleft)

    def update(self, target_entity):
        """Updates the camera's position to center on the target entity."""
        target_pos = target_entity.get_component(PositionComponent)
        if not target_pos: return
        target_pixel_x = target_pos.x * TILE_SIZE + TILE_SIZE // 2
        target_pixel_y = target_pos.y * TILE_SIZE + TILE_SIZE // 2
        x = -target_pixel_x + int(INTERNAL_WIDTH / 2)
        y = -target_pixel_y + int(INTERNAL_HEIGHT / 2)
        self.rect = pygame.Rect(x, y, self.width, self.height)

# ==============================================================================
# VII. Turn-Based System (Principle: Logical, Modular)
# ==============================================================================

class TurnManager:
    """
    Orchestrates the turn-based logic of the game.
    - Necessity: To enforce the core roguelike rule: the world only moves
                 when the player acts.
    - Function: Manages whose turn it is and processes entity actions.
    - Effect: A structured, tactical gameplay flow.
    """

    def __init__(self, game_map, player, entities):
        self.game_map = game_map
        self.player = player
        self.entities = entities  # A list of all entities in the game.
        # This creates a list of only the entities that can take a turn.
        self.turn_takers = [e for e in entities if e.get_component(TurnTakerComponent)]

    def process_player_turn(self, dx, dy):
        """
        Processes the player's intended action, like moving or attacking.
        Returns True if the action took a turn, False otherwise.
        """
        pos = self.player.get_component(PositionComponent)
        if not pos: return False

        next_x, next_y = pos.x + dx, pos.y + dy

        # --- COLLISION CHECK (Refactored Location) ---
        # The TurnManager asks the map if the destination is valid. This keeps
        # the responsibility of knowing the map's layout within the Map class.
        if self.game_map.is_walkable(next_x, next_y):
            # This is where "bump attack" logic will eventually go. If the tile
            # is not empty but contains an enemy, this would trigger an attack
            # instead of a move.
            pos.x = next_x
            pos.y = next_y
            return True  # Player successfully moved, consuming their turn.

        # If the player bumps into a wall, the action is invalid and does not
        # consume a turn. The player can immediately try another action.
        return False

    def process_enemy_turns(self):
        """Processes turns for all non-player entities."""
        for entity in self.turn_takers:
            if entity is self.player:
                continue  # The player's turn is handled separately.

            ai = entity.get_component(AIComponent)
            if ai:
                # This is where each enemy's AI logic is executed.
                ai.take_turn(self)
        pass

# ==============================================================================
# VIII. Main Game Class
# ==============================================================================

class Game:
    """The main class that orchestrates the entire game."""

    def __init__(self):
        pygame.init()
        # The global key repeat is disabled. We will build a more controlled
        # "fast move" system on top of our turn-based logic, which gives us
        # more precision over the game's speed and responsiveness.
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
        self.debug_overlay = DebugOverlay()
        self.camera = Camera(INTERNAL_WIDTH, INTERNAL_HEIGHT)

        map_width, map_height = 100, 100
        self.game_map = Map(map_width, map_height)

        # --- Entity Creation ---
        self.player = Entity()
        spawn_x, spawn_y = self.game_map.spawn_point
        self.player.add_component(PositionComponent(spawn_x, spawn_y))
        self.player.add_component(RenderComponent('@', COLOR_WHITE))
        self.player.add_component(TurnTakerComponent())  # The player can take turns.

        # This list holds all entities in the game. Enemies will be added here.
        self.entities = [self.player]

        # --- System Initialization ---
        self.turn_manager = TurnManager(self.game_map, self.player, self.entities)

        # --- Fast Movement System Attributes ---
        # Stores the player's current directional intent (e.g., {'dx': 1, 'dy': 0}).
        self.fast_move_intent = {'dx': 0, 'dy': 0}
        # Accumulates delta_time to trigger turns at a fixed interval.
        self.fast_move_timer = 0.0
        # The time in seconds between each fast move turn (e.g., 0.1 = 10 turns/sec).
        self.FAST_MOVE_INTERVAL = 0.1
        # A flag to disable fast movement when enemies are visible.
        self.is_in_combat = False

    def run(self):
        """The main game loop. Continues until the game state is QUIT."""
        while self.game_state != GameState.QUIT:
            # Get the time elapsed since the last frame, in seconds.
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
        """Processes all pending events from Pygame, like input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return

            # --- Input for both Tactical and Fast Movement ---
            # We now capture both key presses and releases to manage intent.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.debug_overlay.toggle()

                # Update fast move intent on key press
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.fast_move_intent['dy'] = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.fast_move_intent['dy'] = 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.fast_move_intent['dx'] = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.fast_move_intent['dx'] = 1

            if event.type == pygame.KEYUP:
                # Clear fast move intent on key release
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and self.fast_move_intent['dy'] == -1:
                    self.fast_move_intent['dy'] = 0
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.fast_move_intent['dy'] == 1:
                    self.fast_move_intent['dy'] = 0
                elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.fast_move_intent['dx'] == -1:
                    self.fast_move_intent['dx'] = 0
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.fast_move_intent['dx'] == 1:
                    self.fast_move_intent['dx'] = 0

            # --- Input Handling by Game State ---
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

            # Tactical, one-press-one-move logic. Only fires on a new key press.
            elif self.game_state == GameState.PLAYER_TURN:
                if event.type == pygame.KEYDOWN:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        dy = -1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        dy = 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        dx = -1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        dx = 1

                    if dx != 0 or dy != 0:
                        if self.turn_manager.process_player_turn(dx, dy):
                            self.game_state = GameState.ENEMY_TURN

    def update(self, delta_time):
        """Updates the game's state. Called once per frame."""
        if self.game_state in self.menus:
            self.menus[self.game_state].update(delta_time)

        # --- Fast Movement Logic ---
        # This block handles the "hold-to-move" quality-of-life feature.
        # It checks if we are not in combat and if the player is holding a key.
        if not self.is_in_combat and self.game_state == GameState.PLAYER_TURN:
            # Check if there is an active intent to move.
            move_intent = (self.fast_move_intent['dx'] != 0 or self.fast_move_intent['dy'] != 0)
            if move_intent:
                self.fast_move_timer += delta_time
                # If enough time has passed, process a turn.
                if self.fast_move_timer >= self.FAST_MOVE_INTERVAL:
                    self.fast_move_timer = 0.0  # Reset timer
                    if self.turn_manager.process_player_turn(self.fast_move_intent['dx'], self.fast_move_intent['dy']):
                        self.game_state = GameState.ENEMY_TURN

        # --- Core Turn-Based Logic ---
        if self.game_state == GameState.ENEMY_TURN:
            self.turn_manager.process_enemy_turns()
            self.game_state = GameState.PLAYER_TURN

    def draw(self):
        """Draws everything to the screen."""
        # The camera update is now the first step of drawing. This ensures
        # it has the absolute final position of the player for the current
        # frame, preventing any visual flicker or lag.
        if self.game_state in [GameState.PLAYER_TURN, GameState.ENEMY_TURN]:
            self.camera.update(self.player)

        self.internal_surface.fill(COLOR_NEAR_BLACK)

        # Draw the active menu if in a menu state.
        if self.game_state in self.menus:
            self.menus[self.game_state].draw(self.internal_surface)

        # Draw the game world if in a gameplay state.
        elif self.game_state in [GameState.PLAYER_TURN, GameState.ENEMY_TURN]:
            # Draw the map's background rectangle, offset by the camera.
            map_bg_rect = pygame.Rect(0, 0, self.game_map.width * TILE_SIZE, self.game_map.height * TILE_SIZE)
            visible_bg_rect = self.camera.apply(map_bg_rect)
            pygame.draw.rect(self.internal_surface, COLOR_MEDIUM_BROWN, visible_bg_rect)

            # Draw the map tiles through the camera.
            for y, row in enumerate(self.game_map.tiles):
                for x, tile_char in enumerate(row):
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    visible_rect = self.camera.apply(tile_rect)
                    # Simple culling: only draw if it's on screen.
                    if self.internal_surface.get_rect().colliderect(visible_rect):
                        color = self.game_map.tile_colors.get(tile_char, COLOR_WHITE)
                        text_surface = self.game_font.render(tile_char, True, color)
                        self.internal_surface.blit(text_surface, visible_rect)

            # Render all entities through the camera.
            for entity in self.entities:
                pos = entity.get_component(PositionComponent)
                render = entity.get_component(RenderComponent)
                if pos and render:
                    entity_rect = pygame.Rect(pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    visible_rect = self.camera.apply(entity_rect)
                    text_surface = self.game_font.render(render.char, True, render.color)
                    text_draw_rect = text_surface.get_rect(center=visible_rect.center)
                    self.internal_surface.blit(text_surface, text_draw_rect)

        # Draw the debug overlay on top of everything else.
        player_pos_comp = self.player.get_component(PositionComponent)
        player_pos_text = f"({player_pos_comp.x}, {player_pos_comp.y})" if player_pos_comp else "N/A"
        debug_data = {
            "FPS": f"{self.clock.get_fps():.1f}",
            "State": self.game_state.name,
            "Player Pos": player_pos_text
        }
        self.debug_overlay.draw(self.internal_surface, debug_data)

        # Scale the internal surface to the final screen size and draw it.
        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

# ==============================================================================
# IX. Development Tools
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
        self.enabled = False

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
            text_surface = self.font.render(text, True, (255, 255, 0))
            surface.blit(text_surface, (5, y_offset))
            y_offset += 15

# ==============================================================================
# X. Entry Point
# ==============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
