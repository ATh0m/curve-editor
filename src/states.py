class State(object):
    def __init__(self):
        pass


class DefaultState(State):
    def next_state(self):
        return DefaultState()

    def disable(self):
        pass


class SelectCurveState(DefaultState):
    pass


class RemoveCurveState(DefaultState):
    pass


class MoveCurveState(DefaultState):
    def __init__(self):
        super().__init__()

        self.curve = None
        self.last_position = None


class AddNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve

    def disable(self):
        self.curve.add_node_action.setChecked(False)


class RemoveNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve

    def disable(self):
        self.curve.remove_node_action.setChecked(False)


class MoveNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve
        self.selected_point = None

    def disable(self):
        self.curve.move_node_action.setChecked(False)
