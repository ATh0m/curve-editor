class State(object):
    def __init__(self):
        pass


class DefaultState(State):
    def nextState(self):
        return DefaultState()


class SelectCurveState(DefaultState):
    pass


class AddPointState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve
