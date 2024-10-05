import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMainWindow
from PyQt5.QtGui import QPixmap, QFont, QPalette, QColor, QPainter  # Importar QPainter
from PyQt5.QtCore import Qt
from io import BytesIO
from datetime import datetime, timedelta
from googletrans import Translator

# API Key de la NASA para APOD
API_KEY_NASA = "mOLDlHiTAFgtisXfLuMXfS2BIfMabSYIpRcsd4Ew"

# Inicializar el traductor
translator = Translator()

# Fecha inicial de búsqueda
fecha_actual = datetime.now()

# Función para obtener la imagen APOD de una fecha específica
def obtener_imagen_apod(fecha=None):
    if fecha:
        url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY_NASA}&date={fecha}"
    else:
        url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY_NASA}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['media_type'] == 'image' and ("space" in data['title'].lower() or "universe" in data['title'].lower()):
            return data
    return None

# Función para buscar la imagen espacial, retrocediendo hasta encontrar una
def obtener_imagen_espacial():
    global fecha_actual
    while True:  # Bucle infinito hasta encontrar una imagen espacial
        fecha_str = fecha_actual.strftime('%Y-%m-%d')
        data = obtener_imagen_apod(fecha_str)
        
        if data:
            fecha_actual -= timedelta(days=1)  # Retroceder para la próxima búsqueda
            return data
        
        # Retroceder un día si no hay imagen válida
        fecha_actual -= timedelta(days=1)
    
    return None

# Clase para la ventana de visualización de la imagen
class ImageWindow(QMainWindow):
    def __init__(self, pixmap):
        super().__init__()
        self.setWindowTitle('Imagen en Primer Plano')
        self.setGeometry(200, 100, 800, 600)
        
        # Crear una escena para mostrar la imagen
        self.scene = QGraphicsScene()
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)

        # Crear un QGraphicsView para contener la escena
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        
        # Habilitar las funciones de zoom y desplazamiento
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        # Ajustar el factor de zoom con la rueda del ratón
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.view.scale(zoom_factor, zoom_factor)

# Clase de la aplicación PyQt
class APODApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Imagen Astronómica del Día (APOD)')
        self.setGeometry(100, 100, 800, 600)

        # Establecer colores oscuros
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))  # Fondo gris oscuro
        palette.setColor(QPalette.WindowText, Qt.white)         # Texto blanco
        palette.setColor(QPalette.Button, QColor(20, 20, 20))   # Botones más oscuros
        palette.setColor(QPalette.ButtonText, QColor(138, 43, 226))  # Texto morado en botones
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Título
        self.title = QLabel('Imagen Astronómica del Día')
        self.title.setFont(QFont('Arial', 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Imagen
        self.image_label = QLabel()
        layout.addWidget(self.image_label)

        # Descripción
        self.description = QTextEdit()
        self.description.setReadOnly(True)
        self.description.setFont(QFont('Arial', 10))
        self.description.setStyleSheet("background-color: #333333; color: white;")
        layout.addWidget(self.description)

        # Botón para cargar la imagen
        self.btn_cargar = QPushButton('Cargar Imagen del Día', self)
        self.btn_cargar.setFont(QFont('Arial', 12))
        self.btn_cargar.clicked.connect(self.mostrar_imagen_apod)
        layout.addWidget(self.btn_cargar)

        # Botón para mostrar la siguiente imagen
        self.btn_siguiente = QPushButton('Mostrar Siguiente Imagen Espacial', self)
        self.btn_siguiente.setFont(QFont('Arial', 12))
        self.btn_siguiente.clicked.connect(self.mostrar_siguiente_imagen)
        layout.addWidget(self.btn_siguiente)

        # Botón para visualizar en primer plano
        self.btn_ver_imagen = QPushButton('Ver Imagen en Primer Plano', self)
        self.btn_ver_imagen.setFont(QFont('Arial', 12))
        self.btn_ver_imagen.clicked.connect(self.ver_imagen_en_primer_plano)
        self.btn_ver_imagen.setEnabled(False)  # Desactivar hasta que haya una imagen cargada
        layout.addWidget(self.btn_ver_imagen)

        self.setLayout(layout)

        # Variable para almacenar la imagen descargada
        self.pixmap_actual = None

    def mostrar_imagen_apod(self):
        data = obtener_imagen_espacial()
        self.mostrar_imagen(data)

    def mostrar_siguiente_imagen(self):
        data = obtener_imagen_espacial()
        self.mostrar_imagen(data)

    def mostrar_imagen(self, data):
        if data:
            image_url = data.get('url')
            explanation = data.get('explanation', 'No hay explicación disponible.')
            title = data.get('title', 'Sin título disponible.')

            # Traducir al español
            title_es = translator.translate(title, src='en', dest='es').text
            explanation_es = translator.translate(explanation, src='en', dest='es').text

            self.title.setText(title_es)
            self.description.setPlainText(explanation_es)

            # Descargar y mostrar la imagen
            if image_url:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data.getvalue())
                    self.image_label.setPixmap(pixmap.scaled(700, 400, Qt.KeepAspectRatio))
                    self.pixmap_actual = pixmap
                    self.btn_ver_imagen.setEnabled(True)  # Habilitar el botón de visualización
        else:
            self.title.setText("No se encontró una imagen espacial")
            self.description.setPlainText("No se encontró ninguna imagen espacial en los últimos días.")
            self.btn_ver_imagen.setEnabled(False)  # Desactivar el botón de visualización

    def ver_imagen_en_primer_plano(self):
        if self.pixmap_actual:
            self.ventana_imagen = ImageWindow(self.pixmap_actual)
            self.ventana_imagen.show()

# Ejecutar la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    apod_app = APODApp()
    apod_app.show()
    sys.exit(app.exec_())