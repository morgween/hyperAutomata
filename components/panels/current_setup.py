import tkinter as tk
from tkinter import ttk
from utils.constants import COLOR_RED, COLOR_GREEN, COLOR_CS_BG, EMPTY_SETUP
from utils.logger import operation_logger

class CurrentSetupFrame(tk.Frame):
    """ Displays current simulation history step and highlights tapes in green if fully read. """
    def __init__(self, parent, run_mgr, canvas):
        super().__init__(parent, bg=COLOR_CS_BG)
        self.run_mgr = run_mgr
        self.canvas = canvas

        ttk.Label(self, text="Current Setup", justify='center').pack(pady=5)
        self.state_label = ttk.Label(self, text="State: - ", justify='center')
        self.state_label.pack(pady=5)

        self.tapes_text = tk.Text(self, height=6, width=40, state=tk.DISABLED)
        self.tapes_text.pack(pady=5, padx=5)

        # Configure text tags for coloring
        self.tapes_text.tag_config("red_char", foreground=COLOR_RED)
        self.tapes_text.tag_config("green_text", foreground=COLOR_GREEN)

    def display_step(self, step):
        """  Update Current Setup display based on the current history step. """
        self.tapes_text.config(state=tk.NORMAL)
        self.tapes_text.delete("1.0", tk.END)

        if not step:
            self.state_label.config(text=EMPTY_SETUP)
            self.tapes_text.config(state=tk.DISABLED)
            operation_logger.info("Displayed unknown state in CurrentSetupFrame.")
            return

        state_name = step[0]
        self.state_label.config(text=f"State: {state_name}")
        tape_positions = step[1:]
        if len(tape_positions) < len(self.run_mgr.words):
            tape_positions += [0] * (len(self.run_mgr.words) - len(tape_positions))

        for i, word in enumerate(self.run_mgr.words):
            pos = tape_positions[i]
            self.tapes_text.insert(tk.END, f"Tape {i+1}: ")

            if pos >= len(word):
                # Entire tape read; color green
                self.tapes_text.insert(tk.END, word + "\n", "green_text")
            else:
                # Partial highlight; current character in red
                for j, ch in enumerate(word):
                    if j == pos:
                        self.tapes_text.insert(tk.END, ch, "red_char")
                    else:
                        self.tapes_text.insert(tk.END, ch)
                self.tapes_text.insert(tk.END, "\n")
        self.tapes_text.config(state=tk.DISABLED)
        operation_logger.info(f"Displayed step in CurrentSetupFrame: State={state_name}")
