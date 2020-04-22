from PyQt5.QtCore import QAbstractListModel, Qt
from PyQt5 import QtGui, QtCore

import math

class CurvesModel(QAbstractListModel):
    def __init__(self, *args, curves=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.curves = curves or []

        self.selected_curve = None
        self.selected_curve_index = None

        # Sample curve
        nodes = [(50, 170), (150, 370), (250, 35), (400, 320)]
        curve = PolygonalCurve('Curve #1', nodes)
        curve.calculate_points()
        
        self.add(curve)

    def add(self, curve):
        self.curves.append(curve)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            curve = self.curves[index.row()]
            return f"{curve.name} | {curve.type} | {len(curve.nodes)} nodes"

    def rowCount(self, parent=None):
        return len(self.curves)

    def select(self, index):
        if self.selected_curve:
            self.selected_curve.selected = False

        self.selected_curve = self.curves[index]
        self.selected_curve.selected = True
        self.selected_curve_index = index

        self.updated()

    def remove_selected(self):
        if self.selected_curve_index is not None:
            self.curves.pop(self.selected_curve_index)
            self.selected_curve = None
            self.selected_curve_index = None
            self.updated()

    def updated(self):
        self.layoutChanged.emit()

class Curve(object):
    def __init__(self, name, nodes=None):
        self.nodes = nodes or []
        self.points = []

        self.name = name
        self.type = "Base Curve"

        self.selected = False

        self.color = QtCore.Qt.blue

    def calculate_points(self):
        raise NotImplementedError

    def draw(self, qp: QtGui.QPainter):
        raise NotImplementedError


class BezierCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Bezier Curve"

    @staticmethod
    def binomial(i, n):
        """Binomial coefficient"""
        return math.factorial(n) / float(math.factorial(i) * math.factorial(n - i))

    @staticmethod
    def bernstein(t, i, n):
        """Bernstein polynom"""
        return BezierCurve.binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))

    @staticmethod
    def bezier(t, nodes):
        """Calculate coordinate of a point in the bezier curve"""
        n = len(nodes) - 1
        x = y = 0
        for i, pos in enumerate(nodes):
            bern = BezierCurve.bernstein(t, i, n)
            x += pos[0] * bern
            y += pos[1] * bern
        return x, y

    @staticmethod
    def bezier_curve_range(n, nodes):
        """Range of points in a curve bezier"""
        for i in range(n):
            t = i / float(n - 1)
            yield BezierCurve.bezier(t, nodes)

    def calculate_points(self):
        steps = 1000

        points = [self.nodes[0]]
        for point in BezierCurve.bezier_curve_range(steps, self.nodes):
            points.append(point)

        self.points = points
        return self.points

    def draw(self, qp: QtGui.QPainter):
        if not self.nodes:
            return

        blackPen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        redPen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        greenPen = QtGui.QPen(QtCore.Qt.green, 1, QtCore.Qt.DashLine)
        redBrush = QtGui.QBrush(QtCore.Qt.red)

        oldPoint = self.nodes[0]

        if self.selected:
            qp.setPen(redPen)
            qp.setBrush(redBrush)
            qp.drawEllipse(oldPoint[0] - 3, oldPoint[1] - 3, 6, 6)

            qp.drawText(oldPoint[0] + 5, oldPoint[1] - 3, '1')
            for i, point in enumerate(self.nodes[1:]):
                i += 2
                qp.setPen(blackPen)
                qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])

                qp.setPen(redPen)
                qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

                qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
                oldPoint = point

        qp.setPen(bluePen)
        for point in self.points:
            qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
            oldPoint = point


class PolygonalCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Polygonal Curve"

    def calculate_points(self):
        self.points = self.nodes
        return self.points

    def draw(self, qp: QtGui.QPainter):
        if not self.nodes:
            return

        blackPen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        bluePen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.SolidLine)
        redPen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        redBrush = QtGui.QBrush(QtCore.Qt.red)

        oldPoint = self.nodes[0]

        if self.selected:
            qp.setPen(redPen)
            qp.setBrush(redBrush)
            qp.drawEllipse(oldPoint[0] - 3, oldPoint[1] - 3, 6, 6)

            qp.drawText(oldPoint[0] + 5, oldPoint[1] - 3, '1')
            for i, point in enumerate(self.nodes[1:]):
                i += 2
                qp.setPen(bluePen)
                qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])

                qp.setPen(redPen)
                qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)

                qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)
                oldPoint = point

        qp.setPen(bluePen)
        oldPoint = self.points[0]
        for point in self.points:
            qp.drawLine(oldPoint[0], oldPoint[1], point[0], point[1])
            oldPoint = point
