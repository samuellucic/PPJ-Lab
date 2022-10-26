from State import StatePair


class Nka:
    def __init__(self):
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

    def add_transition(self, left_state, right_state, character):
        if left_state not in self.states:
            raise Exception('Left state doesn\'t exist.')
        if right_state not in self.states:
            raise Exception('Right state doesn\'t exist.')
        self.transitions.update({StatePair(left_state, right_state): character})