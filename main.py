# main.py
# The foundational script for the Gothic Horror Roguelike.

import random
import pygame
import sys
from enum import Enum, auto
import json
import os
import math
from typing import Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import platformdirs

# ==============================================================================
# Define App-Specific Paths
# ==============================================================================

APP_NAME = "GothicRogue"
APP_AUTHOR = "MichaelBanovac" # Replace with your name or studio name

# This finds the correct user data directory based on the OS
# e.g., AppData\Roaming on Windows, ~/.config on Linux
user_data_dir = Path(platformdirs.user_data_path(appname=APP_NAME, appauthor=APP_AUTHOR))

# Ensure the directory exists before we try to write to it
user_data_dir.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# I. Settings Manager (Principle: Preservation Axiom)
# ==============================================================================

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # noinspection SpellCheckingInspection
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # noinspection PyUnresolvedReferences,PyProtectedMember
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SettingsManager:
    """Manages loading and saving game settings to a JSON file."""

    # Add 'resolutions_list' as an argument
    def __init__(self, resolutions_list):
        self.resolutions = resolutions_list # Store the list internally
        # Build the full, correct path to the settings file
        self.filepath = user_data_dir / "gothic_rogue_settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file, or returns defaults."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    settings = json.load(f)
                    if 'show_fps' not in settings:
                        settings['show_fps'] = False

                    res_index = settings.get("resolution_index", 0)
                    # Use the stored list 'self.resolutions'
                    if not isinstance(res_index, int) or not 0 <= res_index < len(self.resolutions):
                        settings["resolution_index"] = 0
                    return settings
            except (json.JSONDecodeError, FileNotFoundError):
                return {"resolution_index": 0, "show_fps": False}
        return {"resolution_index": 0, "show_fps": False}

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value

# ==============================================================================
# II. Item Functions
# These are standalone functions that define the effects of usable items.
# ==============================================================================

def heal(**kwargs):
    """Heals an entity by a given amount."""
    entity = kwargs.get("entity")
    amount = kwargs.get("amount")

    if not entity or not amount:
        return

    stats = entity.get_component(StatsComponent)
    if stats:
        stats.current_hp += amount
        # Prevent overhealing.
        if stats.current_hp > stats.max_hp:
            stats.current_hp = stats.max_hp

def teleport(**kwargs):
    """Finds a random, valid, unoccupied tile and moves the entity there."""
    entity = kwargs.get("entity")
    game_map = kwargs.get("game_map")
    entities = kwargs.get("entities")

    # Defensive check to ensure all necessary data is present.
    if not entity or not game_map or not entities:
        return

    # 1. Create a list of all possible floor tiles on the map.
    possible_locations = []
    for y, row in enumerate(game_map.tiles):
        for x, tile in enumerate(row):
            if tile != '#':  # Any tile that is not a wall is a potential destination.
                possible_locations.append((x, y))

    # 2. Shuffle the list to ensure the destination is random.
    random.shuffle(possible_locations)

    # 3. Find the first valid, unoccupied tile from the shuffled list.
    for loc in possible_locations:
        x, y = loc
        # Check if any other entity is already at this location.
        if not any(e.get_component(PositionComponent).x == x and e.get_component(PositionComponent).y == y for e in entities if e is not entity):
            # Found a safe spot. Move the entity.
            pos = entity.get_component(PositionComponent)
            if pos:
                pos.x = x
                pos.y = y
            return  # Exit the function after successfully teleporting.

# ==============================================================================
# III. Configuration and Constants (Principle: Adaptable)
# ==============================================================================

# --- Display Settings ---
# A list of all available screen resolutions for the player to choose from.
resolutions = [(800, 600), (1024, 768), (1280, 960), (1600, 1200), (2048, 1536)]

# Move the creation of settings_manager here and pass 'resolutions' to it
settings_manager = SettingsManager(resolutions)

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

# --- Enemy Color Palette ---
COLOR_CORPSE_PALE = (170, 180, 150) # A sickly green for ghouls.
COLOR_BONE_WHITE = (220, 220, 200) # An off-white for skeletons.

# --- HUD Color Palette ---
COLOR_HEALTH_GREEN = (0, 255, 0) # Safe health
COLOR_HEALTH_YELLOW = (255, 255, 0) # Caution health
COLOR_HEALTH_ORANGE = (255, 165, 0) # Danger health
COLOR_HEALTH_RED = (255, 0, 0) # Critical health
COLOR_HUD_EMPTY_DASH = (50, 50, 50) # Color for depleted health dashes

# --- HUD Configuration ---
HUD_HEALTH_BAR_DASHES = 20 # The total number of dashes in the health bar

# --- Item Colors ---
COLOR_HEALING_RED = (255, 0, 100) # A vibrant red for potions.
COLOR_SCROLL_BLUE = (100, 100, 255) # A magical blue for scrolls.

# --- Message Log Configuration ---
HUD_MESSAGE_COUNT = 5 # The maximum number of messages to display at once.
# Add some default colors for different message types for future use.
COLOR_MESSAGE_DEFAULT = (255, 255, 255) # White for standard messages.
COLOR_MESSAGE_DAMAGE = (255, 100, 100) # Light red for damage messages.
COLOR_MESSAGE_HEAL = (100, 255, 100)   # Light green for healing messages.

# --- XP & Leveling ---
COLOR_XP_BLUE = (100, 150, 255) # A vibrant blue for the experience bar.
BASE_XP_TO_LEVEL = 100 # XP needed for the first level up.
LEVEL_UP_FACTOR = 1.5  # The scaling exponent for leveling.

# --- Font and Tile Settings ---
# The name of the monospaced font to be used for all game text.
# 'Consolas' is chosen for its clarity and classic roguelike feel.
FONT_NAME = 'Consolas'
FONT_PATH = resource_path('assets/Consolas.ttf') # Location of Consolas .ttf file

# The pixel dimension of a single map tile. This value is crucial for
# converting grid-based coordinates (e.g., x=5, y=3) into pixel-based
# screen positions for rendering.
TILE_SIZE = 16

# --- Game Parameters ---
# This section centralizes all tunable gameplay values.
MAP_WIDTH, MAP_HEIGHT = 100, 100
STAIRS_MIN_DISTANCE_FROM_SPAWN = 20

# --- AI Tuning ---
AI_SIGHT_RADIUS = 8
AI_FORGET_PLAYER_TURNS = 5  # Turns until an ACTIVE AI returns to IDLE
AI_IDLE_ACTION_CHANCE = 5   # Percentage chance for an IDLE AI to do nothing

# --- Procedural Generation Tuning ---
PROCGEN_INITIAL_WALL_CHANCE = 45  # Percentage
PROCGEN_SIMULATION_STEPS = 4
PROCGEN_RUBBLE_CHANCE = 5         # Percentage

# --- Boss Configuration ---
VAMPIRE_LEVEL = 10 # The dungeon level where the Vampire Lord appears.
VAMPIRE_SPAWN_OFFSET_Y = 10 # How far below the center the player spawns

# --- UI Layout & Animation ---
# Centralizes constants for positioning and animating UI elements.
TITLE_Y_POS = 150
TITLE_FLICKER_BASE = 190
TITLE_FLICKER_AMP = 65
TITLE_FLICKER_SPEED = 5

MENU_BUTTON_START_Y = 250
MENU_BUTTON_SPACING = 60

OPTIONS_BUTTON_START_Y = 200

HELP_MENU_MARGIN = 40
HELP_MENU_LINE_SPACING = 20
HELP_MENU_WOBBLE_SPEED = 4
HELP_MENU_WOBBLE_HEIGHT = 3

DIALOGUE_PANEL_HEIGHT = 100
DIALOGUE_PANEL_MARGIN_X = 50
DIALOGUE_PANEL_MARGIN_Y = 30

DEATH_FADE_SPEED = 85
DEATH_TEXT_FADE_THRESHOLD = 200 # Alpha value at which death text appears

# --- Entity Data Definitions ---
# Centralizes the base stats and properties for all non-player entities.
# This makes balancing easier and moves data out of the game logic functions.
ENTITY_DATA = {
    "rat": {
        "char": "r", "color": COLOR_ENTITY_WHITE,
        "stats": {"hp": 5, "power": 2, "defense": 0, "speed": 1, "xp_reward": 40} # Changed from 5
    },
    "ghoul": {
        "char": "g", "color": COLOR_CORPSE_PALE,
        "stats": {"hp": 12, "power": 4, "defense": 1, "speed": 1, "xp_reward": 80} # Changed from 20
    },
    "skeleton": {
        "char": "s", "color": COLOR_BONE_WHITE,
        "stats": {"hp": 8, "power": 3, "defense": 2, "speed": 2, "xp_reward": 100} # Changed from 15
    },
    "vampire_lord": {
        "char": "V", "color": COLOR_BLOOD_RED,
        "stats": {"hp": 100, "power": 10, "defense": 5, "speed": 1, "xp_reward": 1000}
    }
}

# --- Item Data Definitions ---
ITEM_DATA = {
    "health_potion": {
        "spawn_key": "potion", # ADD THIS
        "char": "!", "color": COLOR_HEALING_RED, "name": "Health Potion",
        "use_function": heal, "kwargs": {"amount": 15}
    },
    "teleport_scroll": {
        "spawn_key": "scroll", # ADD THIS
        "char": "?", "color": COLOR_SCROLL_BLUE, "name": "Scroll of Teleportation",
        "use_function": teleport
    },
    "rusty_dagger": {
        "spawn_key": "dagger", # ADD THIS
        "char": ")", "color": (139, 137, 137), "name": "Rusty Dagger",
        "equip": {"slot": "weapon", "power_bonus": 2}
    },
    "leather_armor": {
        "spawn_key": "armor", # ADD THIS
        "char": "[", "color": (139, 69, 19), "name": "Leather Armor",
        "equip": {"slot": "armor", "defense_bonus": 1}
    }
}

# --- Spawn Rate Definitions ---
# Defines the base number and per-level scaling factor for entity spawns.
SPAWN_RATES = {
    "rat":      {"base": 5,  "scaling": 1},      # Changed from base:10, scaling:2
    "ghoul":    {"base": 2,  "scaling": 0.8},    # Changed from base:3, scaling:1
    "skeleton": {"base": 1,  "scaling": 0.6},    # Changed from base:4, scaling:0.5
    "potion":   {"base": 4,  "scaling": -0.5, "min": 1},
    "scroll":   {"base": 0,  "scaling": 0.5},
    "dagger":   {"base": 1,  "scaling": 0},
    "armor":    {"base": 1,  "scaling": 0}
}

# ==============================================================================
# IV. State Management (Principle: Coherence)
# ==============================================================================

class GameState(Enum):
    """
    An enumeration that defines the possible states of the game.
    This governs what logic is currently active, from menus to gameplay.
    """
    QUIT = auto()  # State to signal the application should close.
    MAIN_MENU = auto()  # State for when the main menu is displayed.
    OPTIONS_ROOT = auto()  # The main options menu (with categories).
    OPTIONS_VIDEO = auto()  # The sub-menu for screen resolution settings.
    PLAYER_DEAD = auto()  # A new state for when the player has died.
    EQUIP_MENU = auto() # The new state for the equipment screen.
    DIALOGUE = auto()  # A new state for displaying dialogue.
    VICTORY = auto()  # A new state for when the game is won.

    # The original GAME_RUNNING state has been replaced by a more granular
    # turn-based system to provide more precise control over game flow.
    PLAYER_TURN = auto()  # The game is waiting for the player to act.
    ENEMY_TURN = auto()  # The game is processing the actions of all enemies.

# ==============================================================================
# V. UI Classes (Principle: Modularity)
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
        self.title_font = pygame.font.Font(FONT_PATH, 50)
        self.button_font = pygame.font.Font(FONT_PATH, 30)

        self.buttons = [
            Button(MENU_BUTTON_START_Y, "Start Game", self.button_font, GameState.PLAYER_TURN),
            Button(MENU_BUTTON_START_Y + MENU_BUTTON_SPACING, "Options", self.button_font, GameState.OPTIONS_ROOT),
            Button(MENU_BUTTON_START_Y + (MENU_BUTTON_SPACING * 2), "Quit", self.button_font, GameState.QUIT)
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
        flicker = TITLE_FLICKER_BASE + TITLE_FLICKER_AMP * math.sin(self.title_flicker_timer * TITLE_FLICKER_SPEED)
        title_color = (int(flicker), int(flicker), int(flicker))

        title_text = "Gothic Rogue"
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, TITLE_Y_POS))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

class OptionsMenu:
    """
    Manages all options screens, acting as a state-driven UI system.
    - Necessity: To provide an organized, nested structure for game settings
                 instead of a single, cluttered list.
    - Function: Displays different buttons and titles based on the current
                game state (e.g., OPTIONS_ROOT vs. OPTIONS_VIDEO).
    - Effect: A clean, intuitive, and scalable multiscreen options menu.
    """

    def __init__(self):
        self.title_font = pygame.font.Font(FONT_PATH, 40)
        self.button_font = pygame.font.Font(FONT_PATH, 28)
        self.buttons = []
        self.selected_index = 0

    def rebuild_buttons(self, game_state: GameState):
        """Clears and rebuilds the button list based on the current game state."""
        self.buttons.clear()
        y_offset = OPTIONS_BUTTON_START_Y  # Starting Y position for buttons

        if game_state == GameState.OPTIONS_ROOT:
            # --- Main Options Categories ---
            self.buttons.append(Button(y_offset, "Video Settings", self.button_font, GameState.OPTIONS_VIDEO))

            # This is the FPS toggle from our previous work.
            show_fps = settings_manager.get("show_fps")
            fps_text = f"FPS Counter: {'ON' if show_fps else 'OFF'}"
            self.buttons.append(Button(y_offset + 60, fps_text, self.button_font, {"type": "toggle_fps"}))

            # The back button now returns to the main menu.
            self.buttons.append(Button(y_offset + 120, "Back", self.button_font, GameState.MAIN_MENU))

        elif game_state == GameState.OPTIONS_VIDEO:

            # --- Video Settings Sub-Menu ---
            for i, (w, h) in enumerate(resolutions):
                action = {"type": "resolution", "index": i}
                button_text = f"{w} x {h}"
                # Add an indicator to the currently selected resolution.
                if i == current_resolution_index:
                    button_text += " <"
                button = Button(y_offset + i * 50, button_text, self.button_font, action)
                self.buttons.append(button)

            # The back button now returns to the root options menu.
            back_y = y_offset + len(resolutions) * 50
            self.buttons.append(Button(back_y, "Back", self.button_font, GameState.OPTIONS_ROOT))

        else:
            # This menu does not handle other states. By adding this `else`,
            # we explicitly tell the linter we have considered all other
            # possibilities from the GameState enum.
            pass

        self.selected_index = 0
        self.buttons[self.selected_index].is_selected = True

    def handle_input(self, event):
        """Processes keyboard input for menu navigation and actions."""
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

    def draw(self, surface, game_state):
        """Draws the options menu, with a title that changes based on the state."""
        # --- Dynamic Title ---
        title_text = "Options"
        if game_state == GameState.OPTIONS_VIDEO:
            title_text = "Screen Resolution"

        title_surface = self.title_font.render(title_text, True, COLOR_WHITE)
        title_rect = title_surface.get_rect(center=(INTERNAL_WIDTH / 2, 100))
        surface.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(surface)

class EquipmentMenu:
    # noinspection SpellCheckingInspection
    """
        Manages the UI for viewing and equipping items.
        - Necessity: To provide the player with a dedicated interface for managing
                     their character's gear, a core RPG activity.
        - Function: Displays current stats, equipped items, and equippable items
                    in the inventory, and handles the logic of equipping an item.
        - Effect: A functional, interactive menu that allows players to make
                  strategic decisions about their loadout.
        """

    def __init__(self):
        self.title_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 32)
        self.header_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 20)
        self.item_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 18)
        self.options = []
        self.selected_index = 0

    def rebuild_options(self, player):
        """Clears and rebuilds the list of selectable items from the player's inventory."""
        self.options.clear()
        inventory = player.get_component(InventoryComponent)
        # noinspection SpellCheckingInspection
        if inventory:
            # Filter the inventory to only include items that have an EquippableComponent.
            self.options = [item for item in inventory.items if item.get_component(EquippableComponent)]

        # Ensure selected_index is valid.
        if self.selected_index >= len(self.options):
            self.selected_index = len(self.options) - 1
        if self.selected_index < 0:
            self.selected_index = 0

    def handle_input(self, event):
        """Processes keyboard input for menu navigation and actions."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.options) if self.options else 0
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.options) if self.options else 0
            elif event.key == pygame.K_RETURN and self.options:
                # Return the selected item entity to be equipped.
                return {"type": "equip", "item": self.options[self.selected_index]}
            elif event.key == pygame.K_ESCAPE:
                # Return an action to close the menu.
                return {"type": "close"}
        return None

    # noinspection SpellCheckingInspection
    def draw(self, surface, player):
        """Draws all elements of the equipment menu."""
        # --- Draw Background Panel ---
        panel_rect = pygame.Rect(50, 50, INTERNAL_WIDTH - 100, INTERNAL_HEIGHT - 100)
        pygame.draw.rect(surface, (20, 20, 30), panel_rect)  # Dark blue panel
        pygame.draw.rect(surface, (100, 100, 120), panel_rect, 2)  # Lighter border

        # --- Draw Title ---
        title_surface = self.title_font.render("Character Inventory", True, COLOR_WHITE)
        surface.blit(title_surface, (panel_rect.x + 20, panel_rect.y + 15))

        # --- Draw Player Stats ---
        stats_x = panel_rect.x + 30
        stats_y = panel_rect.y + 80

        # Use the new getter methods to display final, calculated stats.
        stats_text = [
            f"Level: {player.get_component(ExperienceComponent).level}",
            f"Health: {player.get_component(StatsComponent).current_hp} / {player.get_max_hp()}",
            f"Power: {player.get_power()}",
            f"Defense: {player.get_defense()}"
        ]
        for i, text in enumerate(stats_text):
            text_surface = self.item_font.render(text, True, COLOR_WHITE)
            surface.blit(text_surface, (stats_x, stats_y + i * 25))

        # --- Draw Currently Equipped Items ---
        equipped_x = panel_rect.x + 250
        equipped_y = panel_rect.y + 80

        header_surface = self.header_font.render("Equipped", True, COLOR_WHITE)
        surface.blit(header_surface, (equipped_x, equipped_y))

        equipment = player.get_component(EquipmentComponent)
        for i, (slot, item) in enumerate(equipment.slots.items()):
            item_name = item.get_component(ItemComponent).name if item else "None"
            text = f"{slot.capitalize()}: {item_name}"
            text_surface = self.item_font.render(text, True, (200, 200, 200))
            surface.blit(text_surface, (equipped_x + 10, equipped_y + 35 + i * 25))

        # --- Draw Equippable Items in Inventory ---
        inventory_x = panel_rect.x + 30
        inventory_y = panel_rect.y + 250

        inv_header = self.header_font.render("Inventory (Equippable)", True, COLOR_WHITE)
        surface.blit(inv_header, (inventory_x, inventory_y))

        for i, item in enumerate(self.options):
            item_name = item.get_component(ItemComponent).name
            color = COLOR_BLOOD_RED if i == self.selected_index else COLOR_WHITE
            text_surface = self.item_font.render(item_name, True, color)
            surface.blit(text_surface, (inventory_x + 10, inventory_y + 35 + i * 25))

class HelpMenu:
    """
    Manages a toggleable, in-game help screen displaying keybindings.
    - Necessity: To provide players with a non-intrusive, easily accessible
                 reference for game controls, improving user experience.
    - Function: Toggles a list of controls on/off and manages a subtle
                animation for its icon.
    - Effect: A clean, decoupled UI element for player assistance that can
              be accessed at any time during gameplay.
    """

    def __init__(self):
        self.font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 16)
        self.is_open = False
        self.has_been_opened_once = False
        self.animation_timer = 0.0
        # This list contains the text for the help menu.
        self.keybindings = [
            "[ Gameplay ]",
            "Move / Attack: WASD or Arrows",
            "Descend Stairs: > (Shift + .)",
            "",  # Spacer
            "[ Actions ]",
            "Use Health Potion: H",
            "Read Scroll: R",
            "",  # Spacer
            "[ Menus ]",
            "Equipment / Inventory: E",
            "Advance Dialogue: ENTER", # Add the new keybinding here
            "Close Any Menu: ESC",
            "",  # Spacer
            "[ System ]",
            "Toggle Debug Info: F12",
        ]

    def toggle(self):
        """Switches the menu between its open and closed states."""
        self.is_open = not self.is_open
        # Once opened for the first time, disable the introductory animation.
        if not self.has_been_opened_once:
            self.has_been_opened_once = True

    def update(self, delta_time):
        """Updates the animation timer."""
        self.animation_timer += delta_time * HELP_MENU_WOBBLE_SPEED

    def draw(self, surface):
        """Draws the help menu icon or the full list of keybindings."""
        if self.is_open:
            # --- Draw the full help text ---
            # Add the instruction to close the menu to the list dynamically.
            full_text_list = self.keybindings + ["", "Close This Menu: i"]

            for i, text in enumerate(reversed(full_text_list)):
                text_surface = self.font.render(text, True, COLOR_WHITE)
                x_pos = INTERNAL_WIDTH - text_surface.get_width() - HELP_MENU_MARGIN
                # Draw from the bottom up.
                y_pos = INTERNAL_HEIGHT - text_surface.get_height() - HELP_MENU_MARGIN - (i * HELP_MENU_LINE_SPACING)
                surface.blit(text_surface, (x_pos, y_pos))
        else:
            # --- Draw the 'i' icon ---
            y_offset = 0
            # Only apply the wobble animation if the menu has never been opened.
            if not self.has_been_opened_once:
                y_offset = int(math.sin(self.animation_timer) * HELP_MENU_WOBBLE_HEIGHT)

            text_surface = self.font.render("[i]", True, COLOR_WHITE)
            x_pos = INTERNAL_WIDTH - text_surface.get_width() - HELP_MENU_MARGIN
            y_pos = INTERNAL_HEIGHT - text_surface.get_height() - HELP_MENU_MARGIN + y_offset
            surface.blit(text_surface, (x_pos, y_pos))

class DialogueViewer:
    """
    Manages the UI for displaying a dialogue sequence.
    - Necessity: To provide a clean, focused interface for narrative events,
                 pausing the game to deliver story or character moments.
    - Function: Renders a dialogue box and text, advancing line-by-line
                based on player input.
    - Effect: A reusable, decoupled UI system for cinematic storytelling.
    """

    def __init__(self):
        self.font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 18)
        self.speaker_font = pygame.font.Font(pygame.font.match_font(FONT_NAME), 16)
        self.active_entity = None
        self.current_line_index = 0
        self.dialogue_lines = []
        self.speaker_name = ""

    def start_dialogue(self, entity):
        """Prepares the viewer for a new dialogue sequence."""
        dialogue_comp = entity.get_component(DialogueComponent)
        if not dialogue_comp:
            return False  # Cannot start dialogue if the entity has none.

        self.active_entity = entity
        self.current_line_index = 0
        self.speaker_name = dialogue_comp.speaker_name

        # Use subsequent dialogue if the player has already spoken to this entity.
        if dialogue_comp.has_spoken:
            self.dialogue_lines = dialogue_comp.subsequent_dialogue_lines
        else:
            self.dialogue_lines = dialogue_comp.dialogue_lines

        return True

    def handle_input(self, event):
        """Listens only for the Enter key to advance or close the dialogue."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.current_line_index += 1
            # Check if we have run out of dialogue lines.
            if self.current_line_index >= len(self.dialogue_lines):
                # Mark the dialogue as finished and signal to close.
                dialogue_comp = self.active_entity.get_component(DialogueComponent)
                dialogue_comp.has_spoken = True
                return "finished"
        return None

    def draw(self, surface):
        """Draws the dialogue box and the current line of text."""
        if not self.active_entity:
            return

        # --- Draw Background Panel ---
        panel_width = INTERNAL_WIDTH - (DIALOGUE_PANEL_MARGIN_X * 2)
        panel_x = DIALOGUE_PANEL_MARGIN_X
        panel_y = INTERNAL_HEIGHT - DIALOGUE_PANEL_HEIGHT - DIALOGUE_PANEL_MARGIN_Y

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, DIALOGUE_PANEL_HEIGHT)

        # Create a semi-transparent surface for the panel
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill((10, 10, 20, 200))  # Dark blue with 200/255 alpha
        surface.blit(panel_surface, panel_rect.topleft)
        pygame.draw.rect(surface, (100, 100, 120), panel_rect, 2)  # Lighter border

        # --- Draw Speaker Name ---
        speaker_surface = self.speaker_font.render(f"{self.speaker_name}:", True, (200, 180, 100))
        surface.blit(speaker_surface, (panel_rect.x + 15, panel_rect.y + 10))

        # --- Draw Current Dialogue Line ---
        current_line = self.dialogue_lines[self.current_line_index]
        text_surface = self.font.render(current_line, True, COLOR_WHITE)
        surface.blit(text_surface, (panel_rect.x + 20, panel_rect.y + 45))

# ==============================================================================
# VI. Entity-Component System (ECS) (Principle: Modularity)
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

    def __init__(self, sight_radius=AI_SIGHT_RADIUS, is_stationary=False):
        super().__init__()
        self.state = 'IDLE'
        self.sight_radius = sight_radius
        self.is_stationary = is_stationary
        self.turns_since_player_seen = 0

    def take_turn(self, turn_manager, player):
        """Called by the TurnManager for the enemy's turn. Contains all AI logic."""
        # Get entity and player positions at the start. This ensures they are always defined.
        pos = self.owner.get_component(PositionComponent)
        player_pos = player.get_component(PositionComponent)
        if not pos or not player_pos: return

        # A stationary entity in an IDLE state does nothing until it sees the player.
        if self.is_stationary and self.state == 'IDLE':
            distance_to_player = abs(pos.x - player_pos.x) + abs(pos.y - player_pos.y)
            if distance_to_player > self.sight_radius:
                return  # If player is out of sight, do nothing.

        # --- State Transition Logic ---
        distance_to_player = abs(pos.x - player_pos.x) + abs(pos.y - player_pos.y)

        if distance_to_player <= self.sight_radius:
            # --- Dialogue Trigger ---
            dialogue_comp = self.owner.get_component(DialogueComponent)
            if dialogue_comp and not dialogue_comp.has_spoken:
                if turn_manager.game.dialogue_viewer.start_dialogue(self.owner):
                    turn_manager.game.game_state = GameState.DIALOGUE
                return

            if self.state == 'IDLE':
                turn_manager.game.set_combat_state(True)
            self.state = 'ACTIVE'
            self.turns_since_player_seen = 0
        else:
            self.turns_since_player_seen += 1
            if self.turns_since_player_seen >= AI_FORGET_PLAYER_TURNS:
                self.state = 'IDLE'

        # --- Action Logic based on State ---
        # A stationary entity will not enter the 'move_towards' or 'move_randomly' blocks.
        if self.is_stationary:
            # If adjacent to the player, attack. Otherwise, do nothing.
            if distance_to_player <= 1:
                turn_manager.process_attack(self.owner, player)
            return  # End turn after attacking or doing nothing.

        if self.state == 'ACTIVE':
            if random.randint(1, 100) <= AI_IDLE_ACTION_CHANCE:
                return

            if distance_to_player <= 1:
                turn_manager.process_attack(self.owner, player)
            else:
                self.move_towards(player_pos, turn_manager)

        elif self.state == 'IDLE':
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
    def __init__(self, hp, power, defense, speed, xp_reward=0):
        super().__init__()
        self.max_hp = hp
        self.current_hp = hp
        self.power = power
        self.defense = defense  # The entity's innate damage reduction.
        self.speed = speed
        self.xp_reward = xp_reward # The amount of XP granted when slain.

class InventoryComponent(Component):
    """Holds a list of entities that are considered items in an inventory."""
    def __init__(self):
        super().__init__()
        self.items = []

class ItemComponent(Component):
    """
    A component for entities that can be picked up and used.
    - use_function: The function to call when the item is used.
    - kwargs: A dictionary of arguments to pass to the use function.
    """
    def __init__(self, name: str, use_function: Callable = None, kwargs: Dict[str, Any] = None):
        super().__init__()
        self.name = name
        self.use_function = use_function
        # Store any additional data the use_function might need.
        self.kwargs = kwargs if kwargs is not None else {}

class ExperienceComponent(Component):
    """
    Tracks an entity's level, experience points, and progression toward the next level.
    - Necessity: To provide a persistent sense of character growth and reward for combat.
    - Function: Holds all data required for the leveling system.
    - Effect: Enables a core RPG mechanic where the player becomes stronger over time.
    """
    def __init__(self, base_xp=100, level_factor=1.3):
        super().__init__()
        self.level = 1
        self.current_xp = 0
        # The initial XP requirement is simply the base value.
        self.xp_to_next_level = base_xp
        # Store the formula's components for easy recalculation upon leveling up.
        self.base_xp = base_xp
        self.level_factor = level_factor

class EquipmentComponent(Component):
    """
    Manages an entity's equipped items in designated slots.
    - Necessity: To provide a dedicated container for an entity's active loadout,
                 separating it from their general inventory.
    - Function: Holds a dictionary mapping equipment slots (e.g., "weapon")
                to the equipped item entity.
    - Effect: Enables entities to have a persistent loadout that provides
              bonuses and can be managed by the player.
    """
    def __init__(self):
        super().__init__()
        self.slots = {
            "weapon": None,
            "armor": None
        }

# noinspection SpellCheckingInspection
class EquippableComponent(Component):
    # noinspection SpellCheckingInspection
    """
        Marks an item as equippable and defines its properties.
        - Necessity: To distinguish equippable gear from other items like potions
                     and to define the specific bonuses that gear provides.
        - Function: Stores the item's target slot and its stat bonuses.
        - Effect: Allows any item entity to be turned into a piece of gear with
                  defined characteristics, forming the basis of the loot system.
        """
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        super().__init__()
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus

class VampireComponent(Component):
    """
    A marker component for the Vampire Lord boss.
    - Necessity: To uniquely identify the final boss for special mechanics
                 like regeneration and to trigger the game's victory condition.
    - Function: Acts as a unique flag for the game's systems to query.
    - Effect: Creates a unique, identifiable boss entity.
    """
    def __init__(self):
        super().__init__()

class DialogueComponent(Component):
    """
    Holds the data for a dialogue sequence for an entity.
    - Necessity: To attach a narrative event to an entity, creating a more
                 cinematic and engaging encounter.
    - Function: Stores the speaker's name and lines of dialogue.
    - Effect: A decoupled data container for narrative events.
    """
    def __init__(self, speaker_name, dialogue_lines, subsequent_dialogue_lines=None):
        super().__init__()
        self.speaker_name = speaker_name
        self.dialogue_lines = dialogue_lines
        # For the easter egg on subsequent runs
        self.subsequent_dialogue_lines = subsequent_dialogue_lines if subsequent_dialogue_lines else dialogue_lines
        self.has_spoken = False

class StairsComponent(Component):
    """A marker component for an entity that acts as stairs to the next level."""
    def __init__(self):
        super().__init__()

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

    def get_max_hp(self):
        """Calculates the entity's total max HP, including bonuses from equipment."""
        base_hp = self.get_component(StatsComponent).max_hp

        equipment = self.get_component(EquipmentComponent)
        if equipment:
            for item in equipment.slots.values():
                if item:
                    # noinspection SpellCheckingInspection
                    equippable = item.get_component(EquippableComponent)
                    if equippable:
                        base_hp += equippable.max_hp_bonus
        return base_hp

    def get_power(self):
        """Calculates the entity's total power, including bonuses from equipment."""
        base_power = self.get_component(StatsComponent).power

        equipment = self.get_component(EquipmentComponent)
        if equipment:
            for item in equipment.slots.values():
                if item:
                    # noinspection SpellCheckingInspection
                    equippable = item.get_component(EquippableComponent)
                    if equippable:
                        base_power += equippable.power_bonus
        return base_power

    def get_defense(self):
        """Calculates the entity's total defense, including bonuses from equipment."""
        base_defense = self.get_component(StatsComponent).defense

        equipment = self.get_component(EquipmentComponent)
        if equipment:
            for item in equipment.slots.values():
                if item:
                    # noinspection SpellCheckingInspection
                    equippable = item.get_component(EquippableComponent)
                    if equippable:
                        base_defense += equippable.defense_bonus
        return base_defense

# ==============================================================================
# VII. Game World (Principle: Scalability)
# ==============================================================================

class ProceduralCaveGenerator:
    """
    Handles the creation of organic cave-like maps using a Cellular Automata algorithm.
    This method works by treating each tile as a "cell" that can be either alive (a wall)
    or dead (a floor). Over several generations (steps), simple rules about a cell's
    neighbors create complex, natural-looking cave structures from initial random noise.
    """

    @staticmethod
    def _get_neighbor_wall_count(x, y, tiles):
        """
        Counts the number of wall tiles in the 8 surrounding neighbors of a given cell.
        - Necessity: This is the core sensory input for a cell in the automaton. A cell's
                     fate is determined by how many of its neighbors are walls.
        - Function: Iterates through a 3x3 grid centered on the cell (x, y).
        - Effect: Returns a number from 0 to 8 representing the local wall density.
        """
        wall_count = 0
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                # This checks if the neighbor is outside the map's boundaries.
                if i < 0 or i >= len(tiles) or j < 0 or j >= len(tiles[0]):
                    # Treating out-of-bounds areas as walls is a crucial step.
                    # It ensures that the caves are always fully enclosed by the map edge.
                    wall_count += 1
                # This checks if the neighbor is a wall tile, ignoring the center cell itself.
                elif (i, j) != (y, x) and tiles[i][j] == '#':
                    wall_count += 1
        return wall_count

    @staticmethod
    def _simulation_step(old_tiles):
        """
        Runs a single "generation" of the Cellular Automata simulation.
        - Necessity: To apply the rules of life and death to every cell simultaneously,
                     evolving the map from random noise towards a structured cave.
        - Function: Creates a new, blank map and fills it based on the rules applied to the old map.
        - Effect: The map becomes smoother and more organized with each step.
        """
        width, height = len(old_tiles[0]), len(old_tiles)
        new_tiles = [['.' for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                # Get the sensory input for the current cell.
                wall_neighbors = ProceduralCaveGenerator._get_neighbor_wall_count(x, y, old_tiles)

                # --- The Core Rule of the Automaton ---
                # If a cell has more than 4 wall neighbors, it becomes a wall.
                # If it has 4 or fewer, it becomes a floor. This simple rule, when applied
                # to all cells at once, causes isolated walls to disappear and open
                # spaces to be carved out, forming caves.
                if wall_neighbors > 4:
                    new_tiles[y][x] = '#'
                else:
                    new_tiles[y][x] = '.'
        return new_tiles

    @staticmethod
    def generate_map(width, height):
        """
        Generates a complete and playable cave map by orchestrating the entire process.
        """
        # --- Step 1: Create Initial Random Noise ---
        # The map is seeded with a random pattern of walls and floors. This provides
        # the chaotic starting conditions from which order will emerge. A 45% wall
        # chance is a well-tested value that produces good results.
        tiles = [['.' for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if random.randint(1, 100) < PROCGEN_INITIAL_WALL_CHANCE:  # Use constant
                    tiles[y][x] = '#'

        # --- Step 2: Run the Simulation to Form Caves ---
        # The simulation step is run multiple times. Each run smooths the noise
        # further, connecting walls and opening up caverns. 4-5 iterations is
        # typically enough to achieve a stable, organic-looking result.
        for _ in range(PROCGEN_SIMULATION_STEPS):  # Use constant
            tiles = ProceduralCaveGenerator._simulation_step(tiles)

        # --- Step 3: Enforce a Solid Border ---
        # To ensure the player can never leave the map area, we manually turn all
        # tiles at the edges of the map into walls, guaranteeing a sealed level.
        for y in range(height):
            tiles[y][0] = '#'
            tiles[y][width - 1] = '#'
        for x in range(width):
            tiles[0][x] = '#'
            tiles[height - 1][x] = '#'

        # --- Step 4: Add Cosmetic Floor Texture ---
        # To make the caves feel more natural and less uniform, we iterate through
        # the final floor tiles and give a small percentage of them a different
        # character, representing rubble or debris.
        for y in range(height):
            for x in range(width):
                if tiles[y][x] == '.':
                    if random.randint(1, 100) <= PROCGEN_RUBBLE_CHANCE:  # Use constant
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
# VIII. Dungeon and Turn Management (Principle: Cohesion)
# ==============================================================================

class DungeonManager:
    """Manages dungeon levels, progression, and difficulty scaling."""

    def __init__(self, game_instance):
        """Initializes the DungeonManager with a reference to the main Game object."""
        self.game = game_instance
        self.dungeon_level = 1

        # Check for the warp cheat upon creation.
        if "--vampire" in sys.argv:
            self.dungeon_level = 9
            # The message should be added via the game's HUD instance.
            GameLogger.log("Warp cheat activated.", "CHEAT")  # Use the logger
            self.game.hud.add_message("CHEAT: Warped to Level 9.", (255, 255, 0))

    def next_level(self):
        """Transitions the game to the next dungeon level."""
        self.dungeon_level += 1
        self.game.hud.add_message(f"You descend to level {self.dungeon_level}...", (200, 100, 255))
        # This will call the method we refactored in Step 1.
        self.game.generate_new_level()

    def get_entity_spawn_counts(self):
        """
        Calculates entity spawn counts based on defined rates and dungeon level.
        - Necessity: To create a scalable difficulty curve using a centralized data source.
        - Function: Iterates through SPAWN_RATES to calculate counts for each entity.
        - Effect: The game's challenge increases organically and is easily tunable.
        """
        counts = {}
        # We need to spawn scrolls, daggers, and armor as well, but their spawn
        # counts are currently handled elsewhere. Let's consolidate.
        # The keys here must match the keys in the SPAWN_RATES dictionary.
        items_to_spawn = ["rat", "ghoul", "skeleton", "potion", "scroll", "dagger", "armor"]

        for name in items_to_spawn:
            rates = SPAWN_RATES.get(name)
            if not rates:
                continue  # Skip if no spawn rate is defined for this name

            count = math.ceil(rates["base"] + (self.dungeon_level * rates["scaling"]))

            # Enforce a minimum count if specified (e.g., for potions)
            min_count = rates.get("min", 0)
            if count < min_count:
                count = min_count

            # Ensure count doesn't go below zero for items with negative scaling
            if count < 0:
                count = 0

            counts[name] = count
        return counts

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

        # Check if the destination is a wall.
        if not self.game_map.is_walkable(next_x, next_y):
            return False

        # Check for an entity at the destination.
        target_entity = self.get_entity_at_location(next_x, next_y)
        if target_entity:
            # First, check if the entity is stairs. If so, do nothing here,
            # which will allow the movement code below to execute.
            if target_entity.get_component(StairsComponent):
                pass
            # Next, check if the entity is an item to be picked up.
            elif target_entity.get_component(ItemComponent):
                inventory = self.player.get_component(InventoryComponent)
                item_component = target_entity.get_component(ItemComponent)

                if inventory and item_component:
                    inventory.items.append(target_entity)
                    self.game.entities.remove(target_entity)
                    # Use the item's actual name in the message.
                    item_name = item_component.name
                    self.game.hud.add_message(f"You pick up the {item_name}.", (200, 200, 255))
                    return True  # Picking up an item takes a turn.

            # Otherwise, the entity must be an enemy to attack.
            else:
                self.process_attack(self.player, target_entity)
                return True  # Attacking takes a turn.

        # If there's no entity at the destination, move there.
        pos.x = next_x
        pos.y = next_y
        return True # Moving takes a turn.

    def process_enemy_turns(self):
        """Processes turns for all non-player entities."""
        # We iterate over a copy of the list, as entities might be removed.
        for entity in list(self.turn_takers):
            # Skip the player or any entity that might have been killed this turn.
            if entity is self.player or entity not in self.entities:
                continue

            # --- NEW: Speed Mechanic Implementation ---
            # Get the entity's stats to check its speed.
            stats = entity.get_component(StatsComponent)
            speed = stats.speed if stats else 1 # Default to 1 if no stats.

            # Loop a number of times equal to the entity's speed.
            for _ in range(speed):
                # If the entity was killed by the player during its multi-move
                # (e.g., from a future "attack of opportunity" mechanic),
                # it should not get its remaining actions.
                if entity not in self.entities:
                    break

                ai = entity.get_component(AIComponent)
                if ai:
                    ai.take_turn(self, self.player)

                # --- Vampire Regeneration Mechanic ---
                if entity.get_component(VampireComponent):
                    stats = entity.get_component(StatsComponent)
                    if stats.current_hp < stats.max_hp:
                        stats.current_hp += 1  # Regenerate 1 HP per action

    def process_attack(self, attacker, defender):
        """Handles the logic for one entity attacking another."""
        # --- God Mode Check ---
        if defender is self.game.player and self.game.god_mode_active:
            return

        # Get the defender's stats first, as it's always needed.
        defender_stats = defender.get_component(StatsComponent)
        if not defender_stats: return

        # --- Power Mode Cheat Check ---
        if attacker is self.game.player and self.game.power_mode_active:
            damage = 999
        else:
            # --- Original Damage Calculation ---
            attacker_power = attacker.get_power()
            defender_defense = defender.get_defense()
            damage = attacker_power - defender_defense

        # Ensure damage is at least 0. We don't want attacks to heal the target.
        if damage < 0:
            damage = 0

        defender_stats.current_hp -= damage

        attacker_char = attacker.get_component(RenderComponent).char
        defender_char = defender.get_component(RenderComponent).char

        if damage > 0:
            self.game.hud.add_message(f"The {attacker_char} strikes the {defender_char} for {damage} damage!",
                                      COLOR_MESSAGE_DAMAGE)
        else:
            self.game.hud.add_message(f"The {attacker_char} fails to harm the {defender_char}.", COLOR_MESSAGE_DEFAULT)

        # Check if the defender died.
        if defender_stats.current_hp <= 0:
            self.kill_entity(defender)

    def kill_entity(self, entity):
        """Removes a dead entity, grants XP, and checks if combat has ended."""
        char = entity.get_component(RenderComponent).char

        # --- XP Gain Logic ---
        # Get the stats of the slain entity to find its XP reward.
        entity_stats = entity.get_component(StatsComponent)
        if entity_stats and entity is not self.player:
            xp_reward = entity_stats.xp_reward
            if xp_reward > 0:
                # Get the player's experience component and award the XP.
                player_exp = self.player.get_component(ExperienceComponent)
                player_exp.current_xp += xp_reward
                self.game.hud.add_message(f"You gain {xp_reward} experience.", (100, 150, 255))
                # Check if this XP gain results in a level up.
                self.game.check_player_level_up() # We will create this method next.

        self.game.hud.add_message(f"The {char} is slain!", COLOR_MESSAGE_DEFAULT)

        if entity is self.player:
            GameLogger.log(f"Player died on dungeon level {self.game.dungeon_manager.dungeon_level}.", "EVENT")
            self.game.game_state = GameState.PLAYER_DEAD
        else:
            # --- Victory Condition Check ---
            if entity.get_component(VampireComponent):
                self.game.game_state = GameState.VICTORY

            # Remove the entity from all tracked lists.
            self.game.entities.remove(entity)
            if entity.get_component(TurnTakerComponent):
                self.turn_takers.remove(entity)

            # --- Check if Combat is Over ---
            # After killing an enemy, check if any remaining enemies are still active.
            is_any_enemy_active = False
            for e in self.turn_takers:
                if e is self.player: continue
                ai = e.get_component(AIComponent)
                if ai and ai.state == 'ACTIVE':
                    is_any_enemy_active = True
                    break  # Found an active enemy, no need to check further.

            # If no active enemies are left, turn off combat mode.
            if not is_any_enemy_active:
                self.game.set_combat_state(False)

# ==============================================================================
# IX. Main Game Class
# ==============================================================================

# noinspection SpellCheckingInspection
class Game:
    """The main class that orchestrates the entire game."""

    # noinspection SpellCheckingInspection
    def __init__(self):
        # Initialize all Pygame modules.
        pygame.init()
        # Create the main window and the internal rendering surface.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        pygame.display.set_caption("Untitled Gothic Horror Roguelike")
        self.clock = pygame.time.Clock()
        # In class Game, method __init__
        self.game_state: GameState = GameState.MAIN_MENU

        # --- Menu Initialization ---
        # We now have dedicated instances for each main menu screen.
        self.main_menu = Menu()
        self.options_menu = OptionsMenu()
        self.equipment_menu = EquipmentMenu()
        self.help_menu = HelpMenu()
        self.dialogue_viewer = DialogueViewer()  # Add the new dialogue viewer instance.
        # Give the options menu a reference back to the main game object.
        # This allows it to know the current game state to rebuild its buttons.
        self.options_menu.game = self

        # --- Font Initialization ---
        self.game_font = pygame.font.Font(FONT_PATH, 16)
        self.death_font = pygame.font.Font(FONT_PATH, 60)

        # --- System Initialization ---
        self.camera = Camera(INTERNAL_WIDTH, INTERNAL_HEIGHT)
        self.hud = HUD(self.game_font)
        self.fps_counter = FPSCounter(self.game_font)
        self.debug_overlay = DebugOverlay()

        # --- Game Over Fade Effect Attributes ---
        self.death_fade_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.death_fade_surface.fill(COLOR_NEAR_BLACK)
        self.death_fade_alpha = 0
        self.death_fade_speed = 85  # Controls how fast the screen fades (higher is faster)

        # --- Fast Movement System Attributes ---
        self.fast_move_intent = {'dx': 0, 'dy': 0}
        self.fast_move_timer = 0.0
        self.FAST_MOVE_INTERVAL = 0.1
        self.is_in_combat = False
        self.god_mode_active = False
        self.power_mode_active = False

        # --- Pre-declare Game World Attributes ---
        # We define these here with default values so the linter knows they will
        # always exist on a Game instance.
        self.game_map = None
        self.player = None
        self.entities = []
        self.turn_manager = None
        self.dungeon_manager = None

        # 1. Run the setup method to create the player and managers.
        self.setup_new_game()

        # 2. Check for and apply developer cheats to the managers.
        # Add this block for the god mode cheat
        if "--godmode" in sys.argv:
            self.god_mode_active = True
            GameLogger.log("God Mode cheat activated.", "CHEAT")  # Use the logger
            self.hud.add_message("CHEAT: God Mode Activated.", (255, 215, 0))

        # Add this block for the power mode cheat
        if "--power" in sys.argv:
            self.power_mode_active = False  # You will need to add this attribute
            self.power_mode_active = True
            GameLogger.log("Power Mode cheat activated.", "CHEAT")  # Use the logger
            self.hud.add_message("CHEAT: Power Mode Activated.", (255, 165, 0))

        # --- Developer Cheats Command Line Arguments ---
        # python main.py --vampire (Starts on level 9)
        # python main.py --godmode (Makes you invincible)
        # python main.py --vampire --godmode (Starts on level 9 and makes you invincible)
        # python main.py --vampire --godmode --power (Starts on level 9, makes you invincible, and gives you 999 power)

    def setup_new_game(self):
        """Initializes the game for a new run, creating the player and the first level."""
        # --- Player Entity Creation (Happens only once per game) ---
        self.player = Entity()
        # The initial position doesn't matter, as generate_new_level will place the player.
        self.player.add_component(PositionComponent(0, 0))
        self.player.add_component(RenderComponent('@', COLOR_ENTITY_WHITE))
        self.player.add_component(TurnTakerComponent())
        self.player.add_component(StatsComponent(hp=30, power=5, defense=1, speed=1, xp_reward=0)) # Player grants 0 xp
        self.player.add_component(InventoryComponent())
        self.player.add_component(ExperienceComponent(BASE_XP_TO_LEVEL, LEVEL_UP_FACTOR))
        self.player.add_component(EquipmentComponent())

        # --- Initialize Core Game Systems ---
        self.dungeon_manager = DungeonManager(self)

        # --- Generate the First Level ---
        # This will create the map, place the player, spawn entities, and create the turn manager.
        self.generate_new_level()

    def generate_new_level(self):
        """Creates a new map, places the player, and spawns entities based on dungeon level."""
        spawn_counts = self.dungeon_manager.get_entity_spawn_counts()
        self.game_map = Map(MAP_WIDTH, MAP_HEIGHT)

        spawn_x, spawn_y = self.game_map.spawn_point
        player_pos = self.player.get_component(PositionComponent)
        player_pos.x = spawn_x
        player_pos.y = spawn_y

        self.entities = [self.player]

        if self.dungeon_manager.dungeon_level == VAMPIRE_LEVEL:
            # --- BOSS LEVEL ---
            v_data = ENTITY_DATA["vampire_lord"]
            vampire = Entity()
            vampire.add_component(PositionComponent(MAP_WIDTH // 2, MAP_HEIGHT // 2))
            vampire.add_component(RenderComponent(v_data["char"], v_data["color"]))
            vampire.add_component(StatsComponent(**v_data["stats"]))
            vampire.add_component(AIComponent(is_stationary=True))
            vampire.add_component(VampireComponent())
            vampire.add_component(TurnTakerComponent())
            vampire.add_component(DialogueComponent(
                speaker_name="Vampire Lord",
                dialogue_lines=[
                    "So, another fool arrives to offer their blood.",
                    "You reek of determination. A tedious flavor.",
                    "Let us see if your conviction outlasts your life."
                ],
                subsequent_dialogue_lines=[
                    "You again? Your persistence is a monument to your own futility.",
                    "The abyss has spat you out, but I will send you back."
                ]
            ))
            self.entities.append(vampire)
            player_pos.x = MAP_WIDTH // 2
            player_pos.y = MAP_HEIGHT // 2 + VAMPIRE_SPAWN_OFFSET_Y
        else:
            # --- REGULAR LEVEL ---
            # --- Spawn Enemies ---
            for entity_name in ["rat", "ghoul", "skeleton"]:
                count = spawn_counts.get(entity_name, 0)
                data = ENTITY_DATA[entity_name]
                for _ in range(count):
                    entity = Entity()
                    while True:
                        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                        if self.game_map.is_walkable(x, y) and not any(
                                e.get_component(PositionComponent).x == x and e.get_component(PositionComponent).y == y
                                for e in self.entities):
                            entity.add_component(PositionComponent(x, y))
                            break
                    entity.add_component(RenderComponent(data["char"], data["color"]))
                    entity.add_component(TurnTakerComponent())
                    entity.add_component(AIComponent())
                    entity.add_component(StatsComponent(**data["stats"]))
                    self.entities.append(entity)

            # --- Spawn Items & Equipment ---
            for item_name, data in ITEM_DATA.items():
                spawn_key = data["spawn_key"]
                count = spawn_counts.get(spawn_key, 0)
                for _ in range(count):
                    item = Entity()
                    while True:
                        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                        if self.game_map.is_walkable(x, y) and not any(
                                e.get_component(PositionComponent).x == x and e.get_component(PositionComponent).y == y
                                for e in self.entities):
                            item.add_component(PositionComponent(x, y))
                            break
                    item.add_component(RenderComponent(data["char"], data["color"]))

                    # Build the kwargs dictionary for the ItemComponent
                    final_kwargs = data.get("kwargs", {}).copy()
                    if item_name == "teleport_scroll":
                        # noinspection PyTypeChecker
                        final_kwargs.update({"game_map": self.game_map, "entities": self.entities})

                    item.add_component(
                        ItemComponent(name=data["name"], use_function=data.get("use_function"), kwargs=final_kwargs)
                    )

                    # Add EquippableComponent if it exists
                    if "equip" in data:
                        item.add_component(EquippableComponent(**data["equip"]))

                    self.entities.append(item)

            # --- Spawn Stairs Down ---
            stairs = Entity()
            while True:
                x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
                distance_to_player = math.sqrt((x - spawn_x) ** 2 + (y - spawn_y) ** 2)
                if self.game_map.is_walkable(x, y) and distance_to_player > STAIRS_MIN_DISTANCE_FROM_SPAWN:
                    stairs.add_component(PositionComponent(x, y))
                    break
            stairs.add_component(RenderComponent('>', (255, 165, 0)))
            stairs.add_component(StairsComponent())
            self.entities.append(stairs)

        self.turn_manager = TurnManager(game_object=self)

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

    def set_combat_state(self, is_fighting):
        """Sets the game's combat state, enabling or disabling fast movement."""
        self.is_in_combat = is_fighting

    def check_player_level_up(self):
        """Checks if the player has enough XP to level up and processes it."""
        player_exp = self.player.get_component(ExperienceComponent)
        player_stats = self.player.get_component(StatsComponent)

        # Use a while loop in case the player gains enough XP for multiple levels at once.
        while player_exp.current_xp >= player_exp.xp_to_next_level:
            # 1. "Spend" the XP for the level up.
            player_exp.current_xp -= player_exp.xp_to_next_level

            # 2. Increment the player's level.
            player_exp.level += 1

            # 3. Recalculate the XP requirement for the *next* level using our formula.
            player_exp.xp_to_next_level = int(player_exp.base_xp * (player_exp.level ** player_exp.level_factor))

            # 4. Apply the level-up bonuses.
            player_stats.max_hp += 10
            player_stats.power += 1

            # 5. Fully heal the player as a reward.
            player_stats.current_hp = player_stats.max_hp

            # 6. Announce the level up.
            self.hud.add_message(f"You feel stronger! You have reached level {player_exp.level}!", (50, 255, 50))

    def equip_item(self, item_to_equip):
        """Handles the logic of equipping an item from inventory."""
        inventory = self.player.get_component(InventoryComponent)
        equipment = self.player.get_component(EquipmentComponent)
        # noinspection SpellCheckingInspection
        equippable = item_to_equip.get_component(EquippableComponent)

        if not all([inventory, equipment, equippable]):
            return  # Safety check

        slot = equippable.slot

        # --- Unequip Old Item (if any) ---
        # Check if there is already an item in the target slot.
        currently_equipped_item = equipment.slots.get(slot)
        if currently_equipped_item:
            # Move the currently equipped item back to the inventory list.
            inventory.items.append(currently_equipped_item)
            item_name = currently_equipped_item.get_component(ItemComponent).name
            self.hud.add_message(f"You unequip the {item_name}.", (255, 255, 100))

        # --- Equip New Item ---
        # Remove the new item from the inventory list.
        inventory.items.remove(item_to_equip)
        # Place the new item into the now-empty slot.
        equipment.slots[slot] = item_to_equip
        item_name = item_to_equip.get_component(ItemComponent).name
        self.hud.add_message(f"You equip the {item_name}.", (100, 255, 100))

    def handle_events(self):
        """
        Processes all pending events from Pygame's event queue.

        This method acts as the central hub for all user input. It is structured
        as a state machine, where the logic applied depends entirely on the current
        value of `self.game_state`. This ensures that input is only processed
        in the correct context (e.g., movement keys only work during the player's
        turn, menu navigation only works in menus).

        The method iterates through each event provided by Pygame and routes it
        to the appropriate logic block.
        """
        for event in pygame.event.get():
            # ------------------------------------------------------------------
            # I. Global Event Handling
            # These events are checked first as they are the highest priority
            # and can occur regardless of the current game state.
            # ------------------------------------------------------------------

            # The user clicked the window's close button. This is an explicit
            # signal to terminate the application immediately.
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return  # Exit the method immediately to stop further processing.

            # --- Help Menu Toggle ---
            # This is checked globally, outside the main state machine, so it's always accessible.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.help_menu.toggle()

            # A key was pressed. We check for global hotkeys here.
            if event.type == pygame.KEYDOWN:
                # The F12 key toggles the developer debug overlay. This is a
                # tool for us and should always be available.
                if event.key == pygame.K_F12:
                    self.debug_overlay.toggle()

            # ------------------------------------------------------------------
            # II. State-Based Event Handling
            # This is the core of the state machine. An if/elif chain directs
            # the event to the logic block corresponding to the current game state.
            # ------------------------------------------------------------------

            if self.game_state == GameState.PLAYER_DEAD:
                # CONTEXT: The player has died.
                # GOAL: Wait for the player to acknowledge their demise and
                #       return to the main menu.
                # We only listen for a single input: the Enter key.
                # This input is only accepted *after* the fade-to-black
                # animation has fully completed.
                if self.death_fade_alpha >= 255 and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Reset the game world for a fresh start.
                        self.setup_new_game()
                        # Transition back to the main menu.
                        self.game_state = GameState.MAIN_MENU

            elif self.game_state == GameState.MAIN_MENU:
                # CONTEXT: The player is at the main title screen.
                # GOAL: Let the Menu object handle navigation and return an action.
                action = self.main_menu.handle_input(event)
                if action:
                    # An action was returned (e.g., "Start Game" or "Options").
                    # If the player chose to start, we must set up a new game world.
                    if action == GameState.PLAYER_TURN:
                        self.setup_new_game()

                    # Transition to the new state returned by the menu.
                    self.game_state = action
                    # If the new state is the options menu, we must build its buttons.
                    if self.game_state == GameState.OPTIONS_ROOT:
                        self.options_menu.rebuild_buttons(self.game_state)

            elif self.game_state in [GameState.OPTIONS_ROOT, GameState.OPTIONS_VIDEO]:
                # CONTEXT: The player is in one of the options sub-menus.
                # GOAL: Let the OptionsMenu object handle navigation and return an action.
                action = self.options_menu.handle_input(event)
                if action:
                    # The action can be either a state change or a command.
                    if isinstance(action, GameState):
                        # The action is a state change (e.g., going "Back" or
                        # entering a sub-menu).
                        self.game_state = action
                        # We must rebuild the menu to show the correct buttons
                        # for the new options screen.
                        if self.game_state in [GameState.OPTIONS_ROOT, GameState.OPTIONS_VIDEO]:
                            self.options_menu.rebuild_buttons(self.game_state)
                    elif isinstance(action, dict):
                        # The action is a command (e.g., "change_resolution").
                        action_type = action.get("type")
                        if action_type == "resolution":
                            self.change_resolution(action["index"])
                            # noinspection PyTypeChecker
                            self.options_menu.rebuild_buttons(self.game_state)
                        elif action_type == "toggle_fps":
                            current_setting = settings_manager.get("show_fps")
                            settings_manager.set("show_fps", not current_setting)
                            settings_manager.save_settings()
                            # noinspection PyTypeChecker
                            self.options_menu.rebuild_buttons(self.game_state)

            elif self.game_state == GameState.EQUIP_MENU:
                # CONTEXT: The player is managing their equipment.
                # GOAL: Let the EquipmentMenu handle input and return an action.
                action = self.equipment_menu.handle_input(event)
                if action:
                    if action["type"] == "close":
                        self.game_state = GameState.PLAYER_TURN
                    elif action["type"] == "equip":
                        self.equip_item(action["item"])
                        # After equipping, the inventory has changed, so rebuild the options.
                        self.equipment_menu.rebuild_options(self.player)

            elif self.game_state == GameState.DIALOGUE:
                # In this state, pass all input exclusively to the dialogue viewer.
                action = self.dialogue_viewer.handle_input(event)
                if action == "finished":
                    # When dialogue is over, return control to the player.
                    self.game_state = GameState.PLAYER_TURN

            elif self.game_state == GameState.VICTORY:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.setup_new_game()
                    self.game_state = GameState.MAIN_MENU

            elif self.game_state == GameState.PLAYER_TURN:
                # CONTEXT: It is the player's turn to act.
                # GOAL: Process a single, discrete action from a key press.
                if event.type == pygame.KEYDOWN:
                    # --- Action: Open Equipment Menu ---
                    if event.key == pygame.K_e:
                        # Rebuild the menu's options before showing it.
                        self.equipment_menu.rebuild_options(self.player)
                        self.game_state = GameState.EQUIP_MENU

                    action_taken = False

                    # --- Action: Use Health Potion ---
                    if event.key == pygame.K_h:
                        inventory = self.player.get_component(InventoryComponent)
                        if inventory and inventory.items:
                            # Find the first health potion in the inventory.
                            potion_to_use = next((item for item in inventory.items if
                                                  item.get_component(ItemComponent).name == "Health Potion"), None)
                            if potion_to_use:
                                inventory.items.remove(potion_to_use)
                                item_component = potion_to_use.get_component(ItemComponent)
                                if item_component.use_function:
                                    item_component.use_function(entity=self.player, **item_component.kwargs)
                                    self.hud.add_message("You drink a potion and feel better.", COLOR_HEALING_RED)
                                    action_taken = True
                            else:
                                self.hud.add_message("You have no potions to use.", (255, 255, 100))
                        else:
                            self.hud.add_message("You have no potions to use.", (255, 255, 100))

                    # --- Action: Read Scroll ---
                    elif event.key == pygame.K_r:
                        inventory = self.player.get_component(InventoryComponent)
                        if inventory and inventory.items:
                            # Find a scroll in the inventory.
                            scroll_to_use = next((item for item in inventory.items if
                                                  item.get_component(ItemComponent).name == "Scroll of Teleportation"),
                                                 None)
                            if scroll_to_use:
                                inventory.items.remove(scroll_to_use)
                                item_component = scroll_to_use.get_component(ItemComponent)
                                if item_component.use_function:
                                    item_component.use_function(entity=self.player, **item_component.kwargs)
                                    self.hud.add_message("You read the scroll and vanish!", COLOR_SCROLL_BLUE)
                                    action_taken = True
                            else:
                                self.hud.add_message("You have no scrolls to read.", (255, 255, 100))
                        else:
                            self.hud.add_message("You have no scrolls to read.", (255, 255, 100))

                    # --- Action: Descend Stairs ---
                    elif event.key == pygame.K_PERIOD and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        player_pos = self.player.get_component(PositionComponent)

                        # Find if a stairs entity exists at the player's current coordinates.
                        stairs_found = False
                        for entity in self.entities:
                            pos = entity.get_component(PositionComponent)
                            # Check for an entity that is NOT the player, is at the same location, and has a StairsComponent.
                            if entity is not self.player and pos and pos.x == player_pos.x and pos.y == player_pos.y:
                                if entity.get_component(StairsComponent):
                                    stairs_found = True
                                    break  # Exit the loop once stairs are found.

                        if stairs_found:
                            self.dungeon_manager.next_level()
                            action_taken = True  # Descending takes a turn.
                        else:
                            # This message provides feedback if the player hits '>' but is not on stairs.
                            self.hud.add_message("There are no stairs here.", (255, 255, 100))

                    # --- Action: Movement ---
                    else:
                        dx, dy = 0, 0
                        if event.key in (pygame.K_UP, pygame.K_w):
                            dy = -1
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            dy = 1
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            dx = -1
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            dx = 1
                        if dx != 0 or dy != 0:
                            if self.turn_manager.process_player_turn(dx, dy):
                                action_taken = True

                    # If an action was taken AND the game was not won, end the player's turn.
                    if action_taken and self.game_state != GameState.VICTORY:
                        self.game_state = GameState.ENEMY_TURN

    def update(self, delta_time):
        """
        Updates the game's state. Called once per frame.
        The logic is structured as a state machine, ensuring only the code for
        the current game state is executed.
        """
        self.help_menu.update(delta_time)  # Update the help menu's animation timer.
        # This is a clean if/elif chain, making the state transitions mutually exclusive.
        if self.game_state == GameState.MAIN_MENU:
            self.main_menu.update(delta_time)

        elif self.game_state == GameState.PLAYER_TURN:
            # Fast movement logic is only active when not in combat.
            if not self.is_in_combat:
                keys = pygame.key.get_pressed()
                dx, dy = 0, 0
                # By explicitly casting the key state to a boolean, we provide a clear
                # type hint that resolves the linter's confusion with Pygame.
                # noinspection PyUnresolvedReferences
                if bool(keys[pygame.K_UP]) or bool(keys[pygame.K_w]):
                    dy = -1
                elif bool(keys[pygame.K_DOWN]) or bool(keys[pygame.K_s]):
                    dy = 1
                elif bool(keys[pygame.K_LEFT]) or bool(keys[pygame.K_a]):
                    dx = -1
                elif bool(keys[pygame.K_RIGHT]) or bool(keys[pygame.K_d]):
                    dx = 1

                if dx != 0 or dy != 0:
                    self.fast_move_timer += delta_time
                    if self.fast_move_timer >= self.FAST_MOVE_INTERVAL:
                        self.fast_move_timer = 0.0
                        if self.turn_manager.process_player_turn(dx, dy):
                            self.game_state = GameState.ENEMY_TURN

        elif self.game_state == GameState.ENEMY_TURN:
            self.turn_manager.process_enemy_turns()
            # If the player died or dialogue started, the state is handled.
            # Otherwise, it's now the player's turn.
            if self.game_state != GameState.PLAYER_DEAD and self.game_state != GameState.DIALOGUE:
                self.game_state = GameState.PLAYER_TURN

        elif self.game_state == GameState.EQUIP_MENU:
            pass  # The menu is static and only updates based on key events.

        elif self.game_state == GameState.PLAYER_DEAD:
            # If the player is dead, we only update the fade-to-black animation.
            self.death_fade_alpha += DEATH_FADE_SPEED * delta_time  # Use constant
            if self.death_fade_alpha > 255:
                self.death_fade_alpha = 255

    def draw(self):
        """Draws everything to the screen, based on the current game state."""
        self.internal_surface.fill(COLOR_NEAR_BLACK)

        # --- State-Based Drawing Logic ---
        if self.game_state == GameState.MAIN_MENU:
            self.main_menu.draw(self.internal_surface)

        elif self.game_state in [GameState.OPTIONS_ROOT, GameState.OPTIONS_VIDEO]:
            self.options_menu.draw(self.internal_surface, self.game_state)

        # --- Combined Block for All In-Game States ---
        # If the state is any of the main gameplay states (including the equip menu),
        # we always draw the game world first.
        elif self.game_state in [GameState.PLAYER_TURN, GameState.ENEMY_TURN, GameState.PLAYER_DEAD,
                                 GameState.EQUIP_MENU, GameState.DIALOGUE, GameState.VICTORY]:
            self.camera.update(self.player)

            # Draw the game world, entities, and HUD.
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
                    # This check ensures we only render entities that are actually on screen.
                    if self.internal_surface.get_rect().colliderect(visible_rect):
                        text_surface = self.game_font.render(render.char, True, render.color)
                        text_draw_rect = text_surface.get_rect(center=visible_rect.center)
                        self.internal_surface.blit(text_surface, text_draw_rect)

            self.hud.draw(self.internal_surface, self.player, self.dungeon_manager)

        # --- Conditional Overlays ---
        # Now, draw specific overlays ON TOP of the game world based on the state.
        if self.game_state == GameState.EQUIP_MENU:
            self.equipment_menu.draw(self.internal_surface, self.player)
        elif self.game_state == GameState.DIALOGUE:
            self.dialogue_viewer.draw(self.internal_surface)
        elif self.game_state == GameState.VICTORY:
            # Draw a simple victory message.
            victory_font = self.death_font
            victory_text = victory_font.render("YOU ARE VICTORIOUS", True, (255, 215, 0))  # Gold color
            text_rect = victory_text.get_rect(center=(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2 - 30))
            self.internal_surface.blit(victory_text, text_rect)

            restart_font = self.options_menu.button_font
            restart_text = restart_font.render("Press Enter to Return to the Menu", True, COLOR_WHITE)
            restart_rect = restart_text.get_rect(center=(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2 + 40))
            self.internal_surface.blit(restart_text, restart_rect)

        elif self.game_state == GameState.PLAYER_DEAD:
            # Set the transparency of our fade surface based on the current alpha.
            self.death_fade_surface.set_alpha(int(self.death_fade_alpha))
            # Draw the semi-transparent black surface over the whole screen.
            self.internal_surface.blit(self.death_fade_surface, (0, 0))

            # Only draw the death text and restart prompt after the screen is mostly faded.
            if self.death_fade_alpha > DEATH_TEXT_FADE_THRESHOLD:  # Use constant
                death_text = self.death_font.render("YOU DIED", True, COLOR_BLOOD_RED)
                # ...
                text_rect = death_text.get_rect(center=(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2 - 30))
                self.internal_surface.blit(death_text, text_rect)

                restart_font = self.options_menu.button_font
                restart_text = restart_font.render("Press Enter to Return to the Menu", True, COLOR_WHITE)
                restart_rect = restart_text.get_rect(center=(INTERNAL_WIDTH / 2, INTERNAL_HEIGHT / 2 + 40))
                self.internal_surface.blit(restart_text, restart_rect)

        # --- Always-on-Top Drawing ---
        # Draw the FPS counter in ANY state, if enabled.
        if settings_manager.get("show_fps"):
            self.fps_counter.draw(self.internal_surface, self.clock)

        # Draw the help menu.
        self.help_menu.draw(self.internal_surface)

        # Always draw the debug overlay if it's enabled.
        self.debug_overlay.draw(self.internal_surface,
                                {"FPS": f"{self.clock.get_fps():.1f}", "State": self.game_state.name})

        # Final scaling and screen update.
        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        # Final scaling and screen update.
        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

# ==============================================================================
# X. Heads-Up Display (HUD) System
# ==============================================================================

class HUD:
    """
    Manages the rendering of all persistent on-screen UI elements,
    such as the health bar and message log.
    - Necessity: To provide the player with critical, real-time feedback
                 about their status and game events.
    - Function: Draws static and dynamic UI elements in fixed positions.
    - Effect: A clear, informative overlay that enables tactical decision-making.
    """

    def __init__(self, font):
        self.font = font
        self.messages = []  # This will hold the game log messages later.

    def add_message(self, text, color=COLOR_MESSAGE_DEFAULT):
        """
        Adds a new message to the HUD's message log.
        - Necessity: To provide a centralized way for other game systems
                     to send feedback to the player.
        - Function: Appends a new message (text and color) to a list and
                    ensures the list does not exceed a maximum size.
        - Effect: The UI can display a scrolling log of recent game events.
        """
        self.messages.insert(0, (text, color))
        if len(self.messages) > HUD_MESSAGE_COUNT:
            self.messages.pop()

    def draw(self, surface, player, dungeon_manager):
        """Draws all HUD elements onto the provided surface."""
        self.draw_health_bar(surface, player)
        self.draw_xp_bar(surface, player) # Call the new method here.
        self.draw_message_log(surface)
        self.draw_item_status(surface, player)
        self.draw_dungeon_level(surface, dungeon_manager)

    def draw_health_bar(self, surface, player):
        """Calculates and draws the player's health bar."""
        player_stats = player.get_component(StatsComponent)
        if not player_stats: return

        # --- Health Bar Calculation ---
        health_percentage = player_stats.current_hp / player_stats.max_hp
        num_active_dashes = int(health_percentage * HUD_HEALTH_BAR_DASHES)

        # --- Color Determination Logic (The "Pokémon Component") ---
        if num_active_dashes >= 11:
            bar_color = COLOR_HEALTH_GREEN
        elif 5 <= num_active_dashes <= 10:
            bar_color = COLOR_HEALTH_YELLOW
        elif 2 <= num_active_dashes <= 4:
            bar_color = COLOR_HEALTH_ORANGE
        else:
            bar_color = COLOR_HEALTH_RED

        # --- String Construction ---
        active_bar_string = "—" * num_active_dashes
        inactive_bar_string = "—" * (HUD_HEALTH_BAR_DASHES - num_active_dashes)
        numerical_text = f" HP: {player_stats.current_hp}/{player_stats.max_hp}"

        # --- Rendering ---
        # Define the starting position for the HUD in the top-left corner.
        x, y = 10, 10

        # Render the active (filled) part of the bar.
        active_surface = self.font.render(active_bar_string, True, bar_color)
        surface.blit(active_surface, (x, y))

        # Render the inactive (empty) part of the bar, positioned after the active part.
        inactive_x = x + active_surface.get_width()
        inactive_surface = self.font.render(inactive_bar_string, True, COLOR_HUD_EMPTY_DASH)
        surface.blit(inactive_surface, (inactive_x, y))

        # Render the numerical text, positioned after the full bar.
        text_x = inactive_x + inactive_surface.get_width()
        text_surface = self.font.render(numerical_text, True, COLOR_WHITE)
        surface.blit(text_surface, (text_x, y))

    def draw_xp_bar(self, surface, player):
        """Calculates and draws the player's experience bar."""
        player_exp = player.get_component(ExperienceComponent)
        if not player_exp: return

        # --- XP Bar Calculation ---
        # Prevent division by zero if xp_to_next_level is somehow 0.
        xp_percentage = 0
        if player_exp.xp_to_next_level > 0:
            xp_percentage = player_exp.current_xp / player_exp.xp_to_next_level

        bar_width = 150  # The total pixel width of the XP bar.
        current_bar_width = int(bar_width * xp_percentage)

        # --- String Construction ---
        level_text = f"LVL: {player_exp.level}"
        xp_text = f"XP: {player_exp.current_xp}/{player_exp.xp_to_next_level}"

        # --- Rendering ---
        x, y = 10, 30  # Position below the health bar.

        # Render the text labels.
        level_surface = self.font.render(level_text, True, COLOR_WHITE)
        surface.blit(level_surface, (x, y))

        xp_text_surface = self.font.render(xp_text, True, COLOR_WHITE)
        # Position the XP text to the right of the level text.
        surface.blit(xp_text_surface, (x + level_surface.get_width() + 10, y))

        # Render the background of the XP bar.
        bar_bg_rect = pygame.Rect(x, y + 20, bar_width, 8)
        pygame.draw.rect(surface, COLOR_HUD_EMPTY_DASH, bar_bg_rect)

        # Render the filled part of the XP bar.
        bar_fill_rect = pygame.Rect(x, y + 20, current_bar_width, 8)
        pygame.draw.rect(surface, COLOR_XP_BLUE, bar_fill_rect)

    def draw_message_log(self, surface):
        """
        Draws the game's message log to the screen.
        """
        x = 10
        y = 70  # Start below the health and XP bars.

        for text, color in self.messages:
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, y))
            y += self.font.get_height() + 2

    def draw_item_status(self, surface, player):
        """Draws the count of all named items in the player's inventory."""
        inventory = player.get_component(InventoryComponent)
        if not inventory: return

        item_counts = {}
        # Count the occurrences of each named item.
        for item in inventory.items:
            item_name = item.get_component(ItemComponent).name
            item_counts[item_name] = item_counts.get(item_name, 0) + 1

        # Define the display order and colors for items.
        display_items = {
            "Health Potion": COLOR_HEALING_RED,
            "Scroll of Teleportation": COLOR_SCROLL_BLUE
        }

        y_offset = INTERNAL_HEIGHT - self.font.get_height() - 10
        for item_name, color in display_items.items():
            count = item_counts.get(item_name, 0)
            if count > 0:
                text = f"{item_name}s: {count}"
                text_surface = self.font.render(text, True, color)
                surface.blit(text_surface, (10, y_offset))
                # Move the next item's text up.
                y_offset -= self.font.get_height() + 5

    def draw_dungeon_level(self, surface, dungeon_manager):
        """Draws the current dungeon level to the bottom-right of the screen."""
        level_text = f"Level: {dungeon_manager.dungeon_level}"
        text_surface = self.font.render(level_text, True, COLOR_WHITE)

        # Position in the bottom-right corner with a margin.
        margin = 10
        x_pos = INTERNAL_WIDTH - text_surface.get_width() - margin
        y_pos = INTERNAL_HEIGHT - text_surface.get_height() - margin

        surface.blit(text_surface, (x_pos, y_pos))

# ==============================================================================
# XI. Development Tools
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
        if not self.enabled: return

        # Start the Y-position near the top.
        y_offset = 30 # Move down to not overlap with the new FPS counter

        # Define a right-side margin.
        margin = 10

        for key, value in data.items():
            text = f"{key}: {value}"
            text_surface = self.font.render(text, True, (255, 255, 0))

            # Calculate the X-position to right-align the text.
            x_pos = INTERNAL_WIDTH - text_surface.get_width() - margin

            surface.blit(text_surface, (x_pos, y_offset))
            y_offset += 15

class FPSCounter:
    """A simple, player-facing class to display the current FPS."""

    def __init__(self, font):
        self.font = font

    def draw(self, surface, clock):
        """Draws the FPS counter to the top-right of the surface."""
        # Get the FPS from the game's clock and format it.
        fps_text = f"FPS: {clock.get_fps():.1f}"
        text_surface = self.font.render(fps_text, True, COLOR_WHITE)

        # Calculate position for the top-right corner.
        margin = 10
        x_pos = INTERNAL_WIDTH - text_surface.get_width() - margin
        y_pos = 10

        surface.blit(text_surface, (x_pos, y_pos))

class GameLogger:
    """Simple logging system for tracking game events and errors."""
    # Build the full, correct path to the log file
    LOG_FILE = user_data_dir / "gothic_rogue_log.txt"

    @staticmethod
    def log(message, level="INFO"):
        """Logs a message to the console and a file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"

        print(log_message)  # Continue printing to console for live feedback

        try:
            with open(GameLogger.LOG_FILE, "a") as f:
                f.write(log_message + "\n")
        except Exception as e:
            # Don't crash the game if logging fails, just report it
            print(f"CRITICAL: GameLogger failed to write to file: {e}")

# ==============================================================================
# XII. Entry Point
# ==============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
