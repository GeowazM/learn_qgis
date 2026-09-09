# QGIS Learning Assistant (QGIS Lern-Assistent) 

This plugin provides beginners with a short tour of the QGIS interface. It is designed to help new users quickly understand the layout of QGIS and perform their first interactive tasks, such as installing plugins and adding basemaps.

## Features

* **Interactive Dock Widget:** A user-friendly side panel to control the learning experience.
* **Multilingual Support:** The UI and all tour instructions are available in English, German, and Spanish.
* **Spotlight UI Tour:** A guided, darkened screen overlay that highlights core QGIS interface elements step-by-step.
* **Interactive Task Guide:** An active walk-through that waits for the user to perform specific clicks (e.g., opening the plugin manager, installing a tool, adding a map).

## Installation

Since this plugin is currently distributed as a `.zip` file, you can install it directly within QGIS:

1. Open QGIS.
2. Go to **Plugins** > **Manage and Install Plugins...** in the top menu bar.
3. Select the **Install from ZIP** tab on the left.
4. Click the `...` button, locate the `qgis_grundlagentour_plugin_v10.zip` file, and select it.
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

## Requirements
* **QGIS Version:** 3.0 or higher.
* Python 3 & PyQt5/PyQt6 (Standard with modern QGIS installations).
