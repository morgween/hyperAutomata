import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.constants import IMG_SIZE, COLOR_DT_BG
from components.buttons.add_state_button import AddStateTool
from components.buttons.add_transition_button import AddTransitionTool
from components.buttons.selection_button import SelectionTool
from utils.logger import operation_logger, error_logger

class ToolsFrame(tk.Frame):
    """ 
        A side panel with:
          - Word Count controls
          - Tools: Add State, Add Transition, Selection
          - Undo/Redo/Zoom
     """ 
    def __init__(self, parent, automata_mgr, canvas, undo_stack, redo_stack):
        super().__init__(parent, bg=COLOR_DT_BG)
        self.automata_mgr = automata_mgr
        self.canvas = canvas
        self.undo_stack = undo_stack
        self.redo_stack = redo_stack
        self.active_tool = None
        self.tools = {}
        self.buttons_dict = {}

        # Load icons
        self.icons = {
            "add_state": self.load_icon("assets/circle.png"),
            "add_transition": self.load_icon("assets/arrow.png"),
            "select": self.load_icon("assets/arrow_select.png"),
            "undo": self.load_icon("assets/arrow_back.png"),
            "redo": self.load_icon("assets/arrow_forward.png"),
            "zoom_in": self.load_icon("assets/zoom_in.png"),
            "zoom_out": self.load_icon("assets/zoom_out.png"),
        }

        # Style configuration for pressed tool buttons
        style = ttk.Style()
        style.configure("PressedToolButton.TButton", relief="sunken")

        # Word Count controls
        wc_frame = tk.Frame(self, bg=COLOR_DT_BG)
        wc_frame.pack(pady=5)
        ttk.Label(wc_frame, text="Word Count:").pack(side=tk.LEFT, padx=2)
        self.word_count_var = tk.IntVar(value=self.automata_mgr.word_count)
        self.wc_entry = ttk.Entry(wc_frame, textvariable=self.word_count_var, width=4, justify='center')
        self.wc_entry.pack(side=tk.LEFT, padx=2)

        plus_btn = ttk.Button(wc_frame, text="+", width=3, command=self.increment_word_count)
        plus_btn.pack(side=tk.LEFT, padx=2)
        minus_btn = ttk.Button(wc_frame, text="-", width=3, command=self.decrement_word_count)
        minus_btn.pack(side=tk.LEFT, padx=2)

        # Tools Buttons
        btn_add_state = self.add_tool_button(
            label="Add State",
            tool_obj=AddStateTool(canvas, automata_mgr, undo_stack, redo_stack),
            icon=self.icons["add_state"]
        )
        btn_add_transition = self.add_tool_button(
            label="Add Transition",
            tool_obj=AddTransitionTool(canvas, automata_mgr, undo_stack, redo_stack),
            icon=self.icons["add_transition"]
        )
        btn_select = self.add_tool_button(
            label="Selection",
            tool_obj=SelectionTool(canvas, automata_mgr, undo_stack, redo_stack),
            icon=self.icons["select"]
        )

        self.buttons_dict["Add State"] = btn_add_state
        self.buttons_dict["Add Transition"] = btn_add_transition
        self.buttons_dict["Selection"] = btn_select

        # Undo/Redo/Zoom Buttons
        ttk.Button(self, image=self.icons["undo"], command=self.undo).pack(pady=3)
        ttk.Button(self, image=self.icons["redo"], command=self.redo).pack(pady=3)
        ttk.Button(self, image=self.icons["zoom_in"], command=self.zoom_in).pack(pady=3)
        ttk.Button(self, image=self.icons["zoom_out"], command=self.zoom_out).pack(pady=3)

    def load_icon(self, path):
        """ Load and resize an icon image. """ 
        try:
            img = Image.open(path)
            img = img.resize(IMG_SIZE)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            error_logger.error(f"Failed to load icon {path}: {e}")
            return None

    def add_tool_button(self, label, tool_obj, icon):
        """ Add a tool button to the tools panel. """ 
        btn = ttk.Button(self, image=icon, command=lambda: self.activate_tool(label, tool_obj))
        btn.pack(pady=3)
        self.tools[label] = (btn, tool_obj)
        operation_logger.info(f"Tool button added: {label}")
        return btn

    def activate_tool(self, label):
        """  Activate a selected tool and deactivate any previously active tool.  """ 
        if self.active_tool:
            self.reset_tool(self.active_tool)
        self.active_tool = label
        btn, t = self.tools[label]
        btn.config(style="PressedToolButton.TButton")
        t.activate()
        operation_logger.info(f"Tool activated: {label}")

    def reset_tool(self, label):
        """ Reset a tool to its default state. """ 
        btn, t = self.tools[label]
        btn.config(style="TButton")
        t.deactivate()
        self.active_tool = None
        operation_logger.info(f"Tool reset: {label}")

    def enable_drawing_tools(self, enable: bool):
        """ 
            Enable or disable drawing tools based on the application's state.
            Prevents modifications during BFS runs.
         """ 
        state_ = tk.NORMAL if enable else tk.DISABLED
        for k in ["Add State", "Add Transition"]:
            if k in self.buttons_dict:
                self.buttons_dict[k].config(state=state_)
        operation_logger.info(f"Drawing tools {'enabled' if enable else 'disabled'}.")

    # Word Count
    def increment_word_count(self):
        """ Increase the word count and update the automata. """ 
        self.word_count_var.set(self.word_count_var.get() + 1)
        self.set_word_count()

    def decrement_word_count(self):
        """ Decrease the word count and update the automata, ensuring it doesn't go below 1. """ 
        val = self.word_count_var.get()
        if val > 1:
            self.word_count_var.set(val - 1)
            self.set_word_count()

    def set_word_count(self):
        """ Set the word count in the automata manager and redraw the canvas. """ 
        val = self.word_count_var.get()
        self.automata_mgr.set_word_count(val)
        self.canvas.delete("all")
        self.automata_mgr.draw_all(self.canvas)
        operation_logger.info(f"Word count set to: {val}")

    # Undo/Redo
    def undo(self):
        """ Perform an undo operation. """ 
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            operation_logger.info("Undo attempted with empty stack.")
            return
        action, obj = self.undo_stack.pop()
        if action == "add_state":
            self.remove_state_obj(obj)
        elif action == "add_transition":
            self.remove_transition_obj(obj)
        elif action == "remove_state":
            st, tr_list = obj
            self.automata_mgr.states.append(st)
            st.draw(self.canvas)
            for tr in tr_list:
                self.automata_mgr.transitions.append(tr)
                tr.source.outgoing_transitions.append(tr)
                tr.target.incoming_transitions.append(tr)
                tr.draw(self.canvas)
        elif action == "remove_transition":
            tr = obj
            self.automata_mgr.transitions.append(tr)
            tr.source.outgoing_transitions.append(tr)
            tr.target.incoming_transitions.append(tr)
            tr.draw(self.canvas)

        self.redo_stack.append((action, obj))
        operation_logger.info(f"Undo performed: {action} for {obj}")

    def redo(self):
        """ Perform a redo operation. """ 
        if not self.redo_stack:
            messagebox.showinfo("Redo", "Nothing to redo.")
            operation_logger.info("Redo attempted with empty stack.")
            return
        action, obj = self.redo_stack.pop()
        if action == "add_state":
            self.automata_mgr.states.append(obj)
            obj.draw(self.canvas)
        elif action == "add_transition":
            self.automata_mgr.transitions.append(obj)
            obj.source.outgoing_transitions.append(obj)
            obj.target.incoming_transitions.append(obj)
            obj.draw(self.canvas)
        elif action == "remove_state":
            st, _ = obj
            self.remove_state_obj(st)
        elif action == "remove_transition":
            self.remove_transition_obj(obj)

        self.undo_stack.append((action, obj))
        operation_logger.info(f"Redo performed: {action} for {obj}")

    def remove_state_obj(self, st):
        """ Remove a state and its transitions from the automata manager and canvas. """ 
        if st.canvas_id:
            self.canvas.delete(st.canvas_id)
        if st.label_id:
            self.canvas.delete(st.label_id)
        for exid in st.extra_ids:
            self.canvas.delete(exid)
        if st in self.automata_mgr.states:
            self.automata_mgr.states.remove(st)
        all_trans = st.outgoing_transitions + st.incoming_transitions
        for t in all_trans:
            self.remove_transition_obj(t)
        operation_logger.info(f"State removed via undo: {st.name}")

    def remove_transition_obj(self, tr):
        """ Remove a transition from the automata manager and canvas. """ 
        for cid in tr.canvas_ids:
            self.canvas.delete(cid)
        if tr in self.automata_mgr.transitions:
            self.automata_mgr.transitions.remove(tr)
        if tr in tr.source.outgoing_transitions:
            tr.source.outgoing_transitions.remove(tr)
        if tr in tr.target.incoming_transitions:
            tr.target.incoming_transitions.remove(tr)
        operation_logger.info(f"Transition removed via undo: {tr.source.name} -> {tr.target.name}")

    def zoom_in(self):
        """ Zoom in the canvas. """ 
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        operation_logger.info("Canvas zoomed in.")

    def zoom_out(self):
        """ Zoom out the canvas. """ 
        self.canvas.scale("all", 0, 0, 0.8, 0.8)
        operation_logger.info("Canvas zoomed out.")
