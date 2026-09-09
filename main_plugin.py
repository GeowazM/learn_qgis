from qgis.PyQt.QtWidgets import QAction, QDockWidget, QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from .tour_logic import SpotlightTour, get_spotlight_steps, get_interactive_steps
import os

class QgisTourPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action_toggle_panel = None
        self.dock_widget = None
        self.tour_instance = None

    def initGui(self):
        # Icon einbinden (jetzt mit dem korrekten Dateinamen)
        icon_path = os.path.join(self.plugin_dir, "owl.svg")
        
        self.action_toggle_panel = QAction(QIcon(icon_path), "QGIS Lern-Assistent öffnen", self.iface.mainWindow())
        self.action_toggle_panel.triggered.connect(self.toggle_panel)
        self.iface.addToolBarIcon(self.action_toggle_panel)
        self.iface.addPluginToMenu("&QGIS Tour", self.action_toggle_panel)

    def unload(self):
        self.iface.removePluginMenu("&QGIS Tour", self.action_toggle_panel)
        self.iface.removeToolBarIcon(self.action_toggle_panel)
        if self.dock_widget:
            self.iface.removeDockWidget(self.dock_widget)

    def toggle_panel(self):
        if not self.dock_widget:
            self.create_dock_widget()
        
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()

    def create_dock_widget(self):
        self.dock_widget = QDockWidget("QGIS Lern-Assistent", self.iface.mainWindow())
        # --- NEU: Interner Objektname, um das Fenster in der Tour leichter zu finden ---
        self.dock_widget.setObjectName("QgisTourDockWidget")
        self.dock_widget.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        container = QWidget()
        layout = QVBoxLayout()
        
        self.lbl_lang = QLabel("Sprache / Language:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "English", "Español"])
        
        self.lbl_tours = QLabel("<b>Verfügbare Touren:</b>")
        
        self.btn_tour_ui = QPushButton("1. Bedienoberfläche kennenlernen")
        self.btn_tour_ui.clicked.connect(self.start_ui_tour)
        
        self.btn_tour_interact = QPushButton("2. Interaktive Anleitung (Hintergrundkarte)")
        self.btn_tour_interact.clicked.connect(self.start_interactive_tour)
        
        layout.addWidget(self.lbl_lang)
        layout.addWidget(self.lang_combo)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_tours)
        layout.addWidget(self.btn_tour_ui)
        layout.addWidget(self.btn_tour_interact)
        layout.addStretch()
        
        container.setLayout(layout)
        self.dock_widget.setWidget(container)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        
        self.lang_combo.currentIndexChanged.connect(self.update_ui_texts)
        self.update_ui_texts()

    def get_lang_code(self):
        lang = self.lang_combo.currentText()
        if lang == "English": return "en"
        if lang == "Español": return "es"
        return "de"
        
    def update_ui_texts(self):
        code = self.get_lang_code()
        if code == "en":
            self.dock_widget.setWindowTitle("QGIS Learning Assistant")
            self.lbl_lang.setText("Language:")
            self.lbl_tours.setText("<b>Available Tours:</b>")
            self.btn_tour_ui.setText("1. Get to know the Interface")
            self.btn_tour_interact.setText("2. Interactive Guide (Basemap)")
        elif code == "es":
            self.dock_widget.setWindowTitle("Asistente de Aprendizaje")
            self.lbl_lang.setText("Idioma:")
            self.lbl_tours.setText("<b>Tours Disponibles:</b>")
            self.btn_tour_ui.setText("1. Conocer la Interfaz")
            self.btn_tour_interact.setText("2. Guía Interactiva (Mapa base)")
        else:
            self.dock_widget.setWindowTitle("QGIS Lern-Assistent")
            self.lbl_lang.setText("Sprache / Language:")
            self.lbl_tours.setText("<b>Verfügbare Touren:</b>")
            self.btn_tour_ui.setText("1. Bedienoberfläche kennenlernen")
            self.btn_tour_interact.setText("2. Interaktives Anleiten (Hintergrundkarte)")

    def close_active_tour(self):
        if self.tour_instance:
            try:
                self.tour_instance.close()
            except:
                pass

    def start_ui_tour(self):
        self.close_active_tour()
        steps = get_spotlight_steps(self.iface, self.get_lang_code())
        self.tour_instance = SpotlightTour(steps, self.iface)
        self.tour_instance.show()
        
    def start_interactive_tour(self):
        self.close_active_tour()
        steps = get_interactive_steps(self.iface, self.get_lang_code())
        self.tour_instance = SpotlightTour(steps, self.iface)
        self.tour_instance.show()
