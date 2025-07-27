# Standard Operating Procedure: Daily Development Workflow with PyCharm

**Michael Banovac**

**June 29, 2025**

**System: Fedora Workstation**

---

This document outlines the standard daily workflow for working on a Python project using PyCharm as the code editor. It assumes all prior setup from "SOP: Python Development Environment Setup" and "SOP: Python Project Workflow" has been completed.

The core principle remains the separation of the development tools from the execution environment. The graphical IDE (PyCharm) runs on the host Fedora system for a smooth user experience, while the Python code itself is executed within the isolated py-dev container to ensure dependencies are managed cleanly and do not affect the host system.

## I. Development Session Startup

(Perform these steps each time you want to work on a project.)

**Step 1: Launch PyCharm and Open Project Folder**

On your main Fedora desktop, launch PyCharm from the system's application menu. Inside PyCharm, open your project-specific folder.

- **Action:** In the PyCharm welcome window, click "**Open**" and navigate to and select your project folder.
- **Example Path:** ~/Projects/gothic-rogue
- **Generic Path:** ~/Projects/[project-name]
- **Importance:** This loads your project files into the editor, allowing you to view, write, and manage your source code.

**Step 2: Open a Separate Terminal Window**

On your main Fedora desktop, launch your standard terminal application (e.g., GNOME Terminal). This terminal is separate from PyCharm and will be used to run your code.

- **Importance:** This window serves as your direct access to the py-dev container where the code will actually be executed.

**Step 3: Enter Container and Activate Project Environment**

Inside the newly opened terminal, you will perform a sequence of commands to enter the container and prepare the project-specific Python environment.

1. **Enter the development container.**
   - **Command:** distrobox enter py-dev

2. **Navigate to the project folder.** Your terminal is now inside the container, but you need to move to the correct directory.
   - **Example Command:** cd ~/Projects/gothic-rogue
   - **Generic Command:** cd ~/Projects/[project-name]

3. **Activate the project's virtual environment.** This is the most crucial step to ensure your code can find its specific packages, like Pygame.
   - **Command:** source venv/bin/activate
   - **Verification:** Your terminal prompt will change to show (venv) at the beginning.

**Step 4: Run Your Code**

With the environment activated, you can now execute your Python script.

- **Command:** python main.py
- **Importance:** This runs your game or application. Any output or errors will be displayed in this terminal window.

## II. Exiting the Environment

(Perform these steps when you are finished working.)

**Step 1: Deactivate the Virtual Environment**

In your terminal, deactivate the venv to exit the project-specific environment.

- **Command:** deactivate
- **Verification:** The (venv) prefix will disappear from your terminal prompt.

**Step 2: Exit the Container**

Return from the py-dev container back to your main Fedora system's terminal.

- **Command:** exit

You can now safely close the terminal window and PyCharm.

---

*--- End of Standard Operating Procedure ---*
