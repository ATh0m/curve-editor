from PyQt5 import QtGui, QtCore

from .curves import Curve


class PolygonalCurve(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Polygonal Curve"

    def calculate_points(self):
        self.points = self.nodes
        return self.points

    def draw(self, qp: QtGui.QPainter):
        if self.hidden or not self.nodes: return

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
