class State(object):
    def __init__(self):
        pass


class DefaultState(State):
    def nextState(self):
        return DefaultState()

    def disable(self):
        pass


class SelectCurveState(DefaultState):
    pass


class RemoveCurveState(DefaultState):
    pass


class AddPointState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve

    def disable(self):
        self.curve.add_point_action.setChecked(False)


class MovePointState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve
        self.selected_point = None

    def disable(self):
        self.curve.move_point_action.setChecked(False)
