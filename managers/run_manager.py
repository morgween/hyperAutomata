import copy
from tkinter import messagebox
from backend.Automata import Automata
from backend.Manager import Manager
from backend.Tape import Tape
from backend.SymbolVector import SymbolVector
from backend.Transition import Transition
from utils.logger import operation_logger, error_logger
from utils.constants import AppMode  

class RunManager:
    """
        Coordinates BFS logic, partial BFS updates, user actions (word add/remove),
        DB saving/loading, and tracks app_mode: 'drawing'/'running'.
    """
    def __init__(self, automata_manager, db_manager, current_user):
        self.automata_manager = automata_manager
        self.db_manager = db_manager
        self.current_user = current_user

        self.words = []
        self.history = []
        self.current_step = 0
        self.manager = None

        self.running = False
        self.updated_during_run = False
        self.history_backup = []
        self.updated_transitions = False
        self.app_mode = AppMode.DRAWING 
        
        operation_logger.info(f"RunManager initialized for user: {self.current_user}")

    def initialize_backend(self):
        """ Initialize the backend automata and manager based on current states and transitions. """
        try:
            automata = Automata()
            for gui_state in self.automata_manager.states:
                automata.add_state(gui_state.name, is_accept=gui_state.is_accept)
                if gui_state.is_start:
                    automata.set_start_state(gui_state.name)

            for gui_tr in self.automata_manager.transitions:
                source = gui_tr.source.name
                target = gui_tr.target.name
                for vec in gui_tr.transition_vectors:
                    sym_vec = SymbolVector(list(vec))
                    for c in vec:
                        automata.alphabet.add(c)
                    b_tr = Transition(fromState=source, symbols_vector=sym_vec, targetState=target)
                    automata.add_transition(b_tr)

            tapes = [Tape(w) for w in self.words]
            self.manager = Manager(automata, tapes)
            operation_logger.info("Backend Automata and Manager initialized.")

            if automata.start_state is None:
                self.history = []
                self.current_step = 0
                operation_logger.warning("Automata has no start state. History cleared.")
            else:
                snap = [automata.start_state] + [0] * len(tapes)
                self.history = self.manager.update([snap])
                self.current_step = 0
                operation_logger.info("Initial history snapshot created.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize backend: {e}")
            error_logger.error(f"Failed to initialize backend: {e}")

    def load_history(self):
        """ Return the current history. """
        operation_logger.debug("History loaded.")
        return self.history

    def __update_run_history(self, new_word=True):
        """ Update the run history when words are added or removed during a run. """
        self.history_backup = self.history[:self.current_step]
        for snap in self.history_backup:
            while len(snap) < (len(self.words) + 1):
                if new_word:
                    snap.append(0)
                else:
                    break
        self.updated_during_run = True
        operation_logger.debug("Run history updated during run.")

    def simulate_from_updated_history(self):
        """ Simulate BFS steps from the updated history backup. """
        if not self.manager or not self.history_backup:
            return

        last_snap = self.history_backup[-1]
        positions = last_snap[1:]
        for i, tape in enumerate(self.manager.tapes):
            if i < len(positions):
                pos = positions[i]
                tape.currentPos = pos
                tape.symbol = tape.symbols[pos] if pos < len(tape.symbols) else '#'

        self.history = self.manager.update(copy.deepcopy(self.history_backup))
        self.current_step = len(self.history_backup)
        self.updated_during_run = False
        operation_logger.debug("Simulated BFS from updated history.")

    def add_word(self, new_word):
        """ Add a new word to the simulation. """
        if not new_word:
            return
        self.words.append(new_word)
        operation_logger.info(f"Word added: {new_word}")
        if self.running:
            self.__update_run_history(new_word=True)
            self.simulate_from_updated_history()
            if self.manager:
                self.manager.tapes.append(Tape(new_word))
                operation_logger.info(f"Word added to manager tapes: {new_word}")

    def change_word(self, idx, new_word):
        """ Change an existing word in the simulation. """
        if 0 <= idx < len(self.words):
            old_word = self.words[idx]
            self.words[idx] = new_word
            operation_logger.info(f"Word changed from {old_word} to {new_word} at index {idx}")
            if self.running:
                partial = self.history[:self.current_step]
                if partial:
                    last_snap = partial[-1]
                    if (idx + 1) < len(last_snap):
                        last_snap[idx + 1] = 0
                self.history_backup = partial
                if self.manager:
                    self.manager.tapes[idx].symbols = new_word
                self.simulate_from_updated_history()

    def remove_word(self, idx=None):
        """ Remove a word from the simulation. """
        if not self.words:
            return
        if idx is None or idx >= len(self.words):
            removed_word = self.words.pop()
            if self.manager and self.manager.tapes:
                self.manager.tapes.pop()
            operation_logger.info(f"Word removed: {removed_word}")
        else:
            removed_word = self.words.pop(idx)
            if self.manager and idx < len(self.manager.tapes):
                self.manager.tapes.pop(idx)
            operation_logger.info(f"Word removed at index {idx}: {removed_word}")

        if self.running:
            self.__update_run_history(new_word=False)
            self.simulate_from_updated_history()

    def step(self):
        """ Perform a single step in the BFS simulation. """
        self.running = True
        self.app_mode = AppMode.RUNNING
        if self.updated_transitions:
            self.update_transitions_in_backend()
            self.updated_transitions = False

        if self.current_step < len(self.history):
            snap = self.history[self.current_step]
            self.current_step += 1
            operation_logger.debug(f"BFS step performed: {snap}")
            return snap
        else:
            self.running = False
            self.app_mode = AppMode.DRAWING
            operation_logger.info("BFS simulation completed all steps.")
            return None

    def is_accepted(self):
        """ Check if the BFS simulation ended in an accepting state. """
        if not self.history:
            return False
        last_snap = self.history[-1]
        last_state = last_snap[0]
        if last_state in self.manager.automata.accept_states:
            # Check if all tapes are fully read
            for i, pos in enumerate(last_snap[1:]):
                tape = self.manager.tapes[i]
                if pos < len(tape.symbols):
                    return False
            return True
        return False

    def pause(self):
        """ Pause the BFS simulation. """
        self.running = False
        operation_logger.info("BFS simulation paused.")

    def resume(self):
        """ Resume the BFS simulation. """
        self.running = True
        self.app_mode = AppMode.RUNNING
        if self.updated_during_run:
            self.simulate_from_updated_history()
        operation_logger.info("BFS simulation resumed.")

    def restart(self):
        """ Restart the BFS simulation. """
        self.history.clear()
        self.current_step = 0
        self.running = False
        self.updated_during_run = False
        self.app_mode = AppMode.DRAWING
        operation_logger.info("BFS simulation restarted.")

    def clear_all(self):
        """ Clear all data from the simulation. """
        self.words.clear()
        self.automata_manager.states.clear()
        self.automata_manager.transitions.clear()
        self.automata_manager.word_count = 1
        self.history.clear()
        self.current_step = 0
        self.running = False
        self.updated_during_run = False
        self.app_mode = AppMode.DRAWING
        operation_logger.info("All simulation data cleared.")

    def update_transitions_in_backend(self):
        """ Update transitions in the backend Automata based on GUI transitions. """
        if not self.manager or not self.manager.automata:
            return
        self.manager.automata.transitions.clear()
        self.history_backup = self.history[:self.current_step]

        for gui_tr in self.automata_manager.transitions:
            source = gui_tr.source.name
            target = gui_tr.target.name
            for vec in gui_tr.transition_vectors:
                sym_vec = SymbolVector(list(vec))
                for c in vec:
                    self.manager.automata.alphabet.add(c)
                b_tr = Transition(fromState=source, symbols_vector=sym_vec, targetState=target)
                self.manager.automata.add_transition(b_tr)
        operation_logger.info("Backend transitions updated based on GUI.")

        self.simulate_from_updated_history()

    def save_current_run(self, description=""):
        """ Save the current run history to the database. Serialize the run. """
        try:
            st_list = []
            for s in self.automata_manager.states:
                st_list.append({
                    'name': s.name,
                    'x': s.x,
                    'y': s.y,
                    'is_start': s.is_start,
                    'is_accept': s.is_accept
                })
            tr_list = []
            for tr in (self.manager.automata.transitions if self.manager else self.automata_manager.transitions):
                tr_list.append({
                    'source': (tr.fromState if self.manager else tr.source.name),
                    'target': (tr.targetState if self.manager else tr.target.name),
                    'vectors': (tr.symbolsVector.vector if self.manager else tr.transition_vectors)
                })

            automaton_data = {
                'states': st_list,
                'transitions': tr_list,
                'word_count': self.automata_manager.word_count,
                'words': self.words
            }
            history_data = self.history
            self.db_manager.save_run_history(
                username=self.current_user,
                automaton_data=automaton_data,
                history_data=history_data,
                description=description
            )
            operation_logger.info(f"Run history saved with description: {description}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save run history: {e}")
            error_logger.error(f"Exception occurred while saving run history: {e}")

    def load_run(self, automaton_data, history_data):
        """ Load a run history from the database. Unserializing the data"""
        try:
            self.words.clear()
            self.automata_manager.states.clear()
            self.automata_manager.transitions.clear()

            for st in automaton_data['states']:
                self.automata_manager.add_state(
                    name=st['name'],
                    x=st['x'],
                    y=st['y'],
                    is_start=st['is_start'],
                    is_accept=st['is_accept']
                )
            for tdata in automaton_data['transitions']:
                src = None
                tgt = None
                for s in self.automata_manager.states:
                    if s.name == tdata['source']:
                        src = s
                    if s.name == tdata['target']:
                        tgt = s
                if src and tgt:
                    self.automata_manager.add_transition(src, tgt, [tuple(tdata['vectors'])])

            self.words = automaton_data.get('words', [])
            wc = automaton_data.get('word_count', 1)
            self.automata_manager.set_word_count(wc)

            self.history = history_data
            self.current_step = 0
            self.running = False
            self.app_mode = AppMode.DRAWING
            operation_logger.info("Run history loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load run history: {e}")
            error_logger.error(f"Exception occurred while loading run history: {e}")
