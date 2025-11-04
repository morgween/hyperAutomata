class SymbolVector:
    #אם מוסיפים מילה , כלומר טייפ חדש, צריך לעדכן את הווקטור, פשוט עושים אפנד לווקטור עם האות המתאימה
    # def __init__(self, vector):
    #     # self.size = size
    #     self.vector = vector

    # def __init__(self,k, alphabeta):
    #     '''k is amount of words'''
    #     self.vector = []
    #     for i in range(k):
    #         symbol = input(f"please enter symbol to read from word {i+1}: ")
    #         while(symbol not in alphabeta and symbol != '#'):
    #             print("please choose a symbol from the alphabeta:")
    #             print(alphabeta)
    #             symbol = input(f"please enter symbol to read from word {i+1}: ")
    #         self.vector.append(symbol)
    def __init__(self, vector):
        # self.size = size
        self.vector = vector


    def __iter__(self):
        return iter(self.vector)


    def matches(self, tapes):
        '''
        get Tapes and return true if there is a match between itself(SimbolVector) and zip vector of the Tapes.
        '''
        tapesLog = tapes.copy()
        tapesSymbols = [tape.symbol for tape in tapes]
        i = 0

        for sv, tp in zip(self.vector, tapesSymbols):
            if (sv == '#'):
                i += 1
                continue
            elif (sv == tp):
                tapes[i].read()
                i += 1

            else:
                tapes = tapesLog
                return False
        return True


    # def addSymbol(self, symbol):
    #     self.vector.append(symbol)

    # def edit(self, k, alphabeta):
    #     '''k is amount of words'''
    #     self.vector = []
    #     for i in range(k):
    #         symbol = input(f"please enter symbol to read from word {i}")
    #         while(symbol not in alphabeta):
    #             print("please choose a symbol from the alphabeta:")
    #             print(alphabeta)
    #             symbol = input(f"please enter symbol to read from word {i}")
    #         self.vector.append(symbol)