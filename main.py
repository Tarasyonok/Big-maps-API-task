import os
import sys


import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QPoint

SCREEN_SIZE = [600, 450]


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)

        self.ln = 37.530887
        self.lt = 55.703118
        self.spn = [0.002, 0.002]
        self.idx = 0
        self.l = 'map'
        self.mark = None
        self.mark = [self.ln, self.lt]

        self.searchBtn.clicked.connect(self.search)
        self.resetBtn.clicked.connect(self.reset)

        self.getImage()
        self.initUI()

    def getImage(self):
        url_mark = ''
        if self.mark:
            url_mark = f'&pt={self.mark[0]},{self.mark[1]}'

        params = {
            'll': f'{str(self.ln)},{str(self.lt)}',
            'spn': f'{str(self.spn[0])},{str(self.spn[1])}',
            'l': f'{self.l}',
            'pt': f'{self.mark[0]},{self.mark[1]}',
        }
        map_request = f"http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_request, params=params)

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
        # self.image = QLabel(self)
        # self.image.move(0, 0)
        # self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            if self.idx <= 5:
                self.idx += 1

                self.spn[0] *= 2
                self.spn[1] *= 2
        if event.key() == Qt.Key.Key_PageDown:
            if self.idx >= -5:
                self.idx -= 1

                self.spn[0] /= 2
                self.spn[1] /= 2
        if event.key() == Qt.Key.Key_Up:
            self.lt += 0.001
        if event.key() == Qt.Key.Key_Down:
            self.lt -= 0.001
        if event.key() == Qt.Key.Key_Left:
            self.ln -= 0.001
        if event.key() == Qt.Key.Key_Right:
            self.ln += 0.001

        if event.key() == Qt.Key.Key_F1:
            self.l = 'map'
        if event.key() == Qt.Key.Key_F2:
            self.l = 'sat'
        if event.key() == Qt.Key.Key_F3:
            self.l = 'skl'

        self.spn[0] = round(self.spn[0], 6)
        self.spn[1] = round(self.spn[1], 6)

        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def search(self):
        print('search')


    def reset(self):
        print('reset')

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec())
