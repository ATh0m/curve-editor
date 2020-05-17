import logging

logger = logging.getLogger('curve-editor')

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt

from .model import CurvesModel


class Canvas(QtWidgets.QGraphicsPixmapItem):
    """ Canvas for drawing"""

    def __init__(self):
        super().__init__(QtGui.QPixmap(930, 690))
        self.model: CurvesModel = None

    def setModel(self, model):
        self.model: CurvesModel = model
        self.model.layoutChanged.connect(self.draw)

    def mousePressEvent(self, event) -> None:
        self.model.state.mousePressEvent(event, self)

    def mouseMoveEvent(self, event) -> None:
        self.model.state.mouseMoveEvent(event, self)

    def mouseReleaseEvent(self, event) -> None:
        self.model.state.mouseReleaseEvent(event, self)

    def draw(self):
        pixmap = QtGui.QPixmap(930, 690)
        pixmap.fill(Qt.white)

        qp = QtGui.QPainter(pixmap)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)

        for curve in self.model.curves:
            curve.draw(qp)

        qp.end()
        self.setPixmap(pixmap)
        logger.info('Updated')

    def screenshot(self, filename):
        self.pixmap().save(filename)

        logger.info('OK')
