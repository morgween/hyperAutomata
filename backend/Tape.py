
class Tape:
    def __init__(self, symbols):
        self.symbols = symbols
        self.currentPos = 0
        self.symbol = symbols[0]


    def read(self):
        '''
        this method responsible for advancing the currentPosition of the tape and the current symbol to read.
        '''
        if self.currentPos < len(self.symbols):
            self.currentPos += 1
            if self.currentPos <len(self.symbols):
                self.symbol = self.symbols[self.currentPos]
            else:
                self.symbol = '#'

        else:
            self.symbol = '#'
