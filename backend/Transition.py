from backend.SymbolVector import SymbolVector


class Transition:
    def __init__(self, fromState, symbols_vector, targetState):
        self.symbolsVector = symbols_vector
        self.targetState = targetState
        self.fromState = fromState

    # def __init__(self, k,alphabeta,fromState=None, targetState=None):
    #     print("ADD TRANSITION")
    #     self.fromState = int(input("please enter from state: "))
    #     self.targetState = int(input("please enter target state:"))
    #     self.symbolsVector = SymbolVector(k, alphabeta)

    def __repr__(self):
        return f"Transition({self.fromState} -> {self.targetState}, vec={self.symbolsVector})"



