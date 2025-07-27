# Standard Operating Procedure: Python Development Environment Setup

**Michael Banovac**

**June 29, 2025**

**System: Fedora Workstation**

---

This document outlines the standard, one-time process for establishing a clean, containerized development environment for Python projects. This procedure should be performed after a fresh OS installation and initial system setup (including user creation and driver installation).

The core principle is to use a container to isolate all programming tools (compilers, libraries, dependencies) from the main operating system, keeping the host system clean and stable while providing a powerful and flexible "workshop" for development.

## I. Create a Central Project Directory

First, create a dedicated, top-level directory in your home folder to house all of your development projects. This separates your source code from your regular documents.

- **Command:**
  ```
  mkdir ~/Projects
  ```

- **Importance:** This establishes a clean architectural separation between your personal documents (in ~/Documents) and your development workspace. It is a standard convention that simplifies project management, backups, and tooling configuration.

## II. Install the Container Management Tool (Distrobox)

Next, install Distrobox, a powerful tool that allows you to create and manage development environments that are tightly integrated with your home directory.

- **Command:**
  ```
  sudo dnf install distrobox
  ```

- **Importance:** Distrobox enables you to install all your programming tools and dependencies into an isolated container, preventing them from cluttering or potentially conflicting with your main Fedora system.

## III. Create the General Python "Workshop" Container

Now, create a specific container that will serve as your general-purpose Python development environment.

- **Command:**
  ```
  distrobox create --image fedora:42 --name py-dev
  ```

- **Importance:** This command downloads a minimal Fedora image and sets it up as a container named py-dev. This container is your dedicated "workshop" where all Python-related software will be installed.

## IV. Enter the Container and Install Core Dependencies

Finally, enter the newly created container and install the essential system-level packages required for Python programming and for libraries like Pygame to function.

1. **Enter the container.** Your terminal prompt will change to indicate you are inside.
   ```
   distrobox enter py-dev
   ```

2. **Install Python and its package manager, Pip.**
   ```
   sudo dnf install python3 python3-pip
   ```

3. **Install low-level libraries for graphics and sound (for Pygame).**
   ```
   sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
   ```

- **Importance:** These tools are the foundational building blocks within your container. Installing them here ensures that any project running inside the py-dev container has access to them, without affecting your host system.

At the conclusion of this procedure, your general Python development environment is fully configured and ready for you to start creating specific projects.

---

*--- End of Standard Operating Procedure ---*