import qgis.utils
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QDockWidget, QFrame, QApplication, QMessageBox, QToolBar
from qgis.PyQt.QtGui import QPainter, QColor, QPainterPath, QRegion
from qgis.PyQt.QtCore import Qt, QRect, QPoint, QRectF, QTimer

class SpotlightTour(QWidget):
    def __init__(self, steps, iface):
        super().__init__(iface.mainWindow())
        self.steps = steps
        self.current_step = 0
        self.iface = iface
        self.interactive_mode = False
        self.layer_added_flag = False
        
        QgsProject.instance().layersAdded.connect(self.on_layer_added)
        
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        main_window = self.iface.mainWindow()
        self.setGeometry(0, 0, main_window.width(), main_window.height())
        
        self.close_btn = QPushButton("Tour beenden", self)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white; 
                font-weight: bold; 
                padding: 8px 15px; 
                border-radius: 4px; 
                border: 2px solid #c0392b;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.move(self.width() - self.close_btn.width() - 30, 30)
        
        self.bubble = QFrame(self)
        self.bubble.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel { font-size: 14px; color: #333333; margin-bottom: 10px; }
            QPushButton { 
                font-size: 13px; font-weight: bold; padding: 8px; 
                background-color: #3498db; color: white; 
                border: none; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        layout = QVBoxLayout(self.bubble)
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setFixedWidth(280)
        layout.addWidget(self.text_label)
        
        self.next_btn = QPushButton("Weiter")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_step)
        layout.addWidget(self.next_btn)
        
        self.target_rect = QRect()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_conditions)
        
        self.show_step()

    def on_layer_added(self, layers):
        self.layer_added_flag = True

    def resizeEvent(self, event):
        self.close_btn.move(self.width() - self.close_btn.width() - 30, 30)
        super().resizeEvent(event)

    def next_step(self):
        self.current_step += 1
        if self.current_step >= len(self.steps):
            self.close()
        else:
            self.show_step()

    def update_mask(self):
        region = QRegion(self.bubble.geometry())
        region = region.united(QRegion(self.close_btn.geometry()))
        self.setMask(region)

    def show_step(self):
        step = self.steps[self.current_step]
        target_widget = step.get('widget')
        text = step['text']
        self.interactive_mode = step.get('interactive', False)
        
        self.text_label.setText(text)
        self.next_btn.setText(step.get('btn_next', 'Weiter'))
        self.close_btn.setText(step.get('btn_end_tour', 'Tour beenden'))
        if self.current_step == len(self.steps) - 1 and not self.interactive_mode:
            self.next_btn.setText(step.get('btn_end', 'Beenden'))
            
        if self.interactive_mode:
            self.next_btn.hide()
        else:
            self.next_btn.show()
            
        self.bubble.adjustSize()
        
        if self.interactive_mode:
            bubble_x = (self.width() - self.bubble.width()) // 2
            bubble_y = max(50, (self.height() - self.bubble.height()) // 3)
            self.bubble.move(bubble_x, bubble_y)
            
            self.target_rect = QRect()
            
            self.update_mask()
            self.timer.start(1000)
        else:
            self.timer.stop()
            self.clearMask()
            
            if target_widget and target_widget.isVisible():
                global_pos = target_widget.mapToGlobal(QPoint(0,0))
                local_pos = self.mapFromGlobal(global_pos)
                self.target_rect = QRect(local_pos, target_widget.size())
                
                bubble_x = self.target_rect.right() + 20
                bubble_y = self.target_rect.top() + 20
                
                if bubble_x + self.bubble.width() > self.width():
                    bubble_x = self.target_rect.left() - self.bubble.width() - 20
                
                if bubble_x < 0:
                    bubble_x = (self.width() - self.bubble.width()) // 2
                    if self.target_rect.center().y() < self.height() // 2:
                        bubble_y = self.target_rect.bottom() + 20
                    else:
                        bubble_y = self.target_rect.top() - self.bubble.height() - 20
                        
                if bubble_y + self.bubble.height() > self.height():
                    bubble_y = self.height() - self.bubble.height() - 20
                if bubble_y < 0:
                    bubble_y = 20
                    
                self.bubble.move(bubble_x, bubble_y)
            else:
                self.target_rect = QRect()
                self.bubble.move((self.width() - self.bubble.width()) // 2, 
                                 (self.height() - self.bubble.height()) // 2)

        self.update()

    def check_conditions(self):
        step = self.steps[self.current_step]
        cond_func = step.get('condition_check')
        
        if cond_func and cond_func(self):
            self.timer.stop()
            if self.current_step == len(self.steps) - 1:
                msg = step.get('success_msg', "Erfolg!")
                title = step.get('success_title', "Glückwunsch!")
                QMessageBox.information(self.iface.mainWindow(), title, msg)
                self.close()
            else:
                self.next_step()

    def paintEvent(self, event):
        if self.interactive_mode:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRect(0, 0, self.width(), self.height())
        
        if not self.target_rect.isNull():
            cutout = QPainterPath()
            rect = self.target_rect.adjusted(-4, -4, 4, 4)
            cutout.addRoundedRect(QRectF(rect), 8, 8)
            path = path.subtracted(cutout)
            
        painter.fillPath(path, QColor(0, 0, 0, 160))
        painter.end()

    def closeEvent(self, event):
        self.timer.stop()
        try:
            QgsProject.instance().layersAdded.disconnect(self.on_layer_added)
        except:
            pass
        super().closeEvent(event)


def is_plugin_manager_open(tour):
    for w in QApplication.topLevelWidgets():
        if w.objectName() == "QgsPluginManager" and w.isVisible():
            return True
    return False

def is_qms_installed_and_closed(tour):
    installed = "quick_map_services" in qgis.utils.plugins
    manager_closed = not is_plugin_manager_open(tour)
    return installed and manager_closed

def check_layer_added(tour):
    return tour.layer_added_flag


def get_texts(lang):
    texts = {
        "de": {
            "menu": "1. Die Menüleiste\n\nHier finden Sie Zugriff auf alle Funktionen von QGIS, aufgeteilt in Standardmenüs wie Projekt, Bearbeiten, Ansicht, Layer etc.",
            "toolbars": "2. Werkzeugleisten\n\nDiese Leisten bieten Schnellzugriff auf die wichtigsten Funktionen. Sie können frei verschoben oder über einen Rechtsklick ein-/ausgeblendet werden.",
            "browser": "3. Bedienfelder: Der Browser\n\nIhr Dateimanager für Geodaten. Ziehen Sie Dateien einfach per Drag & Drop in das Kartenfenster.",
            "layers": "4. Bedienfelder: Das Layer-Bedienfeld\n\nHier steuern Sie, welche Daten sichtbar sind. Mit den Häkchen schalten Sie Ebenen ein und aus. Die obere Ebene verdeckt die darunterliegende.",
            "canvas": "5. Die Kartenansicht\n\nHier findet die Magie statt! Alle Ihre Geodaten werden in diesem zentralen Fenster visuell als eigentliche Karte dargestellt.",
            "dock": "6. Plugin- & Analyse-Fenster\n\nHier werden die Fenster von Plugins (wie dieser Assistent) oder bspw. auch die Verarbeitungswerkzeugkiste geöffnet.",
            "statusbar": "7. Die Statusleiste\n\nHier unten finden Sie wichtige Projektinfos: die Locator-Suchleiste (links), den Maßstab, die Maus-Koordinaten und rechts die Projektion (KBS).",
            "open_plugin_manager": "<b>📍 INTERAKTIVE AUFGABE</b><br><br>Bitte klicken Sie nun oben im Hauptmenü auf <b>Erweiterungen</b> > <b>Erweiterungen verwalten und installieren...</b>",
            "install_qms": "<b>📍 INTERAKTIVE AUFGABE</b><br><br>Suchen Sie im neuen Fenster nach <b>QuickMapServices</b>.<br>Klicken Sie auf <b>Erweiterung installieren</b> und schließen Sie das Fenster danach.",
            "add_basemap": "<b>📍 INTERAKTIVE AUFGABE</b><br><br>Klicken Sie nun im Hauptmenü auf <b>Web</b> > <b>QuickMapServices</b> und wählen Sie eine Karte (z.B. OSM Standard) aus.",
            "success_title": "Glückwunsch!",
            "success": "Sie haben erfolgreich ein Plugin installiert und eine Hintergrundkarte zum Projekt hinzugefügt.",
            "next": "Weiter",
            "end": "Tour beenden",
            "end_tour_btn": "Tour abbrechen"
        },
        "en": {
            "menu": "1. Menu Bar\n\nProvides access to all QGIS features using standard hierarchical menus like Project, Edit, View, Layer, etc.",
            "toolbars": "2. Toolbars\n\nProvide quick access to most of the same functions as the menus. They can be moved around or toggled via right-click.",
            "browser": "3. Panels: Browser\n\nYour file manager for spatial data. Drag & drop files directly into the Map Canvas.",
            "layers": "4. Panels: Layers\n\nControl which data is visible. Use the checkboxes to toggle visibility. Top layers cover the ones below.",
            "canvas": "5. Map View\n\nThis is where the magic happens! All your spatial data are visually displayed here as the actual map.",
            "dock": "6. Plugin & Analysis Panels\n\nHere you will find windows opened by plugins (like this Assistant) or, for example, the Processing Toolbox.",
            "statusbar": "7. Status Bar\n\nDown here you can see the Locator bar, current map scale, coordinates, and the Coordinate Reference System (CRS) of your project.",
            "open_plugin_manager": "<b>📍 INTERACTIVE TASK</b><br><br>Please click on <b>Plugins</b> > <b>Manage and Install Plugins...</b> in the main menu.",
            "install_qms": "<b>📍 INTERACTIVE TASK</b><br><br>Search for <b>QuickMapServices</b> in the Plugin Manager.<br>Click install and close the window afterwards.",
            "add_basemap": "<b>📍 INTERACTIVE TASK</b><br><br>Now click on <b>Web</b> > <b>QuickMapServices</b> in the main menu and select a basemap (e.g. OSM Standard) to add it.",
            "success_title": "Congratulations!",
            "success": "You have installed a plugin and added a basemap to your project.",
            "next": "Next",
            "end": "Finish Tour",
            "end_tour_btn": "Cancel Tour"
        },
        "es": {
            "menu": "1. Barra de Menú\n\nProporciona acceso a todas las funciones mediante menús jerárquicos como Proyecto, Edición, Ver, etc.",
            "toolbars": "2. Barras de Herramientas\n\nAcceso rápido a las funciones más utilizadas. Se pueden mover o activar/desactivar con clic derecho.",
            "browser": "3. Paneles: Navegador\n\nSu administrador de archivos de datos espaciales. Arrastre archivos al lienzo del mapa.",
            "layers": "4. Paneles: Capas\n\nControle qué datos son visibles. La capa superior cubre las inferiores.",
            "canvas": "5. Vista del Mapa\n\n¡Aquí ocurre la magia! Todos sus datos espaciales se muestran visualmente aquí.",
            "dock": "6. Paneles de Complementos\n\nAquí se abren las ventanas de los complementos (como este Asistente) o, por ejemplo, la Caja de herramientas de procesos.",
            "statusbar": "7. Barra de Estado\n\nAquí encontrará la barra localizadora, la escala, las coordenadas y el SRC del proyecto.",
            "open_plugin_manager": "<b>📍 TAREA INTERACTIVA</b><br><br>Haga clic en <b>Complementos</b> > <b>Administrar e instalar complementos...</b> en el menú principal.",
            "install_qms": "<b>📍 TAREA INTERACTIVA</b><br><br>Busque <b>QuickMapServices</b> en el Administrador.<br>Instálelo y cierre la ventana.",
            "add_basemap": "<b>📍 TAREA INTERACTIVA</b><br><br>Ahora haga clic en <b>Web</b> > <b>QuickMapServices</b> en el menú principal y elija un mapa base (ej. OSM Standard).",
            "success_title": "¡Felicidades!",
            "success": "Ha instalado un complemento y agregado un mapa base a su proyecto.",
            "next": "Siguiente",
            "end": "Terminar Tour",
            "end_tour_btn": "Cancelar Tour"
        }
    }
    return texts.get(lang, texts["de"])


def get_spotlight_steps(iface, lang):
    t = get_texts(lang)
    main_window = iface.mainWindow()
    
    menu_bar = main_window.menuBar()
    
    toolbar = iface.mapNavToolToolBar()
    if not toolbar or not toolbar.isVisible():
        for tb in main_window.findChildren(QToolBar):
            if tb.isVisible():
                toolbar = tb
                break
                
    browser_panel = main_window.findChild(QDockWidget, "Browser")
    layers_panel = main_window.findChild(QDockWidget, "Layers")
    map_canvas = iface.mapCanvas()
    # Das Panel des QGIS Lern-Assistenten suchen (mithilfe des oben definierten objectName)
    dock_panel = main_window.findChild(QDockWidget, "QgisTourDockWidget")
    status_bar = main_window.statusBar()

    steps = [
        {"widget": menu_bar, "text": t["menu"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]}
    ]
    
    if toolbar:
        steps.append({"widget": toolbar, "text": t["toolbars"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]})
        
    steps.extend([
        {"widget": browser_panel, "text": t["browser"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]},
        {"widget": layers_panel, "text": t["layers"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]},
        {"widget": map_canvas, "text": t["canvas"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]}
    ])
    
    # Füge das Plugin-Fenster als Schritt 6 hinzu, wenn es geöffnet ist
    if dock_panel and dock_panel.isVisible():
        steps.append({"widget": dock_panel, "text": t["dock"], "btn_next": t["next"], "btn_end_tour": t["end_tour_btn"]})
        
    # Statusleiste ist nun Schritt 7
    steps.append({"widget": status_bar, "text": t["statusbar"], "btn_next": t["end"], "btn_end_tour": t["end_tour_btn"]})

    return steps

def get_interactive_steps(iface, lang):
    t = get_texts(lang)
    steps = []
    
    if "quick_map_services" not in qgis.utils.plugins:
        steps.append({
            "interactive": True,
            "text": t["open_plugin_manager"],
            "condition_check": is_plugin_manager_open,
            "btn_end_tour": t["end_tour_btn"]
        })
        steps.append({
            "interactive": True,
            "text": t["install_qms"],
            "condition_check": is_qms_installed_and_closed,
            "btn_end_tour": t["end_tour_btn"]
        })
        
    steps.append({
        "interactive": True,
        "text": t["add_basemap"],
        "condition_check": check_layer_added,
        "success_msg": t["success"],
        "success_title": t["success_title"],
        "btn_end_tour": t["end_tour_btn"]
    })
    return steps
