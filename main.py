import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint

SCREEN_SIZE = [600, 450]


class MapsAPI(QWidget):
    def __init__(self):
        super().__init__()
        self.getImage()
        self.initUI()

        self.ln = 37.530887
        self.lt = 55.703118
        self.spn = [0.002, 0.002]

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={str(self.ln)},{str(self.lt)}&spn={str(self.spn[0])},{str(self.spn[1])}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            print(1)
        if event.key() == Qt.Key.Key_PageDown:
            print(2)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec())
