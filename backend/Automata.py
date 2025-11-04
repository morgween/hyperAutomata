from backend.SymbolVector import SymbolVector
from backend.Transition import Transition


class Automata:
    def __init__(self):
        self.states = set()  # Set of states
        self.alphabet = set()  # Input symbols
        self.transitions = {}  # State transitions
        self.start_state = None
        self.accept_states = set()

    def add_state(self, state, is_accept=False):
        self.states.add(state)
        if is_accept:
            self.accept_states.add(state)

    def set_start_state(self, state):
        self.start_state = state
        self.states.add(state)

    def add_transition(self, transition):
        if transition.fromState not in self.transitions:
            self.transitions[transition.fromState] = []
        self.transitions[transition.fromState].append(transition)
    
    def rename_state(self, old_name, new_name):
        """
        Utility function to rename a state in this automaton.
        """
        if old_name == new_name:
            return
        if old_name in self.states:
            self.states.remove(old_name)
            self.states.add(new_name)
        if old_name in self.accept_states:
            self.accept_states.remove(old_name)
            self.accept_states.add(new_name)
        if old_name == self.start_state:
            self.start_state = new_name
        # Update transitions
        if old_name in self.transitions:
            self.transitions[new_name] = self.transitions.pop(old_name)
            for tr in self.transitions[new_name]:
                tr.fromState = new_name
        for fr, tr_list in self.transitions.items():
            for tr in tr_list:
                if tr.targetState == old_name:
                    tr.targetState = new_name
