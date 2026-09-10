# Learn QGIS Assistant (QGIS Lern-Assistent) 

This plugin provides beginners with a short tour of the QGIS interface. It is designed to help new users quickly understand the layout of QGIS and perform their first interactive tasks, such as installing plugins and adding basemaps.

## Features

* **Interactive Dock Widget:** A user-friendly side panel to control the learning experience.
* **Multilingual Support:** The UI and all tour instructions are available in English, German, and Spanish.
* **Spotlight UI Tour:** A guided, darkened screen overlay that highlights core QGIS interface elements step-by-step.
* **Interactive Task Guide:** An active walk-through that waits for the user to perform specific clicks (e.g., opening the plugin manager, installing a tool, adding a map).

## Requirements
* **QGIS Version:** 3.0 or higher.
* Python 3 & PyQt5/PyQt6 (Standard with modern QGIS installations).

## Installation

Since this plugin is currently distributed as a `.zip` file, you can install it directly within QGIS:

1. Open QGIS.
2. Go to **Plugins** > **Manage and Install Plugins...** in the top menu bar.
3. Select the **Install from ZIP** tab on the left.
4. Click the `...` button, locate the `lean_qgis.zip` file, and select it.
5. Click **Install Plugin**.
6. Accept any security warnings regarding ZIP installations.
7. Close the Plugin Manager.

## Usage

Once installed, you will see a new **Owl icon** in your QGIS toolbar and a new menu entry under **Plugins > QGIS Tour**.

1. Click the **"QGIS Lern-Assistent öffnen"** (Open QGIS Learning Assistant) button.
2. A new panel will dock on the right side of your QGIS window.
3. **Select your language** from the dropdown at the top (Deutsch, English, Español). The interface will translate instantly.
4. Choose one of the available tours to start learning!

### Available Tours

#### 1. Get to know the Interface (Bedienoberfläche kennenlernen)
A visual "Spotlight" tour. The screen dims, highlighting one UI element at a time while providing a brief explanation. It covers:
* The Main Menu Bar
* Toolbars
* The Browser Panel
* The Layers Panel
* The Map Canvas
* The Plugin / Analysis Dock
* The Status Bar

#### 2. Interactive Guide (Interaktives Anleiten)
A hands-on task to get you started with real GIS work. The plugin gives you an instruction and waits for you to complete it before moving on. It guides you through:
1. Opening the QGIS Plugin Manager.
2. Searching for and installing the **QuickMapServices** plugin.
3. Adding a web-based background map (Basemap) to your project.

*Note: If you already have QuickMapServices installed, the guide will intelligently skip the installation steps and directly ask you to add a basemap.*

## Canceling a Tour
You can exit a tour at any time by clicking the red **Cancel Tour** (Tour abbrechen) button located in the top right corner of the screen.


## Cross-Platform Compatibility

The QGIS Learning Assistant plugin is fully cross-platform and is designed to run seamlessly on QGIS installations across **Windows**, **macOS**, and **Linux**. 

### Technical Implementation

The plugin's architecture ensures OS-independent execution through the following mechanisms:

* **File Path Handling:** The codebase utilizes Python's native `os.path` module (specifically `os.path.join()` and `os.path.dirname(__file__)`) to construct file paths. This guarantees that the correct directory separators (`\` for Windows, `/` for macOS/Linux) are dynamically applied when locating assets like `owl.svg`.
* **UI Framework (PyQt):** The graphical user interface is built upon the Qt framework (supporting both PyQt5 and PyQt6). Qt is inherently cross-platform, meaning that all panels, buttons, and dropdowns will automatically inherit the native visual style of the host operating system (e.g., macOS UI elements on a Mac, GNOME/KDE styles on Linux).
* **External URL Routing:** To handle the download links in the exercise section, the plugin uses Python's standard `webbrowser` library. This module automatically detects the host OS and safely routes URLs to the user's default system browser without requiring OS-specific terminal commands.
* **QGIS API Core:** All interactions with the QGIS application rely on the standard `qgis.utils.iface` API (such as `iface.mainWindow()` and `iface.mapCanvas()`), which functions uniformly across all supported platforms.

### Notes on Linux Environments

* **Window Compositing:** The Spotlight Tour utilizes a semi-transparent dark overlay (`Qt.WA_TranslucentBackground`). This requires the operating system's window manager to support compositing (transparency).
    * **Windows & macOS:** Supported natively by default.
    * **Linux:** Supported by default on all modern desktop environments (e.g., Ubuntu/GNOME, Linux Mint/Cinnamon, KDE Plasma). On legacy or extremely lightweight window managers without an active compositor, the overlay may render as solid black rather than transparent.
