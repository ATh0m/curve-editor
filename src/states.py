import logging

logger = logging.getLogger('curve-editor')


class State(object):
    pass


class DefaultState(State):
    def next_state(self):
        return DefaultState()

    def mousePressEvent(self, event, canvas):
        pass

    def mouseMoveEvent(self, event, canvas):
        pass

    def mouseReleaseEvent(self, event, canvas):
        pass

    def disable(self):
        pass


class SelectCurveState(DefaultState):
    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        logger.info('selecting')

        index, dist = canvas.model.distance_to_nearest_curve(x, y)
        logger.info(index, dist)
        if dist is not None and dist < 10:
            canvas.model.select(index)
            logger.info(f'Selected curve: {index}')
        else:
            canvas.model.deselect()

        canvas.model.state = self.next_state()


class RemoveCurveState(DefaultState):
    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        logger.info('removing')

        index, dist = canvas.model.distance_to_nearest_curve(x, y)
        logger.info(index, dist)
        if dist is not None and dist < 10:
            canvas.model.remove_curve(index)
            logger.info(f'Remove curve: {index}')

        canvas.model.state = self.next_state()


class MoveCurveState(DefaultState):
    def __init__(self):
        super().__init__()

        self.curve = None
        self.last_position = None

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        index, dist = canvas.model.distance_to_nearest_curve(x, y)
        if dist is not None and dist < 10:
            self.curve = canvas.model.curves[index]
            self.last_position = (x, y)
        else:
            canvas.model.state = self.next_state()

    def mouseMoveEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        if self.curve is not None:
            curve = self.curve
            last_x, last_y = self.last_position

            dx, dy = x - last_x, y - last_y
            curve.translate(dx, dy)
            canvas.model.updated()

            self.last_position = (x, y)

    def mouseReleaseEvent(self, event, canvas):
        canvas.model.state = self.next_state()


class AddNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve

    def disable(self):
        self.curve.add_node_action.setChecked(False)

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        curve = self.curve
        curve.nodes.append((x, y))
        curve.calculate_points()

        canvas.model.layoutChanged.emit()


class RemoveNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve

    def disable(self):
        self.curve.remove_node_action.setChecked(False)

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        curve = self.curve

        index, dist = curve.nearest_node(x, y)

        if dist is not None and dist < 10:
            curve.nodes.pop(index)

            curve.calculate_points()
            canvas.model.layoutChanged.emit()

        canvas.model.state = self.next_state()


class MoveNodeState(DefaultState):
    def __init__(self, curve):
        super().__init__()

        self.curve = curve
        self.selected_point = None

    def disable(self):
        self.curve.move_node_action.setChecked(False)

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        curve = self.curve

        index, dist = curve.nearest_node(x, y)

        if dist is not None and dist < 10:
            self.selected_point = index

    def mouseMoveEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        if self.selected_point is not None:
            curve = self.curve
            index = self.selected_point

            curve.nodes[index] = (x, y)
            curve.calculate_points()
            canvas.model.updated()

    def mouseReleaseEvent(self, event, canvas):
        self.selected_point = None


class ChangeNodesOrderState(DefaultState):
    def __init__(self, curve, mode, controller=None):
        super().__init__()

        self.mode = mode  # swap, before, after
        self.controller = controller

        self.curve = curve
        self.first_node = None
        self.second_node = None

    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        curve = self.curve
        index, dist = curve.nearest_node(x, y)

        if dist is not None and dist < 10:
            if self.first_node is None:
                self.first_node = index
            else:
                self.second_node = index

                self.apply()
                canvas.model.updated()

                canvas.model.state = self.next_state()

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


class DuplicateCurveState(DefaultState):
    def mousePressEvent(self, event, canvas):
        x, y = event.pos().x(), event.pos().y()

        index, dist = canvas.model.distance_to_nearest_curve(x, y)
        logger.info(index, dist)
        if dist is not None and dist < 10:
            curve = canvas.model.curves[index]

            new_curve = curve.clone()
            new_curve.translate(20, 20)

            canvas.model.add(new_curve, selected=True)
            canvas.model.updated()

        canvas.model.state = self.next_state()