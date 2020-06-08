from .curves import Curve

import numpy as np


class PolygonalCurve(Curve):
    type = "Polygonal Curve"

    def calculate_points(self, force=True, fast=False):
        super().calculate_points()

        if len(self.nodes) < 2:
            self.points = self.nodes
            return self.points

        nodes = self.nodes
        n = len(nodes)

        ts = np.linspace(0, 1, n)
        xs, ys = zip(*nodes)

        ts_ = np.linspace(0, 1, self.resolution)
        xs_ = np.interp(ts_, ts, xs)
        ys_ = np.interp(ts_, ts, ys)

        points = list(zip(xs_, ys_))
        self.points = points
        return self.points
