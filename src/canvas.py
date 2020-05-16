import logging
logger = logging.getLogger('curve-editor')

import math
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from .model import CurvesModel
from .states import SelectCurveState, DefaultState, AddPointState, MovePointState


class Canvas(QtWidgets.QGraphicsPixmapItem):
    """ Canvas for drawing"""
    def __init__(self):
        super().__init__(QtGui.QPixmap(930, 690))
        self.model: CurvesModel = None

    def setModel(self, model):
        self.model: CurvesModel = model
        self.model.layoutChanged.connect(self.draw)

    def mousePressEvent(self, ev) -> None:
        x, y = ev.pos().x(), ev.pos().y()

        logger.info(f"START: ({x}, {y})")

        if isinstance(self.model.state, SelectCurveState):
            logger.info('selecting')

            index, dist = self.model.distance_to_nearest_curve(x, y)
            logger.info(index, dist)
            if dist is not None and dist < 10:
                self.model.select(index)
                logger.info(f'Selected curve: {index}')
            else:
                self.model.deselect()

            self.model.state = self.model.state.nextState()

        elif isinstance(self.model.state, AddPointState):
            curve = self.model.state.curve
            curve.nodes.append((x, y))
            curve.calculate_points()

            self.model.layoutChanged.emit()

        elif isinstance(self.model.state, MovePointState):
            curve = self.model.state.curve
            
            index, dist = curve.nearest_node(x, y)

            if dist is not None and dist < 10:
                self.model.state.selected_point = index
            
    def mouseMoveEvent(self, ev) -> None:
        x, y = ev.pos().x(), ev.pos().y()
        # logger.info(f"MOVE: ({x}, {y})")

        if isinstance(self.model.state, MovePointState):
            if self.model.state.selected_point is not None:
                curve = self.model.state.curve
                index = self.model.state.selected_point

                curve.nodes[index] = (x, y)
                curve.calculate_points()
                self.model.updated()

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        x, y = event.pos().x(), event.pos().y()
        logger.info(f"RELEASE: ({x}, {y})")

        if isinstance(self.model.state, MovePointState):
            self.model.state.selected_point = None

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
