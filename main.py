import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt

from math import cos, sqrt
from math import degrees as deg
from math import radians as rad

'''

у нас есть координаты центра по сути и я видел, что есть словарь z: spn;
можно брать текущий спн, и умножать на отношение разницы положения
курсора от центра и ширины всего экрана, также с высотой

lon_point = lon_center + spns[z] * ((center_px - cur_px) / width_px)

Что-то такое было. Я пытался переменные в соответствие назвать


'''


# Определяем функцию, считающую расстояние между двумя точками, заданными координатами
def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = rad((a_lat + b_lat) / 2.)
    lat_lon_factor = cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = sqrt(dx * dx + dy * dy)

    return distance



class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI.ui', self)

        self.setWindowTitle('Отображение карты')
        self.setGeometry(-1000, 100, 0, 0)
        self.setFixedSize(654, 600)

        self.searchInput.setText("")

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        self.ln = 0  # долгота
        self.ln = 37.531684
        self.lt = 0  # широта
        self.lt = 55.703434
        self.z = 13
        self.l = 'map'
        # self.mark = None
        self.marks = [
            [self.ln, self.lt]
        ]

        self.searchBtn.clicked.connect(self.search)
        self.resetBtn.clicked.connect(self.reset)
        self.checkBox.stateChanged.connect(self.toggle_postal_code)

        self.address = None
        self.postal_code = None

        self.getImage()
        self.loadImage()

    def getImage(self):

        params = {
            'll': f'{str(self.ln)},{str(self.lt)}',
            'z': f'{self.z}',
            'l': f'{self.l}',
            'size': '400,400',
        }

        if self.marks:
            m_list = []
            # m_d = [
            #     [0, 0],
            #     [-1, 1],
            #     [1, 1],
            #     [1, -1],
            #     [-1, -1],
            # ]

            # ln долгота (x)
            # lt широта (y)
            k = cos(rad(self.lt))

            for m in self.marks:
                m_list.append(f'{m[0]},{m[1]},pm2dgl')
                # m_list.append(f'{m[0]},{m[1]},pm2rdm,ASD')
                # for dln, dlt in m_d:
                #     dln *= 1.1
                #     dlt *= 1.1
                #
                #     ln, lt = m[0] + (dln), m[1] + (dlt * k)
                #     m_list.append(f'{ln},{lt},pm2dgl')

            params['pt'] = '~'.join(m_list)
            # print('~'.join(m_list))

        map_request = f"http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_request, params=params)
        # print(response.url)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def loadImage(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.search()
            return

        if event.key() == Qt.Key_Right:
            self.ln += 0.001 * ((19 - self.z) / 2) ** 2
        elif event.key() == Qt.Key_Left:
            self.ln -= 0.001 * ((19 - self.z) / 2) ** 2
        elif event.key() == Qt.Key_Up:
            self.lt += 0.001 * ((19 - self.z) / 2) ** 2
        elif event.key() == Qt.Key_Down:
            self.lt -= 0.001 * ((19 - self.z) / 2) ** 2

        if event.key() == Qt.Key.Key_PageUp:
            if self.z < 18:
                self.z += 1

        if event.key() == Qt.Key.Key_PageDown:
            if self.z > 8:
                self.z -= 1

        print(self.z)

        if event.key() == Qt.Key.Key_F1:
            self.l = 'map'
        if event.key() == Qt.Key.Key_F2:
            self.l = 'sat'
        if event.key() == Qt.Key.Key_F3:
            self.l = 'skl'

        self.loadImage()

    # def _mousePressEvent(self, e: QMouseEvent) -> None:
    #     pos = (e.pos().x(), e.pos().y())
    #     rect_size = self.label.size()
    #     rect_pos = self.label.pos()
    #     rect = (rect_pos.x(), rect_pos.y(), rect_size.width(), rect_size.height())
    #     if (not rectPointIntersect(rect, pos)):
    #         return
    #     x = pos[0] - rect[0]
    #     y = pos[1] - rect[1]
    #     map_w = 0.0045 * 2 ** (17 - self.z)
    #     map_h = 0.0025 * 2 ** (17 - self.z)
    #     rel_x = map_w / rect[2]
    #     rel_y = -map_h / rect[3]
    #     point = (
    #         self.ll[0] + rel_x * x - map_w / 2,
    #         self.ll[1] + rel_y * y + map_h / 2,
    #     )
    #     if (e.button() == Qt.MouseButton.LeftButton):
    #         self.search(point)

    def mousePressEvent(self, event):
        if self.searchInput.text().strip() == "":
            self.statusBar().showMessage("Введите объект, который надо найти в поисковую строку", 5000)
            return

        x = event.pos().x()
        y = event.pos().y()

        x -= self.image.x()
        y -= self.image.y()

        if x < 0 or x > 400 or y < 0 or y > 400:
            self.statusBar().showMessage("Ткни на карту", 5000)
            return

        # dx = x - 200
        # dy = y - 200

        dy = 200 - y
        dx = x - 200

        ln = self.ln + dx * 0.0000428 * 2 ** (15 - self.z)
        lt = self.lt + dy * 0.0000428 * cos(rad(self.lt)) * 2 ** (15 - self.z)

        if ln > 180:
            ln -= 360
        elif ln < -180:
            ln += 360

        # dx = dx / 400 * 2  # * 1.02
        # dy = dy / 400 * 2  # * 1.02
        #
        # k = cos(rad(self.lt))
        # ln = self.ln + dx * cos(rad(self.ln))
        # lt = self.lt - dy * k

        print("-----------------------", ln, lt)

        # print(37.5316, round(ln, 4))
        # print(55.7034, round(lt, 4))
        if event.button() == Qt.LeftButton:
            self.marks = [[ln, lt]]

            geo_search_api_server = "https://search-maps.yandex.ru/v1/"
            geo_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

            geo_search_params = {
                "apikey": geo_api_key,
                "text": self.searchInput.text(),
                "lang": "ru_RU",
                "ll": f"{ln},{lt}",
                "type": "geo"
            }

            geo_response = requests.get(geo_search_api_server, params=geo_search_params)
            print(geo_response.url)

            geo_json_response = geo_response.json()
            if len(geo_json_response["features"]) > 0:
                search = geo_json_response["features"][0]["properties"]["GeocoderMetaData"]["text"]

                params = {
                    'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                    'geocode': search,
                    'format': 'json',
                }

                geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
                response = requests.get(geocoder_request, params=params)

                json_response = response.json()

                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

                self.address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]

                if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
                    self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                else:
                    self.postal_code = "(нет почтового индекса)"

                if self.checkBox.isChecked():
                    full_address = self.postal_code + " " + self.address
                else:
                    full_address = self.address

                self.fullAddress.setText(full_address)
            else:
                self.statusBar().showMessage("Здесь нечего не нашлось")
            # Получаем первую найденную организацию.

            self.loadImage()

        elif event.button() == Qt.RightButton:
            self.marks = [[ln, lt]]

            geo_search_api_server = "https://search-maps.yandex.ru/v1/"
            geo_api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

            geo_search_params = {
                "apikey": geo_api_key,
                "text": self.searchInput.text(),
                "lang": "ru_RU",
                "ll": f"{ln},{lt}",
                "type": "biz"
            }

            geo_response = requests.get(geo_search_api_server, params=geo_search_params)

            geo_json_response = geo_response.json()
            if len(geo_json_response["features"]) > 0:
                search = geo_json_response["features"][0]["properties"]["description"]
                print(search)

                params = {
                    'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                    'geocode': search,
                    'format': 'json',
                }

                geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
                response = requests.get(geocoder_request, params=params)

                json_response = response.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_coordinates = toponym["Point"]["pos"]
                print(f'toponym_coordinates: {toponym_coordinates}')

                coords = list(map(float, toponym_coordinates.split(' ')))
                print(lonlat_distance((ln, lt), coords))
                if lonlat_distance((ln, lt), coords) <= 50:

                    self.address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]

                    if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
                        self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                    else:
                        self.postal_code = "(нет почтового индекса)"

                    if self.checkBox.isChecked():
                        full_address = self.postal_code + " " + self.address
                    else:
                        full_address = self.address

                    self.fullAddress.setText(full_address)
                else:
                    self.statusBar().showMessage("В радиусе 50 метров нечего не нашлось", 5000)
            else:
                self.statusBar().showMessage("Здесь нечего не нашлось")

            # Получаем первую найденную организацию.

            self.loadImage()

    # def mousePressEvent(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #
    #     x -= self.image.x()
    #     y -= self.image.y()
    #
    #     if x < 0 or x > 400 or y < 0 or y > 400:
    #         self.statusBar().showMessage("Ткни на карту", 5000)
    #         return
    #
    #     map_w = 0.0045 * 2 ** (17 - self.z)
    #     map_h = 0.0025 * 2 ** (17 - self.z)
    #     rel_x = map_w / 400
    #     rel_y = -map_h / 400
    #     self.marks.append((
    #         self.ln + rel_x * x - map_w / 2,
    #         self.lt + rel_y * y + map_h / 2,
    #     ))
    #
    #
    #     # print(37.5316, round(ln, 4))
    #     # print(55.7034, round(lt, 4))
    #     # if event.button() == Qt.LeftButton:
    #     #     self.marks.append([ln, lt])
    #     #     self.loadImage()
    #     self.loadImage()
    #
    #     if event.button() == Qt.RightButton:
    #         print(2)

    def search(self):
        print('search')

        if self.searchInput.text().strip() == "":
            self.statusBar().showMessage("В поисковой строке пусто", 5000)
            return

        params = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'geocode': self.searchInput.text(),
            'format': 'json',
        }

        geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
        response = requests.get(geocoder_request, params=params)

        if not response:
            # print("Ошибка выполнения запроса:")
            # print("Http статус:", response.status_code, "(", response.reason, ")")
            self.statusBar().showMessage("Нечего не нашлось", 5000)
            return

        json_response = response.json()

        print(response.url)

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]


        self.address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]

        if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
            self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        else:
            self.postal_code = "(нет почтового индекса)"

        if self.checkBox.isChecked():
            full_address = self.postal_code + " " + self.address
        else:
            full_address = self.address

        self.fullAddress.setText(full_address)

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coordinates = toponym["Point"]["pos"]
        print(f'toponym_coordinates: {toponym_coordinates}')

        coords = list(map(float, toponym_coordinates.split(' ')))

        self.ln = coords[0]
        self.lt = coords[1]
        self.marks = [
            [self.ln, self.lt]
        ]

        self.searchInput.setText("")

        self.loadImage()

    def toggle_postal_code(self):
        if self.address:
            if self.checkBox.isChecked():
                full_address = self.postal_code + " " + self.address
            else:
                full_address = self.address
            self.fullAddress.setText(full_address)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        painter.drawLine(0, int(400 / 2 + self.image.y()), self.width(), int(400 / 2 + self.image.y()))
        painter.drawLine(int(self.width() / 2), 0, int(self.width() / 2), self.height())

    def reset(self):
        print('reset')

        self.searchInput.setText('')
        self.marks = []

        self.loadImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())

[
    {
        'type': 'Feature',
        'geometry':
            {
                'type': 'Point',
                'coordinates': [37.621202, 55.753544]
            },
        'properties':
            {
                'name': 'Красная площадь',
                'description': 'Москва, Россия',
                'boundedBy': [[37.618013, 55.751928], [37.62387, 55.755221]],
                'uri': 'ymapsbm1://geo?data=CgoxNTIwNjMzMDI1EjnQoNC-0YHRgdC40Y8sINCc0L7RgdC60LLQsCwg0JrRgNCw0YHQvdCw0Y8g0L_Qu9C-0YnQsNC00YwiCg0dfBZCFaIDX0I,',
                'GeocoderMetaData': {
                    'precision': 'street',
                    'text': 'Россия, Москва, Красная площадь',
                    'kind': 'street'
                }
            }
    },
    {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [37.475073, 55.879617]}, 'properties': {'name': 'ландшафтный заказник Химкинский', 'description': 'Москва, Россия', 'boundedBy': [[37.461391, 55.873077], [37.48252, 55.884423]], 'uri': 'ymapsbm1://geo?data=CgoyNDUxNjM5MTk4EljQoNC-0YHRgdC40Y8sINCc0L7RgdC60LLQsCwg0LvQsNC90LTRiNCw0YTRgtC90YvQuSDQt9Cw0LrQsNC30L3QuNC6INCl0LjQvNC60LjQvdGB0LrQuNC5IgoNeeYVQhW7hF9C', 'GeocoderMetaData': {'precision': 'other', 'text': 'Россия, Москва, ландшафтный заказник Химкинский', 'kind': 'vegetation'}}}, {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [37.474911, 55.561629]}, 'properties': {'name': 'территория 11-й объект', 'description': 'посёлок Коммунарка, Москва, Россия', 'boundedBy': [[37.472575, 55.559593], [37.484945, 55.564938]], 'uri': 'ymapsbm1://geo?data=Cgo0MDUwMDUxMTA4EmjQoNC-0YHRgdC40Y8sINCc0L7RgdC60LLQsCwg0L_QvtGB0ZHQu9C-0Log0JrQvtC80LzRg9C90LDRgNC60LAsINGC0LXRgNGA0LjRgtC-0YDQuNGPIDExLdC5INC-0LHRitC10LrRgiIKDU_mFUIVGz9eQg,,', 'GeocoderMetaData': {'precision': 'other', 'text': 'Россия, Москва, посёлок Коммунарка, территория 11-й объект', 'kind': 'district'}}}]
