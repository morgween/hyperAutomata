import tkinter as tk
from utils.constants import COLOR_BLACK, COLOR_RED
from utils.logger import operation_logger

class DrawingBoard(tk.Canvas):
    """
    The main canvas for drawing states and transitions.
    Allows highlighting a single state at a time.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.current_highlight = None
        operation_logger.info("DrawingBoard initialized.")

    def highlight_state(self, state_name):
        """
            Highlight the specified state on the canvas by changing its outline color.
            Removes highlight from the previously highlighted state.
        """
        # Remove old highlight
        if self.current_highlight:
            self.itemconfig(self.current_highlight, outline=COLOR_BLACK, width=2)
            operation_logger.debug(f"Removed highlight from state: {self.current_highlight}")
            self.current_highlight = None

        if not state_name:
            return

        # Find and highlight the new state
        for item in self.find_all():
            tags = self.gettags(item)
            if f"state_{state_name}" in tags:
                self.itemconfig(item, outline=COLOR_RED, width=3)
                self.current_highlight = item
                operation_logger.info(f"State highlighted: {state_name}")
                break
