import numpy as np
from PyQt5 import QtGui, QtWidgets, QtCore
from scipy.spatial import ConvexHull

from src.states import AddPointState, DefaultState


class Curve(object):
    def __init__(self, name, nodes=None, model=None):
        self.nodes = nodes or []
        self.points = []
        self.convex_hull = []

        self.name = name
        self.type = "Base Curve"

        self.selected = False
        self.hidden = False

        self.show_control_points = False
        self.show_convex_hull = False

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
            self.model.state = AddPointState(self)
        else:
            self.model.state = DefaultState()

    def show_control_points_action_triggered(self, state):
        if state != self.show_control_points:
            self.show_control_points = state
            self.model.updated()

    def calculate_points(self):
        if len(self.nodes) >= 3:
            hull = ConvexHull(self.nodes)
            self.convex_hull = [self.nodes[i] for i in hull.vertices]
        else:
            self.convex_hull = []

    def distance_to_nearest_point(self, x, y):
        dists = [np.sqrt((x - px) ** 2 + (y - py) ** 2) for px, py in self.points]

        if dists:
            return min(dists)

        return np.inf

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
        for i in range(len(points)-1):
            qp.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])

        qp.drawLine(points[-1][0], points[-1][1], points[0][0], points[0][1])

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
