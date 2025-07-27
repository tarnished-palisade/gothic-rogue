# Standard Operating Procedure: Local Version Control with Git

**Michael Banovac**

**June 29, 2025**

**System: Fedora Workstation (within py-dev container)**

---

This document outlines the standard workflow for using Git for local version control. This process creates a detailed, restorable history of a project directly on your PC, without requiring an online account or service. It serves as a powerful development diary and safety net.

The core principle is to capture the project's evolution as a series of atomic, well-documented snapshots (commits). This allows for fearless experimentation, precise bug tracking, and a complete historical record of every change made.

## I. One-Time Project Initialization

(Perform these steps once for each new project after following the "SOP: Python Project Workflow".)

**Step 1: Navigate to Project Directory**

Open a terminal, enter your development container, and navigate to the specific project folder you intend to track.

**Command (Enter Container):**
```
distrobox enter py-dev
```

**Example Command (Navigate):**
```
cd ~/Projects/gothic-rogue
```

**Generic Command (Navigate):**
```
cd ~/Projects/[project-name]
```

**Step 2: Initialize the Git Repository**

This command turns the current directory into a Git repository.

**Command:**
```
git init
```

**Importance:** This creates a hidden sub-folder named .git. This folder is the repository itself—a self-contained database that will store every commit, every version of every file, and the entire history of your project.

**Step 3: Create a .gitignore File**

Create a special file to tell Git which files and folders it should intentionally ignore. This is critical for keeping your repository clean.

**Command:**
```
touch .gitignore
```

Open this new .gitignore file in your code editor and add the following lines for a typical Python project:

```
# Python virtual environment
/venv/

# Python cache
__pycache__/
*.pyc

# IDE / Editor specific files
.vscode/
.idea/
```

**Importance:** This prevents temporary files, caches, and environment-specific folders from being accidentally added to your project's history. It ensures only your actual source code and assets are tracked.

## II. The Core Development Cycle

(Perform these steps repeatedly as you write code.)

This three-step process—Status, Add, Commit—is the fundamental rhythm of working with Git.

**Step 1: Check the Status**

Before doing anything, check the state of your project. Git will tell you which files have been modified, which are new (untracked), and which are staged for the next commit.

**Command:**
```
git status
```

**Step 2: Stage Changes**

Choose which changes you want to include in your next snapshot. This is called "staging."

**Example Command (Stage a single file):**
```
git add main.py
```

**Generic Command (Stage a single file):**
```
git add [file-name]
```

**Command (Stage all modified/new files):**
```
git add .
```

**Importance:** Staging allows you to be precise. You can modify ten files but create a commit that only includes the changes from three of them, grouping logical changes together even if you made them at the same time.

**Step 3: Commit the Snapshot**

Save the staged files as a new permanent snapshot in your project's history. You must include a message describing the change.

**Example Command:**
```
git commit -m "Feat: Implement initial player class and movement logic"
```

**Generic Command:**
```
git commit -m "[type]: [A short, clear description of the change]"
```

**Importance:** The commit message is a crucial piece of documentation. It provides context for *why* a change was made. Good messages make your project history readable and understandable months or years later.

## III. Commit Cadence and Example

**When to Commit**

A commit should represent a single, complete, logical unit of work. Commit your code when:

- You have successfully implemented a new feature (e.g., enemy AI, a scoring system).
- You have fixed a specific bug.
- You have finished refactoring a piece of code to improve it.
- You are about to start a risky or experimental change and want a safe checkpoint to return to.

**Example of a Code Change Warranting a Commit**

Imagine you are working on your game. You have just written the code to define the player and allow them to move. The code is functional. This is a perfect, atomic unit of work to commit.

**Code Chunk (player.py):**

```python
# player.py
# Defines the Player class for the game.

import pygame

class Player(pygame.sprite.Sprite):
    """
    Represents the player character, handling movement and state.
    """
    def __init__(self, start_x, start_y):
        super().__init__()
        self.image = pygame.Surface([32, 32])
        self.image.fill((255, 0, 0))  # Player is a red square for now
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self.speed = 5

    def update(self):
        """ Handles player input for movement. """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
```

After saving this file, you would run the following commands to commit this specific feature:

```
git add player.py
git commit -m "Feat: Create Player class with basic WASD movement"
```

**Concluding Note**

This local-only workflow creates a robust, self-contained repository on your machine. This repository, with its entire detailed history, is perfectly prepared to be linked to an online service like GitHub for backup or collaboration at any point in the future with a few simple commands.

---

*--- End of Standard Operating Procedure ---*