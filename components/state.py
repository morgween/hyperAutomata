import tkinter as tk
from utils.constants import STATE_RADIUS, COLOR_BLACK
from utils.logger import operation_logger

class State:
    """ Represents a single GUI state with x, y coordinates, radius, start/accept flags, ids, transitions"""
    def __init__(self, name, x, y, is_start=False, is_accept=False):
        self.name = name
        self.x = x
        self.y = y
        self.is_start = is_start
        self.is_accept = is_accept
        self.radius = STATE_RADIUS

        # Id's to easy identify states
        self.canvas_id = None   
        self.label_id = None
        self.extra_ids = []

        self.outgoing_transitions = []
        self.incoming_transitions = []

    def draw(self, canvas):
        """ Draw the state on the given canvas, including start arrow and accept ring if applicable. """
        if not canvas:
            return
        if self.canvas_id:
            canvas.delete(self.canvas_id)
        r = self.radius
        self.canvas_id = canvas.create_oval(
            self.x - r, self.y - r, self.x + r, self.y + r,
            fill="white", outline=COLOR_BLACK, width=2,
            tags=(f"state_{self.name}",)
        )
        if self.label_id:
            canvas.delete(self.label_id)
        self.label_id = canvas.create_text(self.x, self.y, text=self.name)

        # Remove old extras
        for exid in self.extra_ids:
            canvas.delete(exid)
        self.extra_ids.clear()

        # Draw accept ring
        if self.is_accept:
            accept_id = canvas.create_oval(
                self.x - r - 4, self.y - r - 4,
                self.x + r + 4, self.y + r + 4,
                outline=COLOR_BLACK, width=2
            )
            self.extra_ids.append(accept_id)
            operation_logger.debug(f"Accept ring drawn for state: {self.name}")

        # Draw start arrow
        if self.is_start:
            arrow_id = canvas.create_line(
                self.x - r - 20, self.y,
                self.x - r, self.y,
                arrow=tk.LAST
            )
            self.extra_ids.append(arrow_id)
            operation_logger.debug(f"Start arrow drawn for state: {self.name}")

    def move(self, canvas, nx, ny):
        """ Move the state to new coordinates and update all associated transitions. """
        dx, dy = nx - self.x, ny - self.y
        self.x, self.y = nx, ny
        canvas.move(self.canvas_id, dx, dy)
        canvas.move(self.label_id, dx, dy)
        for exid in self.extra_ids:
            canvas.move(exid, dx, dy)
        operation_logger.info(f"State moved: {self.name} to ({nx}, {ny})")
