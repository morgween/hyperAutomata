import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from utils.logger import operation_logger, error_logger
from utils.constants import AppMode
class WordsFrame(tk.Frame):
    """
        Displays the list of tapes. Supports adding, editing, and deleting words on double click.
        Prevents deletion while the simulation is running, but can change the word during the run, changed word will run from start
    """
    def __init__(self, parent, run_mgr, tool_window, automata_manager, run_tools):
        super().__init__(parent, bg="#fffde7")
        self.run_mgr = run_mgr
        self.tool_window = tool_window
        self.automata_manager = automata_manager
        self.run_tools = run_tools
        
        ttk.Label(self, text="Words Window", justify='center').pack(pady=5)

        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind("<Double-Button-1>", self.on_click_word)

        ttk.Button(self, text="Add Word", command=self.on_add_word).pack(pady=5)
        operation_logger.info("WordsFrame initialized.")

    def on_add_word(self):
        """ Prompt the user to add a new word. Update word, and word_count """
        w = simpledialog.askstring("Add Word", "Enter a new word:")
        if w:
            try:
                self.run_mgr.add_word(w.strip())
                self.refresh()
                # Update word_count if necessary
                if len(self.run_mgr.words) > self.automata_manager.word_count:
                    self.tool_window.word_count_var.set(len(self.run_mgr.words))
                    self.tool_window.set_word_count()

                # Highlight the current state if simulation is running
                if self.run_mgr.app_mode == AppMode.RUNNING:
                    current_step = self.run_mgr.history[self.run_mgr.current_step] if self.run_mgr.current_step < len(self.run_mgr.history) else None
                    if current_step:
                        self.run_tools.highlight_state(current_step[0])
                operation_logger.info(f"Word added: {w.strip()}")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to add word: {ex}")
                error_logger.error(f"Exception occurred while adding word: {ex}")

    def on_click_word(self):
        """ Handle double-click to edit a selected word. """
        idx = self.listbox.curselection()
        if not idx:
            return
        index = idx[0]
        old_word = self.run_mgr.words[index]
        self.open_edit_window(index, old_word)

    def open_edit_window(self, idx, old_word):
        """ Open a window to edit/delete a selected word. """
        win = tk.Toplevel(self)
        win.title("Edit Word")
        win.geometry("300x120")

        ttk.Label(win, text=f"Current word: {old_word}", justify='center').pack(pady=5)
        new_var = tk.StringVar(value=old_word)
        ttk.Entry(win, textvariable=new_var, justify='center').pack(pady=5)

        def on_change():
            """ Change the selected word after validation. """ 
            new_w = new_var.get().strip()
            if new_w:
                try:
                    self.run_mgr.change_word(idx, new_w)
                    self.refresh()
                    operation_logger.info(f"Word changed at index {idx} to: {new_w}")
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to change word: {ex}")
                    error_logger.error(f"Exception occurred while changing word: {ex}")
            win.destroy()

        def on_delete():
            """ Delete the selected word if the simulation is not running. """ 
            if self.run_mgr.running:
                messagebox.showerror("Error", "Cannot delete a word while the simulation is running.")
                error_logger.warning("Attempted to delete a word during simulation.")
                return
            try:
                self.run_mgr.remove_word(idx)
                self.refresh()
                operation_logger.info(f"Word deleted at index {idx}")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to delete word: {ex}")
                error_logger.error(f"Exception occurred while deleting word: {ex}")
            win.destroy()

        # Buttons for changing and deleting the word
        frm = tk.Frame(win)
        frm.pack(pady=5)
        ttk.Button(frm, text="Change", command=on_change).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm, text="Delete", style="Danger.TButton", command=on_delete).pack(side=tk.LEFT, padx=5)

    def refresh(self):
        """ Refresh the list of words displayed. """ 
        self.listbox.delete(0, tk.END)
        for w in self.run_mgr.words:
            self.listbox.insert(tk.END, w)
        operation_logger.info("WordsFrame refreshed.")

    def tkraise(self, aboveThis=None):
        """ Override tkraise to refresh the list when the frame is raised. """ 
        super().tkraise(aboveThis)
        self.refresh()
