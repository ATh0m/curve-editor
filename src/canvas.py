import logging

logger = logging.getLogger('curve-editor')

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt

from .model import CurvesModel
from .states import SelectCurveState, AddNodeState, MoveNodeState, RemoveCurveState, \
    RemoveNodeState, MoveCurveState, ChangeNodesOrderState


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

            self.model.state = self.model.state.next_state()

        elif isinstance(self.model.state, RemoveCurveState):
            logger.info('removing')

            index, dist = self.model.distance_to_nearest_curve(x, y)
            logger.info(index, dist)
            if dist is not None and dist < 10:
                self.model.remove_curve(index)
                logger.info(f'Remove curve: {index}')

            self.model.state = self.model.state.next_state()

        elif isinstance(self.model.state, MoveCurveState):
            index, dist = self.model.distance_to_nearest_curve(x, y)
            if dist is not None and dist < 10:
                self.model.state.curve = self.model.curves[index]
                self.model.state.last_position = (x, y)
            else:
                self.model.state = self.model.state.next_state()

        elif isinstance(self.model.state, AddNodeState):
            curve = self.model.state.curve
            curve.nodes.append((x, y))
            curve.calculate_points()

            self.model.layoutChanged.emit()

        elif isinstance(self.model.state, RemoveNodeState):
            curve = self.model.state.curve

            index, dist = curve.nearest_node(x, y)

            if dist is not None and dist < 10:
                curve.nodes.pop(index)

                curve.calculate_points()
                self.model.layoutChanged.emit()

            self.model.state = self.model.state.next_state()

        elif isinstance(self.model.state, MoveNodeState):
            curve = self.model.state.curve

            index, dist = curve.nearest_node(x, y)

            if dist is not None and dist < 10:
                self.model.state.selected_point = index

        elif isinstance(self.model.state, ChangeNodesOrderState):
            state = self.model.state
            curve = self.model.state.curve

            index, dist = curve.nearest_node(x, y)

            if dist is not None and dist < 10:
                if state.first_node is None:
                    state.first_node = index
                else:
                    state.second_node = index

                    state.apply()
                    self.model.updated()

                    self.model.state = self.model.state.next_state()



    def mouseMoveEvent(self, ev) -> None:
        x, y = ev.pos().x(), ev.pos().y()
        # logger.info(f"MOVE: ({x}, {y})")

        if isinstance(self.model.state, MoveNodeState):
            if self.model.state.selected_point is not None:
                curve = self.model.state.curve
                index = self.model.state.selected_point

                curve.nodes[index] = (x, y)
                curve.calculate_points()
                self.model.updated()

        elif isinstance(self.model.state, MoveCurveState):
            if self.model.state.curve is not None:
                curve = self.model.state.curve
                last_x, last_y = self.model.state.last_position

                dx, dy = x - last_x, y - last_y
                curve.translate(dx, dy)
                self.model.updated()

                self.model.state.last_position = (x, y)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        x, y = event.pos().x(), event.pos().y()
        logger.info(f"RELEASE: ({x}, {y})")

        if isinstance(self.model.state, MoveNodeState):
            self.model.state.selected_point = None

        elif isinstance(self.model.state, MoveCurveState):
            self.model.state = self.model.state.next_state()

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
