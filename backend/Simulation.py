
class Simulation:
    '''
    this class is represents a a snap shot of a situation in the automata
    '''
    def __init__(self, tapes, history = None, currentState = 0):
        self.currentState = currentState
        self.tapes = tapes
        self.history = history if history is not None else [[0] * (len(tapes) + 1)]
        self.id = self.__hash__()

    def __hash__(self):
        return hash(tuple(self.history[-1]))

    def __eq__(self, other):
        return self.id == other.id








