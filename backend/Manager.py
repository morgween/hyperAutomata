from backend.Simulation import Simulation
import copy

from backend.Tape import Tape
from backend.Transition import Transition



class Manager:
    def __init__(self, automata,tapes):
        self.automata = automata           # Instance of Automata
        self.tapes = tapes

        self.accepting_states = automata.accept_states
        self.sim = Simulation(self.tapes)
        self.visited = {self.sim}  #set of visited simulatios
        self.queue = [self.sim] # List of active Simulation objects


    # def stepTo(self,targetState):
    #     #נראה לי שהפונקציה הזו צריכה להיות בSIMULATION
    #     #צריך לשנות את המבנה של האוטומט - המעברים צריכים להיות בסט, ולהוסיף equal לtransition
    #     sim = self.sim
    #     possible_transitions = self.automata.transitions.get(targetState)
    #     '''
    #     check for all the possible_transitions if there is a transition with targetState == targetState:
    #         if there is:
    #             if transition.symbolsVector.matches(tapesCopy):
    #             update current state
    #             update history
    #             create a new simulation
    #     '''
    #     return True



    def mainLoop(self):
        '''
        this method based of BFS algorithm.
        its search a path to an accepting run and if exists return it history, else return the last Simulation's history.
        :return:
        '''
        flag = True
        while any(tape.symbol != '#' for tape in self.tapes) \
                and (len(self.queue))>=0:
            if flag:
                sim = self.queue.pop(0)
                self.tapes = sim.tapes
                flag = False



            for transition in self.automata.transitions.get(sim.currentState):
                history = sim.history.copy()
                tapesCopy = copy.deepcopy(self.tapes)
                if transition.symbolsVector.matches(tapesCopy):

                    current_state = transition.targetState
                    historySnapShot = []
                    historySnapShot.append(current_state)

                    for tape in tapesCopy:
                        historySnapShot.append(tape.currentPos)

                    history.append(historySnapShot)
                    newSim = Simulation(tapesCopy, history, current_state)
                    if newSim in self.visited:
                        continue
                    else:
                        self.visited.add(newSim)
                        self.queue.append(newSim)

            sim = self.queue.pop(0)
            self.tapes = sim.tapes
            if (sim.currentState in self.accepting_states) and (all(tape.symbol == '#' for tape in self.tapes)):
                return sim.history


        return sim.history


    def addTape(self, tape, history):
        '''
        this method gets the tape tou user would like to add, and the history from where he stop the run.
        it ask the user to redifine the transitions, and call mainLoop the fine a path to accepting state...
        '''
        automata = self.automata
        for char in tape:
            if char not in automata.alphabet:
                print("The tape is not valid: at least one of its char is not in the alphabet")
                return
        self.setTapes(history[-1])
        self.tapes.append(Tape(tape))

        # automata.transitions = {}
        # k = len(self.tapes)
        # print()
        # print("set transitions:")
        # # automata.add_transition(Transition(0, ['1', '#', '#'], 1))
        # # automata.add_transition(Transition(0, ['0', '#', '#'], 0))
        # # automata.add_transition(Transition(0, ['#', '1', '#'], 1))
        # # automata.add_transition(Transition(0, ['#', '0', '#'], 0))
        # # automata.add_transition(Transition(0, ['#', '#', '1'], 1))
        # # automata.add_transition(Transition(0, ['#', '#', '0'], 0))
        # # automata.add_transition(Transition(1, ['1', '#', '#'], 0))
        # # automata.add_transition(Transition(1, ['0', '#', '#'], 1))
        # # automata.add_transition(Transition(1, ['#', '1', '#'], 0))
        # # automata.add_transition(Transition(1, ['#', '0', '#'], 1))
        # # automata.add_transition(Transition(1, ['#', '#', '1'], 0))
        # # automata.add_transition(Transition(1, ['#', '#', '0'], 1))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # automata.add_transition(Transition(k, automata.alphabet))
        # '''edit automata screen
        #     eventListener -> addTransitions        
        # '''
        
        """Made function from this part."""
    def update(self,history):
        sim = Simulation(self.tapes,history,history[-1][0])
        self.visited = {sim}  # empty visited
        self.queue = [sim]  # empty queue
        self.sim = sim
        h = self.mainLoop()
        return h

    def setTapes(self, snapShot):
        snapShot = snapShot[1:]
        for i in range(len(snapShot)):
            self.tapes[i].currentPos = snapShot[i]
            if(snapShot[i] >= len(self.tapes[i].symbols)):
                self.tapes[i].symbol = '#'
            else:
                self.tapes[i].symbol = self.tapes[i].symbols[snapShot[i]]
        return

    def stepBack(self,history):
        #מחזירים את ההיסטוריה צעד אחד אחורה
        #מעדכנים את המיקומים בטייפים בהתאם להיסטוריה האחרונה
        history.pop()
        snapShot = history[-1]
        currentState = snapShot[0]
        tapes = self.setTapes(snapShot)
        sim = Simulation(tapes, history, currentState)
        #להסגר על פונקציונליות רצויה ולשכתב את הפוקנציה. לאחר מכן לבדוק.




