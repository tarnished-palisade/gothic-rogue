# Replication Guide: Python Game Development

**Michael Banovac**

**July 24, 2025**

*Project: Gothic Horror Roguelike*

---

This document provides complete instructions for replicating, studying, or forking this Python game project on any compatible system. All necessary information for independent setup and execution is contained within this guide.

## **I. Development Environment Specifications**

### **System Requirements**

**Minimum Hardware:**
- CPU: Any x86_64 processor from 2015 or later
- RAM: 4GB minimum (8GB recommended)
- Storage: 500MB free space
- Display: 800x600 minimum resolution

**Verified Operating Systems:**
- Linux: Fedora 42, Ubuntu 22.04 LTS, Debian 12
- Windows: Windows 10 (22H2), Windows 11
- macOS: macOS 12 Monterey or later (Intel and Apple Silicon)

### **Core Dependencies**

**Python Environment:**
- Python: 3.13.5 (exact version used in development)
- Package Manager: pip 25.1.1

**Required Python Libraries:**
- pygame: 2.6.1
- platformdirs: 4.3.8

**System Libraries:**
- SDL2: SDL2-devel (Note: May need to be installed separately)
- SDL2_image: 2.8.8-1.fc42.x86_64
- SDL2_mixer: 2.8.1-1.fc42.x86_64
- SDL2_ttf: 2.22.0-4.fc42.x86_64

## **II. Project Structure**

```
gothic-rogue/
├── .github/
│   └── workflows/
│       └── build-executables.yml
├── assets/
│   └── Consolas.ttf
├── Session_01/
│   ├── session_01_code_review_claude_25_06_29.md
│   └── session_01_progress_report_gemini_25_06_29.md
├── ... (Sessions 02 through 19)
├── Session_20/
│   ├── session_20_code_review_claude_25_07_24.md
│   └── session_20_progress_report_gemini_25_07_24.md
├── standard_operating_procedures/
│   ├── sop_daily_development_workflow_pycharm.md
│   ├── sop_local_version_control_git.md
│   ├── sop_python_development_environment_setup.md
│   ├── sop_python_project_workflow.md
│   └── sop_script_line_count_ceilings_protocol.md
├── verification/
│   └── checksums.txt
├── .gitignore
├── ai_collaboration.md
├── code_doctrine.md
├── LICENSE
├── main.py
├── project_charter_retrospective.md
├── README.md
└── test_gothic_rogue.py
```

## **III. Setup Instructions**

### **Linux Setup (Fedora/RHEL)**

1. **Install Python and Development Tools:**
   ```bash
   sudo dnf install python3.13 python3-pip
   sudo dnf install gcc python3-devel
   ```

2. **Install SDL2 Libraries:**
   ```bash
   sudo dnf install SDL2-devel SDL2_image-devel
   sudo dnf install SDL2_mixer-devel SDL2_ttf-devel
   ```

3. **Create Project Environment:**
   ```bash
   mkdir -p ~/Projects/gothic-rogue
   cd ~/Projects/gothic-rogue
   python3.13 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python Dependencies:**
   ```bash
   pip install pygame==2.6.1 platformdirs==4.3.8
   ```

### **Linux Setup (Ubuntu/Debian)**

1. **Install Python and Development Tools:**
   ```bash
   sudo apt update
   sudo apt install python3.13 python3-pip python3.13-venv
   sudo apt install build-essential python3.13-dev
   ```

2. **Install SDL2 Libraries:**
   ```bash
   sudo apt install libsdl2-dev libsdl2-image-dev
   sudo apt install libsdl2-mixer-dev libsdl2-ttf-dev
   ```

3. **Follow steps 3-4 from Fedora instructions above**

### **Windows Setup**

1. **Install Python:**
   - Download Python 3.13.5 from python.org
   - Check "Add Python to PATH" during installation

2. **Install via Command Prompt:**
   ```cmd
   cd %USERPROFILE%\Projects\gothic-rogue
   python -m venv venv
   venv\Scripts\activate
   pip install pygame==2.6.1 platformdirs==4.3.8
   ```

### **macOS Setup**

1. **Install Homebrew (if needed):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Dependencies:**
   ```bash
   brew install python@3.13
   brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
   ```

3. **Follow steps 3-4 from Linux instructions**

## **IV. Running the Game**

### **Standard Execution**

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run the game
python main.py
```

### **Running Tests**

```bash
# Run the test suite
python test_gothic_rogue.py
```

### **Command Line Options**

```bash
python main.py --vampire        # Start on dungeon level 9
python main.py --godmode        # Make player invincible
python main.py --power          # Give player 999 attack power
```
# These can be combined:

```bash
python main.py --vampire --godmode --power
```

## **V. Development Information**

### **Architecture Overview**

The game uses a single-script architecture with the following primary systems:

1. **State Management:** Enum-based finite state machine
2. **Rendering:** Internal surface with resolution-independent scaling
3. **Input Handling:** Event-driven keyboard input system
4. **Game Logic:** Turn-based mechanics with discrete time steps
5. **Procedural Generation:** Deterministic dungeon creation algorithms

### **Code Organization**

```python
# Section I: Settings Manager (Principle: Preservation Axiom)
# Section II: Item Functions
# Section III: Configuration and Constants (Principle: Adaptable)
# Section IV: State Management (Principle: Coherence)
# Section V: UI Classes (Principle: Modularity)
# Section VI: Entity-Component System (ECS) (Principle: Modularity)
# Section VII: Game World (Principle: Scalability)
# Section VIII: Dungeon and Turn Management (Principle: Cohesion)
# Section IX: Main Game Class
# Section X: Heads-Up Display (HUD) System
# Section XI: Development Tools
# Section XII: Entry Point
```

### **Key Design Patterns**

- **Entity-Component System:** For game objects
- **State Machine:** For game flow control
- **Observer Pattern:** For event handling
- **Factory Pattern:** For procedural generation

## **VI. Modification Guide**

### **Adding New Features**

1. **New Game States:** Add to GameState enum
2. **New Entities:** Extend Entity base class
3. **New UI Elements:** Follow Button class pattern
4. **New Levels:** Modify generation algorithms

### **Performance Considerations**

- Frame rate capped at 60 FPS
- Viewport culling implemented for rendering optimization
- Turn-based mechanics ensure predictable performance
- Single-threaded design for simplicity and reliability

## **VII. Troubleshooting**

### **Common Issues**

**Issue:** "pygame not found" error
**Solution:** Ensure virtual environment is activated

**Issue:** Poor performance
**Solution:** Verify SDL2 hardware acceleration is enabled

### **Debug Mode**

Toggle debug overlay during gameplay by pressing F12. This displays FPS and current game state.

## **VIII. File Verification**

All distributed files can be verified using the checksums in verification/checksums.txt:

```bash
sha256sum -c verification/checksums.txt  # Linux/macOS
# or
CertUtil -hashfile [filename] SHA256     # Windows
```

## **IX. Build Information**

### **Compilation Details**

**Source Type:** Interpreted Python (no compilation required)
**Bytecode:** Python automatically generates .pyc files in __pycache__

### **Creating Standalone Executable (Optional)**

```bash
pip install pyinstaller==6.14.2
# For Linux/macOS
pyinstaller --onefile --windowed --add-data "assets:assets" main.py
# For Windows
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

## **X. Contact and Support**

**Project Repository:** [Will be provided upon release]
**Developer Contact:** [Will be provided upon release]
**Response Time:** Inquiries acknowledged within 14 days

## **XI. Quick Start**

For experienced developers who want to run immediately:

```bash
# Assumes Python 3.13+ and SDL2 are installed
git clone [repository]
cd gothic-rogue
python -m venv venv && source venv/bin/activate
pip install pygame==2.6.1 platformdirs==4.3.8
python main.py
```

---

This guide contains all information necessary for complete project replication. No external documentation or resources are required.
