from qgis.PyQt.QtWidgets import QAction, QDockWidget, QVBoxLayout, QWidget, QComboBox, QLabel, QPushButton, QMessageBox, QFrame, QApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from .tour_logic import SpotlightTour, get_spotlight_steps, get_interactive_steps
import os
import webbrowser

# PyQt6 / PyQt5 Kompatibilität für Qt Enums
try:
    RIGHT_DOCK = Qt.DockWidgetArea.RightDockWidgetArea
    LEFT_DOCK = Qt.DockWidgetArea.LeftDockWidgetArea
    RICH_TEXT = Qt.TextFormat.RichText
    HAND_CURSOR = Qt.CursorShape.PointingHandCursor
except AttributeError:
    RIGHT_DOCK = Qt.RightDockWidgetArea
    LEFT_DOCK = Qt.LeftDockWidgetArea
    RICH_TEXT = Qt.RichText
    HAND_CURSOR = Qt.PointingHandCursor

class QgisTourPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action_toggle_panel = None
        self.dock_widget = None
        self.tour_instance = None
        self.current_exercise = 1

    def initGui(self):
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
        self.dock_widget.setObjectName("QgisTourDockWidget")
        self.dock_widget.setAllowedAreas(RIGHT_DOCK | LEFT_DOCK)
        
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

        self.btn_tour_exercise_1 = QPushButton("3. Übungsaufgabe (Puffer-Analyse)")
        self.btn_tour_exercise_1.clicked.connect(lambda: self.start_exercise_tour(1))

        self.btn_tour_exercise_2 = QPushButton("4. Übungsaufgabe (Erdbeben & Tektonik)")
        self.btn_tour_exercise_2.clicked.connect(lambda: self.start_exercise_tour(2))
        
        self.btn_tour_exercise_3 = QPushButton("5. Übungsaufgabe (Vulkane & Rasterdaten)")
        self.btn_tour_exercise_3.clicked.connect(lambda: self.start_exercise_tour(3))
        
        layout.addWidget(self.lbl_lang)
        layout.addWidget(self.lang_combo)
        layout.addSpacing(20)
        layout.addWidget(self.lbl_tours)
        layout.addWidget(self.btn_tour_ui)
        layout.addWidget(self.btn_tour_interact)
        layout.addWidget(self.btn_tour_exercise_1)
        layout.addWidget(self.btn_tour_exercise_2)
        layout.addWidget(self.btn_tour_exercise_3)
        
        # --- ABGETRENNTER BEREICH FÜR ÜBUNGSAUFGABEN (MyST Style) ---
        self.exercise_frame = QFrame()
        self.exercise_frame.setObjectName("ExerciseFrame")
        self.exercise_frame.setStyleSheet("#ExerciseFrame { border-top: 2px solid #bdc3c7; margin-top: 15px; padding-top: 10px; }")
        self.exercise_frame.setVisible(False)
        
        ex_layout = QVBoxLayout(self.exercise_frame)
        ex_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_ex_title = QLabel()
        
        # MyST 'Note' Admonition
        self.lbl_ex_desc = QLabel()
        self.lbl_ex_desc.setWordWrap(True)
        self.lbl_ex_desc.setTextFormat(RICH_TEXT)
        
        self.btn_ex_hint = QPushButton("Tipp anzeigen")
        self.btn_ex_hint.setCursor(HAND_CURSOR)
        self.btn_ex_hint.clicked.connect(self.toggle_hint)
        
        # MyST 'Tip' Admonition
        self.lbl_ex_hint = QLabel()
        self.lbl_ex_hint.setWordWrap(True)
        self.lbl_ex_hint.setTextFormat(RICH_TEXT)
        self.lbl_ex_hint.setVisible(False)
        
        self.lbl_ex_link = QLabel()
        self.lbl_ex_link.setOpenExternalLinks(True)
        
        # Download Button für Aufgabe 3 (Öffnet jetzt nur den Link)
        self.btn_download_data = QPushButton("Geodaten für Aufgabe Vulkane herunterladen")
        self.btn_download_data.setCursor(HAND_CURSOR)
        self.btn_download_data.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_download_data.clicked.connect(self.open_download_link)
        self.btn_download_data.setVisible(False)
        
        ex_layout.addWidget(self.lbl_ex_title)
        ex_layout.addSpacing(5)
        ex_layout.addWidget(self.lbl_ex_desc)
        ex_layout.addWidget(self.btn_download_data)
        ex_layout.addSpacing(10)
        ex_layout.addWidget(self.btn_ex_hint)
        ex_layout.addWidget(self.lbl_ex_hint)
        ex_layout.addSpacing(10)
        ex_layout.addWidget(self.lbl_ex_link)
        
        layout.addWidget(self.exercise_frame)
        # ----------------------------------------

        layout.addStretch()
        
        container.setLayout(layout)
        self.dock_widget.setWidget(container)
        self.iface.addDockWidget(RIGHT_DOCK, self.dock_widget)
        
        self.lang_combo.currentIndexChanged.connect(self.update_ui_texts)
        self.update_ui_texts()

    def toggle_hint(self):
        is_visible = self.lbl_ex_hint.isVisible()
        self.lbl_ex_hint.setVisible(not is_visible)

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
            self.btn_tour_exercise_1.setText("3. Exercise (Buffer Analysis)")
            self.btn_tour_exercise_2.setText("4. Exercise (Earthquakes & Tectonics)")
            self.btn_tour_exercise_3.setText("5. Exercise (Volcanoes & Rasters)")
            self.btn_ex_hint.setText("Toggle Hint")
            self.btn_download_data.setText("Download Geodata for Volcanoes Exercise")
        elif code == "es":
            self.dock_widget.setWindowTitle("Asistente de Aprendizaje")
            self.lbl_lang.setText("Idioma:")
            self.lbl_tours.setText("<b>Tours Disponibles:</b>")
            self.btn_tour_ui.setText("1. Conocer la Interfaz")
            self.btn_tour_interact.setText("2. Guía Interactiva (Mapa base)")
            self.btn_tour_exercise_1.setText("3. Ejercicio (Análisis de zona de influencia)")
            self.btn_tour_exercise_2.setText("4. Ejercicio (Terremotos y Tectónica)")
            self.btn_tour_exercise_3.setText("5. Ejercicio (Volcanes y Rasters)")
            self.btn_ex_hint.setText("Mostrar/Ocultar Pista")
            self.btn_download_data.setText("Descargar datos para el ejercicio de volcanes")
        else:
            self.dock_widget.setWindowTitle("QGIS Lern-Assistent")
            self.lbl_lang.setText("Sprache / Language:")
            self.lbl_tours.setText("<b>Verfügbare Touren:</b>")
            self.btn_tour_ui.setText("1. Bedienoberfläche kennenlernen")
            self.btn_tour_interact.setText("2. Interaktives Anleiten (Hintergrundkarte)")
            self.btn_tour_exercise_1.setText("3. Übungsaufgabe (Puffer-Analyse)")
            self.btn_tour_exercise_2.setText("4. Übungsaufgabe (Erdbeben & Tektonik)")
            self.btn_tour_exercise_3.setText("5. Übungsaufgabe (Vulkane & Rasterdaten)")
            self.btn_ex_hint.setText("Tipp ein-/ausblenden")
            self.btn_download_data.setText("Geodaten für Aufgabe Vulkane herunterladen")
            
        self.update_exercise_texts()

    def update_exercise_texts(self):
        code = self.get_lang_code()
        myst_note_style = "background-color: #ebf5fb; border-left: 4px solid #3498db; padding: 10px; border-radius: 0px 4px 4px 0px; margin: 5px 0px;"
        myst_tip_style = "background-color: #e8f8f5; border-left: 4px solid #1abc9c; padding: 10px; border-radius: 0px 4px 4px 0px; margin: 5px 0px;"

        self.btn_download_data.setVisible(self.current_exercise == 3)

        if self.current_exercise == 1:
            if code == "en":
                self.lbl_ex_title.setText("<b>Exercise 3: Buffer Analysis</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Scenario</b><br><br>We want to identify buildings that are too close to a road. Find a road layer and a building layer. Buffer the roads by 50 meters and identify the buildings that fall into this buffer zone.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tip</b><br><br>Open 'Vector > Geoprocessing Tools > Buffer' to buffer the roads. Then use 'Vector > Research Tools > Select by Location' to find buildings intersecting the new buffer.</div>")
                self.lbl_ex_link.setText(f"<a href='https://docs.qgis.org/3.44/en/docs/gentle_gis_introduction/vector_spatial_analysis_buffers.html#now-you-try' style='color: #2980b9; text-decoration: none;'><b>➤ View Solution in QGIS Docs</b></a>")
            elif code == "es":
                self.lbl_ex_title.setText("<b>Ejercicio 3: Análisis de zona de influencia</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Escenario</b><br><br>Queremos identificar edificios que están demasiado cerca de una carretera. Cree un área de influencia (buffer) de 50 metros alrededor de las carreteras e identifique qué edificios caen dentro de esta zona.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Pista</b><br><br>Use 'Vectorial > Herramientas de geoproceso > Buffer' para las carreteras. Luego use 'Selección por localización' para encontrar los edificios.</div>")
                self.lbl_ex_link.setText(f"<a href='https://docs.qgis.org/3.44/es/docs/gentle_gis_introduction/vector_spatial_analysis_buffers.html#now-you-try' style='color: #2980b9; text-decoration: none;'><b>➤ Ver solución en la documentación</b></a>")
            else:
                self.lbl_ex_title.setText("<b>Übungsaufgabe 3: Puffer-Analyse</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Szenario</b><br><br>Wir möchten herausfinden, welche Gebäude sich zu nah an einer Hauptstraße befinden. Puffern Sie eine Straßen-Ebene mit 50 Metern und finden Sie heraus, welche Gebäude in diese Pufferzone fallen.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tipp</b><br><br>Nutzen Sie das Werkzeug 'Puffer' (Vektor > Geoverarbeitungswerkzeuge > Puffer) für die Straßen. Verwenden Sie danach 'Nach Ort auswählen' (Vektor > Forschungswerkzeuge), um Gebäude innerhalb des Puffers zu markieren.</div>")
                self.lbl_ex_link.setText(f"<a href='https://docs.qgis.org/3.44/de/docs/gentle_gis_introduction/vector_spatial_analysis_buffers.html#now-you-try' style='color: #2980b9; text-decoration: none;'><b>➤ Lösung in QGIS-Doku ansehen</b></a>")
        
        elif self.current_exercise == 2:
            if code == "en":
                self.lbl_ex_title.setText("<b>Exercise 4: Earthquakes & Tectonics</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Scenario</b><br><br>We want to investigate the distribution of earthquakes in relation to tectonic plate boundaries. Download the corresponding vector data and add it to QGIS. Adjust the earthquake symbology (e.g., scale point size by magnitude).</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tip</b><br><br>Use the 'Data Source Manager' to add the vector layers. Go to 'Layer Properties > Symbology' to change the styling (e.g., use 'Graduated' to vary the size of the points based on magnitude).</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/en/latest/lessons/L1/exercise-1-tectonicplates.html' style='color: #2980b9; text-decoration: none;'><b>➤ View Exercise Tutorial</b></a>")
            elif code == "es":
                self.lbl_ex_title.setText("<b>Ejercicio 4: Terremotos y Tectónica</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Escenario</b><br><br>Queremos investigar la distribución de los terremotos en relación con los límites de las placas tectónicas. Descargue los datos vectoriales correspondientes y añádalos a QGIS. Ajuste la simbología de los terremotos (ej. tamaño del punto por magnitud).</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Pista</b><br><br>Utilice el 'Administrador de fuentes de datos' para añadir las capas vectoriales. Vaya a 'Propiedades de la capa > Simbología' para cambiar el estilo (ej. use 'Graduado' para el tamaño).</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/es/latest/lessons/L1/exercise-1-tectonicplates.html' style='color: #2980b9; text-decoration: none;'><b>➤ Ver Ejercicio en el Tutorial</b></a>")
            else:
                self.lbl_ex_title.setText("<b>Übungsaufgabe 4: Erdbeben & Tektonik</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Szenario</b><br><br>Wir wollen die Verteilung von Erdbeben im Zusammenhang mit tektonischen Plattengrenzen untersuchen. Laden Sie die bereitgestellten Vektordaten herunter und fügen Sie diese in QGIS ein. Passen Sie die Darstellung an (z.B. Größe der Punkte nach Erdbeben-Magnitude).</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tipp</b><br><br>Nutzen Sie den Datenquellenverwalter (Strg+L), um die Daten hinzuzufügen. Unter 'Layer-Eigenschaften > Symbolisierung' können Sie die Darstellung auf 'Abgestuft' stellen, um die Punkte nach Größe zu variieren.</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/de/latest/lessons/L1/exercise-1-tectonicplates.html' style='color: #2980b9; text-decoration: none;'><b>➤ Übung im Tutorial ansehen</b></a>")

        elif self.current_exercise == 3:
            if code == "en":
                self.lbl_ex_title.setText("<b>Exercise 5: Volcanoes & Raster Data</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Scenario</b><br><br>Let's investigate volcanoes and topographic features. Use the button below to download the dataset and load it into QGIS. Afterwards, follow the tutorial to adjust the symbology.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tip</b><br><br>Once the raster layer (DEM) is loaded, go to 'Symbology' and change the render type to 'Singleband pseudocolor' to apply a color ramp to the elevation data.</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/en/latest/lessons/L3/exercise-3-vulcanoes.html' style='color: #2980b9; text-decoration: none;'><b>➤ View Exercise Tutorial</b></a>")
            elif code == "es":
                self.lbl_ex_title.setText("<b>Ejercicio 5: Volcanes y Datos Raster</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Escenario</b><br><br>Investiguemos los volcanes y la topografía. Use el botón abajo para descargar los datos y cargarlos en QGIS. Luego siga el tutorial para ajustar la simbología.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Pista</b><br><br>Una vez cargado el raster (DEM), vaya a 'Simbología' y cambie el tipo a 'Pseudocolor monobanda' para aplicar una rampa de color a la elevación.</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/es/latest/lessons/L3/exercise-3-vulcanoes.html' style='color: #2980b9; text-decoration: none;'><b>➤ Ver Ejercicio en el Tutorial</b></a>")
            else:
                self.lbl_ex_title.setText("<b>Übungsaufgabe 5: Vulkane & Rasterdaten</b>")
                self.lbl_ex_desc.setText(f"<div style='{myst_note_style}'><b style='color:#2980b9;'>📝 Szenario</b><br><br>Wir untersuchen Vulkane in Kombination mit topografischen Rasterdaten. Nutzen Sie den Button, um die ZIP-Datei herunterzuladen. Entpacken Sie diese und laden Sie die Daten in QGIS. Passen Sie anschließend die Symbolisierung an.</div>")
                self.lbl_ex_hint.setText(f"<div style='{myst_tip_style}'><b style='color:#16a085;'>💡 Tipp</b><br><br>Sobald das Raster (DEM) geladen ist, gehen Sie in die Symbolisierung und stellen Sie den Darstellungsstil auf 'Einkanalpeudofarbe' um, um ein Höhenprofil farblich darzustellen.</div>")
                self.lbl_ex_link.setText(f"<a href='https://einfuhrung-gis-fur-geowissenschaften.readthedocs.io/de/latest/lessons/L3/exercise-3-vulcanoes.html' style='color: #2980b9; text-decoration: none;'><b>➤ Übung im Tutorial ansehen</b></a>")

    def close_active_tour(self):
        if self.tour_instance:
            try:
                self.tour_instance.close()
            except:
                pass

    def start_ui_tour(self):
        self.close_active_tour()
        self.exercise_frame.setVisible(False)
        steps = get_spotlight_steps(self.iface, self.get_lang_code())
        self.tour_instance = SpotlightTour(steps, self.iface)
        self.tour_instance.show()
        
    def start_interactive_tour(self):
        self.close_active_tour()
        self.exercise_frame.setVisible(False)
        steps = get_interactive_steps(self.iface, self.get_lang_code())
        self.tour_instance = SpotlightTour(steps, self.iface)
        self.tour_instance.show()

    def start_exercise_tour(self, ex_num):
        self.close_active_tour()
        self.current_exercise = ex_num
        self.update_exercise_texts()
        self.lbl_ex_hint.setVisible(False)
        self.exercise_frame.setVisible(True)

    def open_download_link(self):
        url = "https://drive.google.com/file/d/1PgPannrjP2JuDgtKvFBathNstQ-WKmvD/view?usp=sharing"
        webbrowser.open(url)
