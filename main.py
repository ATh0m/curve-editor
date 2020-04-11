import math
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from MainWindow import Ui_MainWindow

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

class PointsModel(QtCore.QAbstractListModel):
    def __init__(self, *args, points=None, **kwargs):
        super(PointsModel, self).__init__(*args, **kwargs)
        self.points = points or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the data structure.
            x, y = self.points[index.row()]
            # Return the todo text only.
            return f"({x}, {y})"

    def rowCount(self, index):
        return len(self.points)

class Canvas(QtWidgets.QLabel):

    def __init__(self, points):
        super().__init__()
        self.points = points

        pixmap = QtGui.QPixmap(800, 500)
        pixmap.fill(Qt.white)
        self.setPixmap(pixmap)

        self.draw_something()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        x, y = ev.x(), ev.y()
        print(x, y)

        self.points.points.append((x, y))
        self.points.layoutChanged.emit()

    def draw_something(self):
        qp = QtGui.QPainter(self.pixmap())

        blackPen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        redPen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        greenPen = QtGui.QPen(QtCore.Qt.green, 1, QtCore.Qt.DashLine)
        redBrush = QtGui.QBrush(QtCore.Qt.red)

        steps = 1000
        controlPoints = (
            (50, 170),
            (150, 370),
            (250, 35),
            (400, 320))
        oldPoint = controlPoints[0]

        qp.setPen(redPen)
        qp.setBrush(redBrush)
        qp.drawEllipse(oldPoint[0] - 3, oldPoint[1] - 3, 6, 6)

        qp.drawText(oldPoint[0] + 5, oldPoint[1] - 3, '1')
        for i, point in enumerate(controlPoints[1:]):
            i += 2
            qp.setPen(blackPen)
            qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])

            qp.setPen(redPen)
            qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

            qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
            oldPoint = point

        qp.setPen(bluePen)
        for point in bezier_curve_range(steps, controlPoints):
            qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
            oldPoint = point

        qp.end()


data = [
    ("Alice", [
        ("Keys", []),
        ("Purse", [
            ("Cellphone", [])
        ])
    ]),
    ("Bob", [
        ("Wallet", [
            ("Credit card", []),
            ("Money", [])
        ])
    ])
]

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.model = PointsModel(points=[(100, 200)])
        # self.listView.setModel(self.model)

        self.model = QtGui.QStandardItemModel()
        self.addItems(self.model, data)
        self.treeView.setModel(self.model)

        self.canvas = Canvas(self.model)
        self.layout.addWidget(self.canvas)

    def addItems(self, parent, elements):
        for text, children in elements:
            item = QtGui.QStandardItem(text)
            parent.appendRow(item)
            if children:
                self.addItems(item, children)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()