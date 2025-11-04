from components.buttons.selection_button import SelectionTool
from utils.logger import operation_logger
from utils.constants import COLOR_BLACK, COLOR_RED
class AddTransitionTool:
    """
        Tool to add a new transition by selecting two states on the canvas.
        If a transition in the same direction exists, it opens an edit window instead.
    """
    def __init__(self, canvas, automata_manager, undo_stack, redo_stack):
        self.canvas = canvas
        self.automata_manager = automata_manager
        self.undo_stack = undo_stack
        self.redo_stack = redo_stack
        self.selected_states = []

    def activate(self):
        """ Activate the tool by binding the click event. """
        self.canvas.bind("<Button-1>", self.on_click)
        operation_logger.info("AddTransitionTool activated.")

    def deactivate(self):
        """ Deactivate the tool by unbinding the click event and clearing selections. """
        self.canvas.unbind("<Button-1>")
        self.selected_states.clear()
        operation_logger.info("AddTransitionTool deactivated.")

    def on_click(self, event):
        """
            Handle canvas click to select two states for the transition.
            Click two states - get transition, if exists - edit it
        """
        selected_state = self.find_state(event.x, event.y)
        if selected_state:
            self.highlight_state(selected_state, True)
            self.selected_states.append(selected_state)
            if len(self.selected_states) == 2:
                state1, state2 = self.selected_states
                existing = self.find_existing_transition_same_dir(state1, state2)
                selection_tool = SelectionTool(
                    canvas=self.canvas,
                    automata_manager=self.automata_manager,
                    undo_stack=self.undo_stack,
                    redo_stack=self.redo_stack
                )
                if existing: # edit
                    selection_tool.open_transition_window(existing_transition=existing,
                                                          rx=event.x_root, ry=event.y_root)
                    operation_logger.info(f"Existing transition selected for editing: {state1.name} -> {state2.name}")
                else:       # add
                    selection_tool.open_transition_window(src=state1, tgt=state2,
                                                          existing_transition=None,
                                                          rx=event.x_root, ry=event.y_root)
                    operation_logger.info(f"New transition created: {state1.name} -> {state2.name}")
                for s_ in self.selected_states:
                    self.highlight_state(s_, False)
                self.selected_states.clear()
        else:
            # Clicked on empty space; reset selections
            for s_ in self.selected_states:
                self.highlight_state(s_, False)
            self.selected_states.clear()
            operation_logger.warning("Clicked on empty space while adding transition.")

    def find_state(self, x, y):
        """ Find and return the state at the given coordinates. """
        for s in self.automata_manager.states:
            dx, dy = x - s.x, y - s.y
            if (dx*dx + dy*dy)**0.5 <= s.radius:
                return s
        return None

    def highlight_state(self, st, on=True):
        """ Highlight or unhighlight a state on the canvas. """
        color = COLOR_RED if on else COLOR_BLACK
        if st.canvas_id:
            self.canvas.itemconfig(st.canvas_id, outline=color, width=3 if on else 2)

    def find_existing_transition_same_dir(self, state1, state2):
        """ Check if a transition from state1 to state2 already exists. """
        for t in self.automata_manager.transitions:
            if t.source == state1 and t.target == state2:
                return t
        return None
