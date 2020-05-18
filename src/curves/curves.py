import logging

logger = logging.getLogger('curve-editor')

import numpy as np
import copy
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QInputDialog, QColorDialog

from scipy.spatial import ConvexHull

from src.states import AddNodeState, DefaultState, RemoveNodeState, MoveNodeState, \
    ChangeNodesOrderState


class Curve(object):
    def __init__(self, name, nodes=None, model=None):
        self.nodes = nodes or []
        self.points = []
        self.convex_hull = []

        self.name = name
        self.type = "Base Curve"

        self.selected = False
        self.hidden = False

        self.show_nodes = False
        self.show_convex_hull = False

        self.color = QtCore.Qt.blue
        self.width = 1.0

        self.resolution = 500

        self.model = model

        self.toolbar = None
        self.extra_toolbar = None

    def __repr__(self):
        return f"{self.type} | {len(self.nodes)} nodes"

    def clone(self):
        return copy.copy(self)

    def setModel(self, model):
        self.model = model

    def setup_toolbar(self, parent):
        self.toolbar = QtWidgets.QToolBar()

        self.add_node_action = QtWidgets.QAction("Add node", parent)
        self.add_node_action.triggered.connect(
            self.add_node_action_triggered)
        self.add_node_action.setCheckable(True)
        self.toolbar.addAction(self.add_node_action)

        self.remove_node_action = QtWidgets.QAction("Remove node", parent)
        self.remove_node_action.triggered.connect(
            self.remove_node_action_triggered)
        self.remove_node_action.setCheckable(True)
        self.toolbar.addAction(self.remove_node_action)

        self.move_node_action = QtWidgets.QAction("Move node", parent)
        self.move_node_action.triggered.connect(
            self.move_node_action_triggered)
        self.move_node_action.setCheckable(True)
        self.toolbar.addAction(self.move_node_action)

        self.show_nodes_action = QtWidgets.QAction("Show nodes",
                                                   parent)
        self.show_nodes_action.triggered.connect(
            self.show_nodes_action_triggered)
        self.show_nodes_action.setCheckable(True)
        self.toolbar.addAction(self.show_nodes_action)

        self.swap_nodes_action = QtWidgets.QAction("Swap nodes",
                                                   parent)
        self.swap_nodes_action.triggered.connect(
            self.swap_nodes_action_triggered)
        self.swap_nodes_action.setCheckable(True)
        self.toolbar.addAction(self.swap_nodes_action)

        self.insert_node_before_action = QtWidgets.QAction("Move node before",
                                                           parent)
        self.insert_node_before_action.triggered.connect(
            self.insert_node_before_action_triggered)
        self.insert_node_before_action.setCheckable(True)
        self.toolbar.addAction(self.insert_node_before_action)

        self.insert_node_after_action = QtWidgets.QAction("Move node after",
                                                          parent)
        self.insert_node_after_action.triggered.connect(
            self.insert_node_after_action_triggered)
        self.insert_node_after_action.setCheckable(True)
        self.toolbar.addAction(self.insert_node_after_action)

        self.visibility_action = QtWidgets.QAction("Show/hide", parent)
        self.visibility_action.triggered.connect(
            self.visibility_action_triggered)
        self.visibility_action.setCheckable(True)
        self.toolbar.addAction(self.visibility_action)

        self.rotate_action = QtWidgets.QAction("Rotate", parent)
        self.rotate_action.triggered.connect(
            self.rotate_action_triggered)
        self.toolbar.addAction(self.rotate_action)

        self.scale_action = QtWidgets.QAction("Scale", parent)
        self.scale_action.triggered.connect(
            self.scale_action_triggered)
        self.toolbar.addAction(self.scale_action)

        self.line_color_action = QtWidgets.QAction("Line color", parent)
        self.line_color_action.triggered.connect(
            self.line_color_action_triggered)
        self.toolbar.addAction(self.line_color_action)

        self.line_width_action = QtWidgets.QAction("Line width", parent)
        self.line_width_action.triggered.connect(
            self.line_width_action_triggered)
        self.toolbar.addAction(self.line_width_action)

        self.resolution_set_action = QtWidgets.QAction("Set resolution", parent)
        self.resolution_set_action.triggered.connect(
            self.resolution_set_action_triggered)
        self.toolbar.addAction(self.resolution_set_action)

    def add_node_action_triggered(self, state):
        if state:
            self.model.state = AddNodeState(self)
        else:
            self.model.state = DefaultState()

    def remove_node_action_triggered(self, state):
        if state:
            self.model.state = RemoveNodeState(self)
        else:
            self.model.state = DefaultState()

    def move_node_action_triggered(self, state):
        if state:
            self.model.state = MoveNodeState(curve=self)
        else:
            self.model.state = DefaultState()

    def show_nodes_action_triggered(self, state):
        if state != self.show_nodes:
            self.show_nodes = state
            self.model.updated()

    def swap_nodes_action_triggered(self, state):
        if state:
            self.model.state = ChangeNodesOrderState(self, 'swap', self.swap_nodes_action)
        else:
            self.model.state = DefaultState()

    def insert_node_before_action_triggered(self, state):
        if state:
            self.model.state = ChangeNodesOrderState(self, 'before', self.insert_node_before_action)
        else:
            self.model.state = DefaultState()

    def insert_node_after_action_triggered(self, state):
        if state:
            self.model.state = ChangeNodesOrderState(self, 'after', self.insert_node_after_action)
        else:
            self.model.state = DefaultState()

    def visibility_action_triggered(self, state):
        if state != self.hidden:
            self.hidden = state
            self.model.updated()

    def rotate_action_triggered(self, state):
        theta, ok = QInputDialog().getDouble(self.model.parent,
                                             "Rotate curve",
                                             "Degrees:",
                                             value=0.0,
                                             min=0.0,
                                             max=360.0)
        if ok:
            logger.info(f"Rotate curve: {theta}")
            self.rotate(theta)
            self.model.updated()

    def scale_action_triggered(self, state):
        scale, ok = QInputDialog().getDouble(self.model.parent,
                                             "Scale curve",
                                             "Scale:",
                                             value=1.0,
                                             min=0.0,
                                             max=10.0,
                                             decimals=2)
        if ok:
            logger.info(f"Scale curve: {scale}")
            self.scale(scale)
            self.model.updated()

    def line_color_action_triggered(self):
        color = QColorDialog().getColor(self.color,
                                        parent=self.model.parent,
                                        title="Select color")

        if color != self.color:
            logger.info(f"Changed color: {color}")
            self.color = color
            self.model.updated()

    def line_width_action_triggered(self):
        width, ok = QInputDialog().getDouble(self.model.parent,
                                             "Curve width",
                                             "Width:",
                                             value=self.width,
                                             min=0.1,
                                             max=100.0,
                                             decimals=1)
        if ok and width != self.width:
            logger.info(f"Curve width: {width}")
            self.width = width
            self.model.updated()

    def resolution_set_action_triggered(self):
        resolution, ok = QInputDialog().getInt(self.model.parent,
                                               "Curve resolution",
                                               "Points number:",
                                               value=self.resolution,
                                               min=100,
                                               max=100000,
                                               step=100)
        if ok and resolution != self.resolution:
            logger.info(f"Curve resolution: {resolution}")
            self.resolution = resolution
            self.calculate_points(force=True)
            self.model.updated()

    def calculate_convex_hull(self):
        if len(self.nodes) >= 3:
            hull = ConvexHull(self.nodes)
            self.convex_hull = [self.nodes[i] for i in hull.vertices]
        else:
            self.convex_hull = []

    def calculate_points(self, force=False, fast=False):
        if self.show_convex_hull:
            self.calculate_convex_hull()

    def distance_to_nearest_point(self, x, y):
        dists = [(np.sqrt((x - px) ** 2 + (y - py) ** 2), i)
                 for i, (px, py) in enumerate(self.points)]

        if dists:
            dist, index = min(dists)
            return index, dist

        return None, None

    def nearest_node(self, x, y):
        dists = [(np.sqrt((x - px) ** 2 + (y - py) ** 2), i) for i, (px, py) in enumerate(self.nodes)]

        if dists:
            dist, index = min(dists)
            return index, dist

        return None, None

    def draw_convex_hull(self, qp: QtGui.QPainter):
        points = self.convex_hull
        if len(points) < 2:
            return

        greenPen = QtGui.QPen(QtCore.Qt.green, 1, QtCore.Qt.DashLine)
        qp.setPen(greenPen)
        for i in range(len(points) - 1):
            qp.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])

        qp.drawLine(points[-1][0], points[-1][1], points[0][0], points[0][1])

    def draw_points(self, qp: QtGui.QPainter):
        pen = QtGui.QPen(self.color, self.width, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        points = self.points
        if len(points) < 2:
            return

        for i in range(len(points) - 1):
            x, y = points[i]
            next_x, next_y = points[i + 1]

            qp.drawLine(x, y, next_x, next_y)

    def draw_nodes(self, qp: QtGui.QPainter):
        red_pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        red_brush = QtGui.QBrush(QtCore.Qt.red)

        qp.setPen(red_pen)
        qp.setBrush(red_brush)

        old_point = self.nodes[0]
        qp.drawEllipse(old_point[0] - 3, old_point[1] - 3, 6, 6)
        qp.drawText(old_point[0] + 5, old_point[1] - 3, '1')
        for i, point in enumerate(self.nodes[1:]):
            i += 2
            qp.drawEllipse(point[0] - 3, point[1] - 3, 6, 6)
            qp.drawText(point[0] + 5, point[1] - 3, '%d' % i)

    def draw(self, qp: QtGui.QPainter):
        if self.hidden or not self.nodes:
            return

        if self.show_nodes:
            logger.info("Drawing nodes")
            self.draw_nodes(qp)

        self.draw_points(qp)

        if self.show_convex_hull:
            logger.info("Drawing convex hull")
            self.draw_convex_hull(qp)

    def calculate_center(self):
        center = [0, 0]
        for (x, y) in self.nodes:
            center[0] += x
            center[1] += y

        n = len(self.nodes)
        center = (center[0] / n, center[1] / n)
        return center

    def translate(self, dx, dy, calculate=True):
        self.nodes = [(x + dx, y + dy) for x, y in self.nodes]
        if calculate:
            self.calculate_points(force=True)

    def scale(self, scalar):
        (cx, cy) = self.calculate_center()

        for i, (x, y) in enumerate(self.nodes):
            dx, dy = x - cx, y - cy
            self.nodes[i] = (cx + dx * scalar, cy + dy * scalar)

        self.calculate_points()

    def rotate(self, theta):
        theta = theta * np.pi / 180

        center = np.array(self.calculate_center()).reshape(2, 1)
        nodes = np.array(self.nodes).T

        rotate_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                                  [np.sin(theta), np.cos(theta)]])

        new_nodes = center + rotate_matrix.dot(nodes - center)
        self.nodes = [(x, y) for x, y in new_nodes.T]

        print(nodes, new_nodes)

        self.calculate_points()

    def hide(self, state):
        self.hidden = state

    def to_dict(self):
        data = {
            "name": self.name,
            "type": self.type,
            "color": self.color,
            "nodes": self.nodes
        }
        return data

    @classmethod
    def from_dict(cls, data):
        nodes = data["nodes"] if "nodes" in data else []
        curve = cls(data["name"], nodes)

        if "color" in data:
            curve.color = data["color"]

        curve.calculate_points()
        return curve

