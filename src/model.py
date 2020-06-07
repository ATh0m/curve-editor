import json

from PyQt5.QtCore import QAbstractListModel, Qt

import src.curves
from .curves import Curve
from .states import DefaultState


class CurvesModel(QAbstractListModel):
    def __init__(self, *args, curves=None, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.curves = curves or []

        self.__state = DefaultState()
        self.parent = parent

        self.selected_curve = None
        self.selected_curve_index = None

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, s):
        self.__state.disable()
        self.__state = s
        self.__state.enable()

    def add(self, curve: Curve, selected=False):
        curve.setup_toolbar(self.parent)
        curve.setModel(self)

        self.curves.append(curve)
        if selected:
            self.select(len(self.curves) - 1)

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            curve = self.curves[index.row()]
            return str(curve)

    def rowCount(self, parent=None):
        return len(self.curves)

    def distance_to_nearest_curve(self, x, y):
        dists = [(curve.distance_to_nearest_point(x, y)[1], i)
                 for i, curve in enumerate(self.curves)]

        if dists:
            dist, index = min(dists)
            return index, dist

        return None, None

    def select(self, index):
        if self.selected_curve:
            self.selected_curve.selected = False

        self.selected_curve = self.curves[index]
        self.selected_curve.selected = True
        self.selected_curve_index = index

        self.updated()

    def deselect(self):
        if self.selected_curve:
            self.selected_curve.selected = False

            if len(self.selected_curve.nodes) < 2:
                self.remove_selected()
                return

        self.selected_curve = None
        self.selected_curve_index = None

        self.updated()

    def remove_selected(self):
        if self.selected_curve_index is not None:
            self.curves.pop(self.selected_curve_index)
            self.selected_curve = None
            self.selected_curve_index = None
            self.updated()

    def remove_curve(self, index):
        if index == self.selected_curve_index:
            self.remove_selected()
        else:
            self.curves.pop(index)
            self.updated()

    def updated(self):
        self.layoutChanged.emit()

    def save(self, filename):
        curves = [curve.to_dict() for curve in self.curves]
        with open(filename, 'w') as outfile:
            json.dump(curves, outfile)

    def load(self, filename):
        self.new(update=False)

        with open(filename, 'r') as json_file:
            data = json.load(json_file)

        types = {cls.type: cls for cls in map(src.curves.__dict__.get, src.curves.__all__)}
        curves = [types[d["type"]].from_dict(d) for d in data]

        for curve in curves:
            self.add(curve)

        self.updated()

    def new(self, update=True):
        self.__state = DefaultState()
        self.selected_curve = None
        self.selected_curve_index = None

        del self.curves
        self.curves = []

        if update:
            self.updated()
