import logging

import numpy as np
from scipy.interpolate import CubicSpline as CS

from .curves import Curve

logger = logging.getLogger('curve-editor')


class CubicSpline(Curve):
    def __init__(self, name, nodes=None):
        super().__init__(name, nodes)

        self.type = "Cubic Spline"

    @staticmethod
    def cubic_interp1d(ts0, ts, xs):
        ts = np.asfarray(ts)
        xs = np.asfarray(xs)

        n = len(ts)

        dt = np.diff(ts)
        dx = np.diff(xs)

        # allocate buffer matrices
        li = np.empty(n)
        li_1 = np.empty(n - 1)
        z = np.empty(n)

        # fill diagonals Li and Li-1 and solve [L][xs] = [B]
        li[0] = np.sqrt(2 * dt[0])
        li_1[0] = 0.0
        b0 = 0.0  # natural boundary
        z[0] = b0 / li[0]

        for i in range(1, n - 1, 1):
            li_1[i] = dt[i - 1] / li[i - 1]
            li[i] = np.sqrt(2 * (dt[i - 1] + dt[i]) - li_1[i - 1] * li_1[i - 1])
            bi = 6 * (dx[i] / dt[i] - dx[i - 1] / dt[i - 1])
            z[i] = (bi - li_1[i - 1] * z[i - 1]) / li[i]

        i = n - 1
        li_1[i - 1] = dt[-1] / li[i - 1]
        li[i] = np.sqrt(2 * dt[-1] - li_1[i - 1] * li_1[i - 1])
        bi = 0.0  # natural boundary
        z[i] = (bi - li_1[i - 1] * z[i - 1]) / li[i]

        # solve [L.T][ts] = [xs]
        i = n - 1
        z[i] = z[i] / li[i]
        for i in range(n - 2, -1, -1):
            z[i] = (z[i] - li_1[i - 1] * z[i + 1]) / li[i]

        # find index
        index = ts.searchsorted(ts0)
        np.clip(index, 1, n - 1, index)

        xi1, xi0 = ts[index], ts[index - 1]
        yi1, yi0 = xs[index], xs[index - 1]
        zi1, zi0 = z[index], z[index - 1]
        hi1 = xi1 - xi0

        # calculate cubic
        f0 = zi0 / (6 * hi1) * (xi1 - ts0) ** 3 + \
             zi1 / (6 * hi1) * (ts0 - xi0) ** 3 + \
             (yi1 / hi1 - zi1 * hi1 / 6) * (ts0 - xi0) + \
             (yi0 / hi1 - zi0 * hi1 / 6) * (xi1 - ts0)
        return f0

    def calculate_points(self, force=True, fast=False):
        super().calculate_points()

        if not self.nodes:
            self.points = []
            return self.points

        if len(self.nodes) < 3:
            self.points = self.nodes
            return self.points

        steps = self.resolution

        xs, ys = zip(*self.nodes)
        n = len(self.nodes)

        ts = np.linspace(0, 1, n)
        ts0 = np.linspace(0, 1, steps)

        # xs_ = CS(ts, xs, bc_type='natural')(ts0)
        # ys_ = CS(ts, ys, bc_type='natural')(ts0)

        xs_ = CubicSpline.cubic_interp1d(ts0, ts, xs)
        ys_ = CubicSpline.cubic_interp1d(ts0, ts, ys)
        points = list(zip(xs_, ys_))

        self.points = points
        return self.points
