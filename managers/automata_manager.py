from components.state import State
from components.transition import Transition as GTransition
from utils.logger import operation_logger

class AutomataManager:
    """ Manages the GUI states & transitions. 'word_count' = # of symbols per transition vector. """
    def __init__(self):
        self.states = []
        self.transitions = []
        self.word_count = 1
        operation_logger.info("AutomataManager initialized.")

    def add_state(self, name, x, y, is_start=False, is_accept=False):
        """ Add a new state to the automata. """
        st = State(name, x, y, is_start, is_accept)
        self.states.append(st)
        operation_logger.info(f"State added to AutomataManager: {name}")
        return st

    def add_transition(self, src, tgt, vectors):
        """ Add a new transition to the automata. """
        tr = GTransition(src, tgt, vectors)
        self.transitions.append(tr)
        operation_logger.info(f"Transition added to AutomataManager: {src.name} -> {tgt.name}")
        return tr

    def set_word_count(self, new_count):
        """ Set the number of symbols per transition vector and adjust existing transitions. """
        self.word_count = new_count
        for tr in self.transitions:
            new_vecs = []
            for vec in tr.transition_vectors:
                lst = list(vec)
                if len(lst) < new_count:
                    lst += ['#'] * (new_count - len(lst))
                elif len(lst) > new_count:
                    lst = lst[:new_count]
                new_vecs.append(tuple(lst))
            tr.transition_vectors = new_vecs
        operation_logger.info(f"Word count set to: {new_count}")

    def draw_all(self, canvas):
        """ Draw all states and transitions on the canvas. """
        canvas.delete("all")
        for s in self.states:
            s.draw(canvas)
        for t in self.transitions:
            t.draw(canvas)
        operation_logger.info("All states and transitions drawn on the canvas.")
