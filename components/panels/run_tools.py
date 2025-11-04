import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from utils.constants import IMG_SIZE, COLOR_RT_BG, RUN_PAUSES_MS, AppMode
from utils.logger import operation_logger, error_logger

class RunToolsFrame(tk.Frame):
    """ 
        The bottom frame with Run/Pause/Step/Stop/Reload/Save/Load icons and words window.
        Using run_manager to coordinate GUI and backend together.
     """ 
    def __init__(self, parent, run_mgr, canvas):
        super().__init__(parent, bg=COLOR_RT_BG)
        
        # References to other components
        self.run_mgr = run_mgr
        self.canvas = canvas
        self.running = False
        self.current_setup_window = None
        self.tools_panel_ref = None
        self.words_window_ref = None  

        self.after_id = None
        
        self.icons = {
            "run": self.load_icon("assets/run.png"),
            "pause": self.load_icon("assets/pause.png"),
            "step": self.load_icon("assets/step.png"),
            "stop": self.load_icon("assets/stop.png"),
            "reload": self.load_icon("assets/reload.png"),
            "save": self.load_icon("assets/save.png"),
            "story": self.load_icon("assets/story.png"),
        }

        # Initialize buttons with ttk for better appearance
        self.run_btn = ttk.Button(self, image=self.icons["run"], command=self.on_run)
        self.run_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_btn = ttk.Button(self, image=self.icons["pause"], command=self.on_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.step_btn = ttk.Button(self, image=self.icons["step"], command=self.on_step)
        self.step_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.stop_btn = ttk.Button(self, image=self.icons["stop"], command=self.on_stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.reload_btn = ttk.Button(self, image=self.icons["reload"], command=self.on_reload)
        self.reload_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_btn = ttk.Button(self, image=self.icons["save"], command=self.on_save_run)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_btn = ttk.Button(self, image=self.icons["story"], command=self.on_load_run)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def load_icon(self, path):
        """ Load and resize an icon image. """ 
        try:
            img = Image.open(path)
            img = img.resize(IMG_SIZE)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            error_logger.error(f"Failed to load icon {path}: {e}")
            return None

    def set_current_setup(self, setup_window):
        """ Set reference to the Current Setup window. """ 
        self.current_setup_window = setup_window
        operation_logger.info("CurrentSetupFrame linked to RunToolsFrame.")

    def set_tools_panel_ref(self, tools_panel):
        """ Set reference to the Tools Panel. """ 
        self.tools_panel_ref = tools_panel
        operation_logger.info("ToolsPanel linked to RunToolsFrame.")

    def set_words_window_ref(self, words_window):
        """ Set reference to the Words Window. """ 
        self.words_window_ref = words_window
        operation_logger.info("WordsWindow linked to RunToolsFrame.")

    def on_run(self):
        """  Start the BFS simulation. Runs until paused. """ 
        self.run_mgr.app_mode = AppMode.RUNNING
        self.run_mgr.running = True
        if self.tools_panel_ref:
            self.tools_panel_ref.enable_drawing_tools(False)

        if not self.running:
            self.run_mgr.initialize_backend()
            self.run_mgr.load_history()

        self.running = True
        self.run_simulation()
        operation_logger.info("BFS simulation started.")

    def run_simulation(self):
        """ Run the BFS simulation step-by-step. """ 
        if not self.running:
            return
        snap = self.run_mgr.step()
        if snap:
            self.highlight_step(snap)
            self.after_id = self.after(RUN_PAUSES_MS, self.run_simulation)  # Continue after 600ms
        else:
            self.running = False
            msg = "Accepted!" if self.run_mgr.is_accepted() else "Rejected!"
            messagebox.showinfo("Result", msg)
            operation_logger.info(f"BFS simulation ended with result: {msg}")
            self.finish_run()

    def on_pause(self):
        """ Pause the BFS simulation. """ 
        self.running = False
        self.run_mgr.pause()
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        operation_logger.info("BFS simulation paused.")

    def on_step(self):
        """ Perform a single step in the BFS simulation. """ 
        if not self.run_mgr.running:
            self.run_mgr.running = True
            self.run_mgr.app_mode = AppMode.RUNNING
            self.run_mgr.initialize_backend()
            self.run_mgr.load_history()

        if self.tools_panel_ref:
            self.tools_panel_ref.enable_drawing_tools(False)

        snap = self.run_mgr.step()
        if snap:
            self.highlight_step(snap)
        else:
            msg = "Accepted!" if self.run_mgr.is_accepted() else "Rejected!"
            messagebox.showinfo("Result", msg)
            operation_logger.info(f"BFS simulation ended with result: {msg}")
            self.finish_run()

    def on_stop(self):
        """ Stop the BFS simulation and reset. """ 
        self.on_pause()
        self.run_mgr.restart()
        self.canvas.highlight_state(None)
        self.finish_run()
        messagebox.showinfo("Stopped", "Simulation has been reset.")
        operation_logger.info("BFS simulation stopped and reset.")

    def on_reload(self):
        """ Reload the simulation, clearing all states and transitions. """ 
        self.on_pause()
        self.run_mgr.clear_all()
        self.canvas.delete("all")
        if self.current_setup_window:
            self.current_setup_window.display_step(None)
        if self.tools_panel_ref:
            self.tools_panel_ref.enable_drawing_tools(True)
        messagebox.showinfo("Reloaded", "All states and transitions have been cleared.")
        operation_logger.info("BFS simulation reloaded and cleared.")

    def finish_run(self):
        """ Finalize the BFS simulation run. """ 
        self.running = False
        self.run_mgr.running = False
        self.run_mgr.app_mode = AppMode.DRAWING
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        if self.tools_panel_ref:
            self.tools_panel_ref.enable_drawing_tools(True)
        operation_logger.info("BFS simulation run finished.")

    def highlight_step(self, step):
        """ Highlight the current state and update the Current Setup display. """ 
        if not step:
            return
        state_name = step[0]
        self.highlight_state(state_name)
        if self.current_setup_window:
            self.current_setup_window.display_step(step)
        operation_logger.info(f"Highlighted step: {state_name}")

    def highlight_state(self, state_name):
        """ Highlight a specific state on the canvas. """ 
        self.canvas.highlight_state(state_name)
        operation_logger.info(f"State highlighted: {state_name}")

    def on_save_run(self):
        """ Save the current run history to the database. """ 
        if not self.run_mgr.current_user:
            messagebox.showerror("Error", "No user is currently logged in.")
            error_logger.error("Attempted to save run history without a logged-in user.")
            return
        snap_name = simpledialog.askstring("Save Snapshot", "Enter a name for the current snapshot:")
        if snap_name is None or not snap_name.strip():
            return 
        self.run_mgr.save_current_run(description=f"{snap_name}")
        messagebox.showinfo("Saved", "Run history saved successfully!")
        operation_logger.info(f"Run history saved with description: {snap_name}")

    def on_load_run(self):
        """ Load a run history from the database. """ 
        if not self.run_mgr.current_user:
            messagebox.showerror("Error", "No user is currently logged in.")
            error_logger.error("Attempted to load run history without a logged-in user.")
            return
        histories = self.run_mgr.db_manager.list_run_histories(self.run_mgr.current_user)
        if not histories:
            messagebox.showinfo("No Snapshots", "There are no saved runs for this user.")
            operation_logger.info("No run histories found for user during load attempt.")
            return

        load_win = tk.Toplevel(self)
        load_win.title("Load Snapshot")
        load_win.geometry("300x300")

        ttk.Label(load_win, text="Select a snapshot to load:", justify='center').pack(pady=5)
        lb = tk.Listbox(load_win)
        lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        records_map = {}
        for i, rec in enumerate(histories):
            rid, desc, _, _ = rec
            record_name = f"ID={rid}: {desc}"
            lb.insert(tk.END, record_name)
            records_map[i] = rec

        def on_select_load():
            """ Handle the selection and loading of a run history. """ 
            sel = lb.curselection()
            if not sel:
                return
            idx = sel[0]
            _, desc, automaton_json, hist_json = records_map[idx]
            import json
            try:
                automaton_data = json.loads(automaton_json)
                history_data = json.loads(hist_json)
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Failed to parse run history data: {e}")
                error_logger.error(f"JSON decode error during run history load: {e}")
                return

            self.run_mgr.load_run(automaton_data, history_data)
            self.canvas.delete("all")
            self.run_mgr.automata_manager.draw_all(self.canvas)

            # Refresh the Words Window
            if self.words_window_ref:
                self.words_window_ref.refresh()

            # Reset the Current Setup display
            if self.current_setup_window:
                self.current_setup_window.display_step(None)

            load_win.destroy()
            messagebox.showinfo("Loaded", f"Snapshot '{desc}' loaded successfully.")
            operation_logger.info(f"Run history loaded: {desc}")

        lb.bind("<Double-Button-1>", on_select_load)
        ttk.Label(load_win, text="(Double-click to load)", foreground="gray").pack(pady=5)
