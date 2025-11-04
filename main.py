import tkinter as tk
from tkinter import ttk
from db_integration import DBManager
import traceback

from components.panels.draw_tools import ToolsFrame
from components.panels.run_tools import RunToolsFrame
from components.panels.words import WordsFrame
from components.panels.current_setup import CurrentSetupFrame

from components.login_window import LoginWindow
from components.drawing_board import DrawingBoard

from managers.run_manager import RunManager
from managers.automata_manager import AutomataManager

from utils.logger import operation_logger, error_logger

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hyper Automata")
        self.geometry("1300x800")
        operation_logger.info("Application started.")

        # Initialize current_user after login
        self.current_user = None

        # Initialize Database Manager
        self.db_manager = DBManager(db_url="sqlite:///demo.db")

        # Launch Login Window
        self.login_window = LoginWindow(self, self.db_manager)
        self.wait_window(self.login_window)

        # If the user closed the login, the app ends
        if not self.current_user:
            operation_logger.info("Application terminated by user during login.")
            return  # user closed or never logged in

        # Continue building main GUI
        self.automata_mgr = AutomataManager()
        self.run_mgr = RunManager(
            automata_manager=self.automata_mgr,
            db_manager=self.db_manager,
            current_user=self.current_user
        )

        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize Drawing Board
        self.canvas = DrawingBoard(self, bg="white", width=900, height=700)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Initialize Tools Panel
        self.tools_panel = ToolsFrame(
            parent=self,
            automata_mgr=self.automata_mgr,
            canvas=self.canvas,
            undo_stack=self.undo_stack,
            redo_stack=self.redo_stack
        )
        self.tools_panel.grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        # Initialize Bottom Frame
        self.bottom_frame = ttk.Frame(self, style="Background.TFrame")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.columnconfigure(2, weight=1)

        # Initialize Run Tools
        self.run_tools = RunToolsFrame(
            parent=self.bottom_frame,
            run_mgr=self.run_mgr,
            canvas=self.canvas
        )
        self.run_tools.grid(row=0, column=0, sticky="nsew")

        # Initialize Words Window
        self.words_window = WordsFrame(
            parent=self.bottom_frame,
            run_mgr=self.run_mgr,
            tool_window=self.tools_panel,
            automata_manager=self.automata_mgr,
            run_tools=self.run_tools
        )
        self.words_window.grid(row=0, column=1, sticky="nsew")

        # Initialize Current Setup Window
        self.current_setup = CurrentSetupFrame(
            parent=self.bottom_frame,
            run_mgr=self.run_mgr,
            canvas=self.canvas
        )
        self.current_setup.grid(row=0, column=2, sticky="nsew")

        # Set Cross-references
        self.run_tools.set_current_setup(self.current_setup)
        self.run_tools.set_words_window_ref(self.words_window)
        self.run_tools.set_tools_panel_ref(self.tools_panel)

        # Link selection tool to run_mgr for partial BFS updates
        if "Selection" in self.tools_panel.tools:
            _, selection_tool = self.tools_panel.tools["Selection"]
            selection_tool.run_mgr = self.run_mgr

        operation_logger.info("Main GUI initialized.")

def main():
    try:
        app = MainApplication()
        app.mainloop()
    except Exception as e:
        error_message = f"Critical error occurred: {str(e)}"
        error_logger.critical(f"{error_message}\n{traceback.format_exc()}")
        
        # Show error dialog to user
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        show_error_dialog(error_message)
        root.destroy()
        
        return 1  # Return error code
    finally:
        operation_logger.info("Application closed.")
        
    return 0  # Return success code
        

def show_error_dialog(error_message):
    """ Error occured during program run. """
    error_window = tk.Toplevel()
    error_window.title("Error")
    error_window.geometry("400x200")
    
    label = tk.Label(error_window, text=error_message, wraplength=350)
    label.pack(padx=20, pady=20)
    
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
    ok_button.pack(pady=10)
    
    
if __name__ == "__main__":
    main()
    operation_logger.info("Application closed.")
