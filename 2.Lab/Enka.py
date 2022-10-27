from State import State, StatePair


class Enka:
    def __init__(self):
        self.state_count = 0
        self.states = list()
        self.transitions = dict()

    def __str__(self):
        states = 'Stanja: \n'
        for state in self.states:
            states += (str(state) + '\n')
        states = states.strip()
        transitions = 'Prijelazi: \n'
        for transition in self.transitions:
            transitions += (str(transition) + ' with ' + repr(self.transitions[transition]) + '\n')
        transitions = transitions.strip()
        return states + '\n--------------------\n' + transitions

    def create_state(self, state_label):
        self.states.append(State(state_label).__str__())
        self.state_count += 1
        return self.states[-1]

    def add_epsilon_transition(self, left_state, right_state):
        if left_state not in self.states:
            raise Exception('Left state doesn\'t exist.')
        if right_state not in self.states:
            raise Exception('Right state doesn\'t exist.')
        self.transitions.update({StatePair(left_state, right_state): 'epsilon'})

    def add_transition(self, left_state, right_state, character):
        if left_state not in self.states:
            raise Exception('Left state doesn\'t exist.')
        if right_state not in self.states:
            raise Exception('Right state doesn\'t exist.')
        self.transitions.update({StatePair(left_state, right_state): character})
