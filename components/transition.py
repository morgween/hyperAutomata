import tkinter as tk
import math
from utils.constants import COLOR_BLACK, PARALLEL_OFFSET
from utils.logger import operation_logger, error_logger

class Transition:
    """
        Represents a GUI transition from a source state to a target state,
        with one or more condition vectors.
        Handles drawing of arrows and labels.
    """
    def __init__(self, source, target, transition_vectors):
        self.source = source
        self.target = target
        self.transition_vectors = transition_vectors
        self.canvas_ids = []
        self.offset_index = 0  # Used to compute ± offset for parallel transitions

        source.outgoing_transitions.append(self)
        target.incoming_transitions.append(self)
        operation_logger.info(f"Transition created: {source.name} -> {target.name}")

    def draw(self, canvas):
        """ Draw the transition on the canvas. """
        self.clear(canvas)
        if not canvas:
            return
        if self.source == self.target:
            self.draw_loop(canvas)
        else:
            self.draw_arrow(canvas)

    def redraw(self, canvas):
        """ Redraw the transition (useful after moving states) """
        self.draw(canvas)

    def draw_loop(self, canvas):
        """ Draw a loop transition for transitions from a state to itself. """
        r = self.source.radius
        cx = self.source.x
        cy = self.source.y - (r + 30)
        try:
            arc_id = canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=290, extent=320, style="arc",
                outline=COLOR_BLACK, width=2
            )
            self.canvas_ids.append(arc_id)

            lbl = canvas.create_text(cx, cy - (r + 10), text=self.label_text())
            self.canvas_ids.append(lbl)
            operation_logger.debug(f"Loop transition drawn for state: {self.source.name}")
        except Exception as e:
            error_logger.error(f"Failed to draw loop transition: {e}")

    def draw_arrow(self, canvas):
        """
            Draw an arrow from the source state to the target state,
            handling parallel transitions by offsetting them.
        """
        sx, sy = self.source.x, self.source.y
        tx, ty = self.target.x, self.target.y
        dx, dy = tx - sx, ty - sy
        dist = math.hypot(dx, dy)

        # Unit vector components
        ux, uy = dx / dist, dy / dist

        # Calculate offset for parallel transitions to handle q0-q1 q1-q0 transitions
        sign = -1 if self.offset_index % 2 == 0 else 1
        steps = (self.offset_index // 2) + 1
        offset = sign * steps * PARALLEL_OFFSET
        perp_x, perp_y = -uy, ux  # Perpendicular vector

        # Adjusted start and end points
        sx_e = sx + ux * self.source.radius + perp_x * offset
        sy_e = sy + uy * self.source.radius + perp_y * offset
        tx_e = tx - ux * self.target.radius + perp_x * offset
        ty_e = ty - uy * self.target.radius + perp_y * offset

        try:
            line_id = canvas.create_line(
                sx_e, sy_e, tx_e, ty_e,
                arrow=tk.LAST, fill=COLOR_BLACK, width=2
            )
            self.canvas_ids.append(line_id)

            # Label near the midpoint
            mx, my = (sx_e + tx_e) / 2, (sy_e + ty_e) / 2
            lbl_id = canvas.create_text(mx, my - 10, text=self.label_text())
            self.canvas_ids.append(lbl_id)
            operation_logger.debug(f"Transition arrow drawn: {self.source.name} -> {self.target.name}")
        except Exception as e:
            error_logger.error(f"Failed to draw transition arrow: {e}")

    def label_text(self):
        """ Generate the label text based on transition vectors. """
        parts = []
        for vec in self.transition_vectors:
            vs = ",".join(vec)
            parts.append("{" + vs + "}")
        return ", ".join(parts)

    def clear(self, canvas):
        """ Remove all canvas items associated with this transition. """
        try:
            for cid in self.canvas_ids:
                canvas.delete(cid)
            self.canvas_ids.clear()
            operation_logger.debug(f"Transition cleared: {self.source.name} -> {self.target.name}")
        except Exception as e:
            error_logger.error(f"Failed to clear transition: {e}")
