from State import State, StatePair


class Automata:
    def __init__(self):
        self.state_count = 0
        self.states = []
        self.transitions = {}

    def create_state(self):
        self.states.append(State().__str__())
        self.state_count += 1
        return self.states[-1]

    def add_epsilon_transition(self, left_state, right_state):
        self.transitions.update({StatePair(left_state, right_state): '$'})

    def add_transition(self, left_state, right_state, character):
        self.transitions.update({StatePair(left_state, right_state): character})
