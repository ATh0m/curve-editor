import logging

logger = logging.getLogger('curve-editor')

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


class ChangeNodesOrderState(DefaultState):
    def __init__(self, curve, mode, controller=None):
        super().__init__()

        self.mode = mode # swap, before, after
        self.controller = controller

        self.curve = curve
        self.first_node = None
        self.second_node = None

    def apply(self):
        curve = self.curve

        first_node = curve.nodes[self.first_node]
        second_node = curve.nodes[self.second_node]

        if self.mode == 'swap':
            curve.nodes[self.first_node] = second_node
            curve.nodes[self.second_node] = first_node

            curve.calculate_points()

        elif self.mode == 'before':
            curve.nodes.insert(self.second_node, first_node)

            if self.second_node <= self.first_node:
                curve.nodes.pop(self.first_node + 1)
            else:
                curve.nodes.pop(self.first_node)
        elif self.mode == 'after':
            curve.nodes.insert(self.second_node + 1, first_node)

            if self.second_node + 1 <= self.first_node:
                curve.nodes.pop(self.first_node + 1)
            else:
                curve.nodes.pop(self.first_node)


    def disable(self):
        self.controller.setChecked(False)