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
COLOR_ENTITY_WHITE = (255, 255, 255)  # A general color for entities like the player and rats.

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
    PLAYER_DEAD = auto()  # A new state for when the player has died.

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
    Handles all logic for non-player entities, from movement to combat.
    - Necessity: To give enemies autonomy and make the world interactive.
    - Function: Contains a state machine (IDLE/ACTIVE) and logic for each state.
    - Effect: Creates dynamic, responsive enemies that can hunt the player.
    """

    def __init__(self, sight_radius=8):
        super().__init__()
        self.state = 'IDLE'
        self.sight_radius = sight_radius
        self.turns_since_player_seen = 0

    def take_turn(self, turn_manager, player):
        """Called by the TurnManager for the enemy's turn. Contains all AI logic."""
        # Get this entity's position and the player's position.
        pos = self.owner.get_component(PositionComponent)
        player_pos = player.get_component(PositionComponent)
        if not pos or not player_pos: return

        # --- State Transition Logic ---
        # Calculate distance to player (Manhattan distance is fast and good for grids).
        distance_to_player = abs(pos.x - player_pos.x) + abs(pos.y - player_pos.y)

        if distance_to_player <= self.sight_radius:
            self.state = 'ACTIVE'
            self.turns_since_player_seen = 0
        else:
            self.turns_since_player_seen += 1
            # If player is unseen for 5 turns, go back to idle.
            if self.turns_since_player_seen >= 5:
                self.state = 'IDLE'

        # --- Action Logic based on State ---
        if self.state == 'ACTIVE':
            # 5% chance to do nothing, adding variety to behavior.
            if random.randint(1, 100) <= 5:
                return  # Skip turn.

            # If adjacent to the player, attack.
            if distance_to_player <= 1:
                turn_manager.process_attack(self.owner, player)
            # Otherwise, move towards the player.
            else:
                self.move_towards(player_pos, turn_manager)

        elif self.state == 'IDLE':
            # Perform a simple random walk.
            self.move_randomly(turn_manager)

    def move_towards(self, target_pos, turn_manager):
        """Moves the entity one step closer to the target position."""
        pos = self.owner.get_component(PositionComponent)
        dx = target_pos.x - pos.x
        dy = target_pos.y - pos.y

        # Normalize the direction vector to get a single step.
        if dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1

        # Check if the intended move is valid before committing.
        next_x, next_y = pos.x + dx, pos.y + dy
        if turn_manager.game_map.is_walkable(next_x, next_y) and not turn_manager.get_entity_at_location(next_x,
                                                                                                         next_y):
            pos.x = next_x
            pos.y = next_y

    def move_randomly(self, turn_manager):
        """Moves the entity one step in a random valid direction."""
        pos = self.owner.get_component(PositionComponent)
        move_options = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        dx, dy = random.choice(move_options)
        next_x, next_y = pos.x + dx, pos.y + dy
        if turn_manager.game_map.is_walkable(next_x, next_y) and not turn_manager.get_entity_at_location(next_x,
                                                                                                         next_y):
            pos.x = next_x
            pos.y = next_y

class StatsComponent(Component):
    """
    Holds the core combat and descriptive stats for an entity.
    - Necessity: To give entities attributes like health and power, which
                 are essential for any combat or interaction system.
    - Function: Stores numerical values for an entity's capabilities.
    - Effect: Allows the game to quantify an entity's resilience and strength,
              forming the basis for combat calculations.
    """

    def __init__(self, hp, power, speed):
        super().__init__()
        self.max_hp = hp
        self.current_hp = hp
        self.power = power
        self.speed = speed

class Entity:
    """A generic container for components. Represents any object in the game."""

    def __init__(self):
        self.components = {}

    def add_component(self, component):
        """Adds a component to the entity and sets its owner."""
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
        for radius in range(1, max(center_x, center_y)):
            for i in range(-radius, radius + 1):
                for j in range(-radius, radius + 1):
                    x, y = center_x + j, center_y + i
                    if 0 <= y < self.height and 0 <= x < self.width and self.tiles[y][x] == '.':
                        return x, y
        return None

    def is_walkable(self, x, y):
        """Checks if a given tile is walkable (i.e., not a wall)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
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
    Orchestrates the turn-based logic of the game, including combat.
    - Necessity: To enforce the core roguelike rule: the world only moves
                 when the player acts, and to resolve interactions.
    - Function: Manages whose turn it is and processes entity actions.
    - Effect: A structured, tactical gameplay flow.
    """

    def __init__(self, game_object):
        """
        Initializes the TurnManager.
        - game_object: A reference back to the main Game instance.
        """
        self.game = game_object  # Store the reference
        self.game_map = game_object.game_map
        self.player = game_object.player
        self.entities = game_object.entities
        # This creates a list of only the entities that can take a turn.
        self.turn_takers = [e for e in self.entities if e.get_component(TurnTakerComponent)]

    def get_entity_at_location(self, x, y):
        """Checks for and returns an entity at a given location."""
        for entity in self.entities:
            pos = entity.get_component(PositionComponent)
            if pos and pos.x == x and pos.y == y:
                return entity
        return None

    def process_player_turn(self, dx, dy):
        """Processes the player's intended action, like moving or attacking."""
        pos = self.player.get_component(PositionComponent)
        if not pos: return False

        next_x, next_y = pos.x + dx, pos.y + dy

        if not self.game_map.is_walkable(next_x, next_y):
            return False

        target_entity = self.get_entity_at_location(next_x, next_y)
        if target_entity:
            self.process_attack(self.player, target_entity)
            return True

        pos.x = next_x
        pos.y = next_y
        return True

    def process_enemy_turns(self):
        """Processes turns for all non-player entities."""
        # We iterate over a copy of the list, as entities might be removed during their turn.
        for entity in list(self.turn_takers):
            if entity is self.player or entity not in self.entities:
                continue

            ai = entity.get_component(AIComponent)
            if ai:
                ai.take_turn(self, self.player)

    def process_attack(self, attacker, defender):
        """Handles the logic for one entity attacking another."""
        attacker_stats = attacker.get_component(StatsComponent)
        defender_stats = defender.get_component(StatsComponent)

        if not attacker_stats or not defender_stats: return

        damage = attacker_stats.power
        defender_stats.current_hp -= damage

        attacker_char = attacker.get_component(RenderComponent).char
        defender_char = defender.get_component(RenderComponent).char
        print(f"The {attacker_char} strikes the {defender_char} for {damage} damage!")

        # Check if the defender died.
        if defender_stats.current_hp <= 0:
            self.kill_entity(defender)

    def kill_entity(self, entity):
        """Removes a dead entity from the game."""
        char = entity.get_component(RenderComponent).char
        print(f"The {char} is slain!")

        # If the player died, end the game.
        if entity is self.player:
            self.game.game_state = GameState.PLAYER_DEAD
        else:
            # Remove the entity from all tracked lists.
            self.game.entities.remove(entity)
            self.turn_takers.remove(entity)

# ==============================================================================
# VIII. Main Game Class
# ==============================================================================

class Game:
    """The main class that orchestrates the entire game."""

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
        self.death_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 60)
        self.debug_overlay = DebugOverlay()
        self.camera = Camera(INTERNAL_WIDTH, INTERNAL_HEIGHT)

        map_width, map_height = 100, 100
        self.game_map = Map(map_width, map_height)

        # --- Entity Creation ---
        self.player = Entity()
        spawn_x, spawn_y = self.game_map.spawn_point
        self.player.add_component(PositionComponent(spawn_x, spawn_y))
        self.player.add_component(RenderComponent('@', COLOR_ENTITY_WHITE))
        self.player.add_component(TurnTakerComponent())
        self.player.add_component(StatsComponent(hp=30, power=5, speed=1))

        rat = Entity()
        while True:
            rat_x = random.randint(1, map_width - 2)
            rat_y = random.randint(1, map_height - 2)
            if self.game_map.is_walkable(rat_x, rat_y) and (rat_x, rat_y) != (spawn_x, spawn_y):
                rat.add_component(PositionComponent(rat_x, rat_y))
                break

        rat.add_component(RenderComponent('r', COLOR_ENTITY_WHITE))
        rat.add_component(TurnTakerComponent())
        rat.add_component(AIComponent())
        rat.add_component(StatsComponent(hp=2, power=1, speed=1))

        self.entities = [self.player, rat]

        # --- System Initialization ---
        # The TurnManager now gets a reference to the whole Game object for better context.
        self.turn_manager = TurnManager(game_object=self)

        # --- Fast Movement System Attributes ---
        self.fast_move_intent = {'dx': 0, 'dy': 0}
        self.fast_move_timer = 0.0
        self.FAST_MOVE_INTERVAL = 0.1
        self.is_in_combat = False

    def run(self):
        """The main game loop. Continues until the game state is QUIT."""
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
        """Processes all pending events from Pygame, like input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F12:
                    self.debug_overlay.toggle()

                # If the player is dead, any key press quits the game.
                if self.game_state == GameState.PLAYER_DEAD:
                    self.game_state = GameState.QUIT
                    return

                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.fast_move_intent['dy'] = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.fast_move_intent['dy'] = 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.fast_move_intent['dx'] = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.fast_move_intent['dx'] = 1

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_UP or event.key == pygame.K_w) and self.fast_move_intent['dy'] == -1:
                    self.fast_move_intent['dy'] = 0
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.fast_move_intent['dy'] == 1:
                    self.fast_move_intent['dy'] = 0
                elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.fast_move_intent['dx'] == -1:
                    self.fast_move_intent['dx'] = 0
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.fast_move_intent['dx'] == 1:
                    self.fast_move_intent['dx'] = 0

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

        if not self.is_in_combat and self.game_state == GameState.PLAYER_TURN:
            move_intent = (self.fast_move_intent['dx'] != 0 or self.fast_move_intent['dy'] != 0)
            if move_intent:
                self.fast_move_timer += delta_time
                if self.fast_move_timer >= self.FAST_MOVE_INTERVAL:
                    self.fast_move_timer = 0.0
                    if self.turn_manager.process_player_turn(self.fast_move_intent['dx'], self.fast_move_intent['dy']):
                        self.game_state = GameState.ENEMY_TURN

        if self.game_state == GameState.ENEMY_TURN:
            self.turn_manager.process_enemy_turns()
            if self.game_state != GameState.PLAYER_DEAD:
                self.game_state = GameState.PLAYER_TURN

    def draw(self):
        """Draws everything to the screen."""
        if self.game_state in [GameState.PLAYER_TURN, GameState.ENEMY_TURN, GameState.PLAYER_DEAD]:
            self.camera.update(self.player)

        self.internal_surface.fill(COLOR_NEAR_BLACK)

        if self.game_state in self.menus:
            self.menus[self.game_state].draw(self.internal_surface)

        elif self.game_state in [GameState.PLAYER_TURN, GameState.ENEMY_TURN, GameState.PLAYER_DEAD]:
            map_bg_rect = pygame.Rect(0, 0, self.game_map.width * TILE_SIZE, self.game_map.height * TILE_SIZE)
            visible_bg_rect = self.camera.apply(map_bg_rect)
            pygame.draw.rect(self.internal_surface, COLOR_MEDIUM_BROWN, visible_bg_rect)

            for y, row in enumerate(self.game_map.tiles):
                for x, tile_char in enumerate(row):
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    visible_rect = self.camera.apply(tile_rect)
                    if self.internal_surface.get_rect().colliderect(visible_rect):
                        color = self.game_map.tile_colors.get(tile_char, COLOR_WHITE)
                        text_surface = self.game_font.render(tile_char, True, color)
                        self.internal_surface.blit(text_surface, visible_rect)

            for entity in self.entities:
                pos = entity.get_component(PositionComponent)
                render = entity.get_component(RenderComponent)
                if pos and render:
                    entity_rect = pygame.Rect(pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    visible_rect = self.camera.apply(entity_rect)
                    text_surface = self.game_font.render(render.char, True, render.color)
                    text_draw_rect = text_surface.get_rect(center=visible_rect.center)
                    self.internal_surface.blit(text_surface, text_draw_rect)

        if self.game_state == GameState.PLAYER_DEAD:
            death_text = self.death_font.render("YOU DIED", True, COLOR_BLOOD_RED)
            text_rect = death_text.get_rect(center=(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2))
            self.internal_surface.blit(death_text, text_rect)

        player_stats = self.player.get_component(StatsComponent)
        debug_data = {
            "FPS": f"{self.clock.get_fps():.1f}",
            "State": self.game_state.name,
            "Player HP": f"{player_stats.current_hp}/{player_stats.max_hp}" if player_stats else "N/A"
        }
        self.debug_overlay.draw(self.internal_surface, debug_data)

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
