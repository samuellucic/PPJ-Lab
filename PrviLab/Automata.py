from State import State, StatePair


class Automata:
    def __init__(self):
        self.state_count = 0
        self.states = list()
        self.transitions = dict()
        self.lex_state = ""
        self.special_actions = list()

    def __str__(self):
        states = 'Stanja: \n'
        for state in self.states:
            states += (str(state) + ' ')
        transitions = 'Prijelazi: \n'
        for transition in self.transitions:
            transitions += (str(transition) + ' sa znakom ' + repr(self.transitions[transition]) + '\n')
        return states + '\n--------------------\n' + transitions

    def create_state(self):
        self.states.append(State().__str__())
        self.state_count += 1
        return self.states[-1]

    def add_epsilon_transition(self, left_state, right_state):
        self.transitions.update({StatePair(left_state, right_state): 'epsilon'})

    def add_transition(self, left_state, right_state, character):
        self.transitions.update({StatePair(left_state, right_state): character})
