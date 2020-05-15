from PyQt5 import QtGui, QtWidgets

import numpy as np
from src.states import AddPointState, DefaultState


class Curve(object):
    def __init__(self, name, nodes=None, model=None):
        self.nodes = nodes or []
        self.points = []

        self.name = name
        self.type = "Base Curve"

        self.selected = False
        self.hidden = False

        self.show_control_points = False

        self.color = "blue"

        self.model = model

        self.toolbar = None

    def __repr__(self):
        return f"{self.name} | {self.type} | {len(self.nodes)} nodes"

    def setModel(self, model):
        self.model = model

    def setup_toolbar(self, parent):
        self.toolbar = QtWidgets.QToolBar()

        self.add_point_action = QtWidgets.QAction("Add point", parent)
        self.add_point_action.triggered.connect(
            self.add_point_action_triggered)
        self.add_point_action.setCheckable(True)
        self.toolbar.addAction(self.add_point_action)

        show_control_points_action = QtWidgets.QAction("Control points",
                                                       parent)
        show_control_points_action.triggered.connect(
            self.show_control_points_action_triggered)
        show_control_points_action.setCheckable(True)
        self.toolbar.addAction(show_control_points_action)

    def add_point_action_triggered(self, state):
        if state:
            self.model.state = AddPointState(curve=self)
        else:
            self.model.state = DefaultState()

    def show_control_points_action_triggered(self, state):
        if state != self.show_control_points:
            self.show_control_points = state
            self.model.updated()

    def calculate_points(self):
        raise NotImplementedError

    def distance_to_nearest_point(self, x, y):
        dists = [np.sqrt((x - px)**2 + (y - py)**2) for px, py in self.points]

        if dists:
            return min(dists)

        return np.inf

    def draw(self, qp: QtGui.QPainter):
        if self.hidden or not self.nodes:
            return

    def calculate_center(self):
        center = [0, 0]
        for (x, y) in self.nodes:
            center[0] += x
            center[1] += y

        n = len(self.nodes)
        center = (center[0] / n, center[1] / n)
        return center

    def translate(self, dx, dy):
        self.nodes = [(x + dx, y + dy) for x, y in self.nodes]
        self.calculate_points()

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
