import math

from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QRectF, Qt, QUrl
from PyQt5.QtGui import QColor, QGuiApplication, QPainter, QPen, QBrush
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickPaintedItem, QQuickView

def binomial(i, n):
    """Binomial coefficient"""
    return math.factorial(n) / float(
        math.factorial(i) * math.factorial(n - i))


def bernstein(t, i, n):
    """Bernstein polynom"""
    return binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))


def bezier(t, points):
    """Calculate coordinate of a point in the bezier curve"""
    n = len(points) - 1
    x = y = 0
    for i, pos in enumerate(points):
        bern = bernstein(t, i, n)
        x += pos[0] * bern
        y += pos[1] * bern
    return x, y


def bezier_curve_range(n, points):
    """Range of points in a curve bezier"""
    for i in range(n):
        t = i / float(n - 1)
        yield bezier(t, points)

class PieChart(QQuickPaintedItem):

    chartCleared = pyqtSignal()  # 定义信号

    @pyqtProperty(str)
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = QColor(color)

    def __init__(self, parent=None):
        super(PieChart, self).__init__(parent)

        self._name = ''
        self._color = QColor()

    def paint(self, painter):
        # painter.setPen(QPen(self._color, 2))
        painter.setRenderHints(QPainter.Antialiasing, True)
        #
        # rect = QRectF(0, 0, self.width(), self.height()).adjusted(1, 1, -1, -1)
        # painter.drawPie(rect, 90 * 16, 290 * 16)

        blackPen = QPen(Qt.black, 1, Qt.DashLine)
        redPen = QPen(Qt.red, 1, Qt.DashLine)
        bluePen = QPen(Qt.blue, 1, Qt.DashLine)
        greenPen = QPen(Qt.green, 1, Qt.DashLine)
        redBrush = QBrush(Qt.red)

        steps = 1000
        controlPoints = (
            (50, 170),
            (150, 370),
            (250, 35),
            (400, 320))
        oldPoint = controlPoints[0]

        painter.setPen(redPen)
        painter.setBrush(redBrush)
        painter.drawEllipse(oldPoint[0] - 3, oldPoint[1] - 3, 6, 6)

        painter.drawText(oldPoint[0] + 5, oldPoint[1] - 3, '1')
        for i, point in enumerate(controlPoints[1:]):
            i += 2
            painter.setPen(blackPen)
            painter.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])

            painter.setPen(redPen)
            painter.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

            painter.drawText(point[0] + 5, point[1] - 3, '%d' % i)
            oldPoint = point

        painter.setPen(bluePen)
        for point in bezier_curve_range(steps, controlPoints):
            painter.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
            oldPoint = point



    @pyqtSlot()
    def clearChart(self):
        self.color = QColor(Qt.transparent)
        self.update()

        self.chartCleared.emit()  # 发射信号


if __name__ == '__main__':
    import os
    import sys

    app = QGuiApplication(sys.argv)

    qmlRegisterType(PieChart, "Charts", 1, 0, "PieChart")

    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(
        QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__), 'src/qml/main.qml')))
    view.show()

    sys.exit(app.exec_())