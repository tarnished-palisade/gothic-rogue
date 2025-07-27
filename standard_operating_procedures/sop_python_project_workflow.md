# Standard Operating Procedure: Python Project Workflow

**Michael Banovac**

**June 29, 2025**

**System: Fedora Workstation**

---

This document outlines the standard workflow for creating and working on a specific Python project. It assumes the general development environment has already been established as per the "SOP: Python Development Environment Setup" document.

The core principle is to create a self-contained *virtual environment* for each individual project. This isolates one project's specific dependencies (e.g., Pygame version 2.1) from another's (e.g., Pygame version 2.5), preventing conflicts.

## I. New Project Initialization

(Perform these steps once for each new project.)

**Step 1: Create the Project-Specific Folder**

On your main Fedora desktop, create a new folder inside your central ~/Projects directory.

- **Example Command:**
  ```
  mkdir ~/Projects/gothic-rogue
  ```

- **Generic Command:**
  ```
  mkdir ~/Projects/[project-name]
  ```

- **Importance:** This folder will contain all the files for this one project: your Python source code, images, sound files, and its isolated virtual environment.

**Step 2: Enter Your Development Container**

Open a terminal and enter the py-dev workshop.

- **Command:**
  ```
  distrobox enter py-dev
  ```

**Step 3: Create the Project's Virtual Environment**

Inside the container, navigate to your new project folder and create a virtual environment within it.

1. **Navigate to the project folder.**
   - **Example:** cd ~/Projects/gothic-rogue
   - **Generic:** cd ~/Projects/[project-name]

2. **Create the virtual environment (commonly named venv).**
   ```
   python3 -m venv venv
   ```

- **Importance:** This creates a venv sub-folder containing a private copy of Python and a place to install packages. This is the most crucial step for ensuring projects do not interfere with each other.

**Step 4: Activate the Environment and Install Dependencies**

Activate the new environment and install the specific Python packages this project needs.

1. **Activate the environment.** Your terminal prompt will change to show (venv) at the beginning.
   ```
   source venv/bin/activate
   ```

2. **Install necessary packages (e.g., Pygame).**
   ```
   pip install pygame
   ```

- **Importance:** Activating the environment ensures that the pip install command places packages inside the project's private venv folder, not into the main system.

## II. Daily Workflow (Working on a Project)

(Perform these steps each time you want to work on the project.)

1. **Open Project in Code Editor:** On your main Fedora desktop, open your code editor (like VS Code or GNOME Text Editor) and open the project folder (e.g., ~/Projects/gothic-rogue) to edit your .py files.

2. **Enter Container:** In a terminal, enter your development workshop.
   ```
   distrobox enter py-dev
   ```

3. **Navigate to Project Folder:**
   - **Example:** cd ~/Projects/gothic-rogue
   - **Generic:** cd ~/Projects/[project-name]

4. **Activate Virtual Environment:** You must activate the correct environment for your code to find its dependencies.
   ```
   source venv/bin/activate
   ```

5. **Run Your Code:** Execute your script using Python.
   ```
   python main.py
   ```

## III. Exiting the Environment

(Perform these steps when you are finished working.)

1. **Deactivate the Virtual Environment:** This returns your terminal to the container's standard environment. The (venv) prefix will disappear.
   ```
   deactivate
   ```

2. **Exit the Container:** This returns you to your main Fedora system's terminal.
   ```
   exit
   ```

---

*--- End of Standard Operating Procedure ---*