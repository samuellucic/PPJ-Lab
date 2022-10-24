class State:
    state_count = 0

    def __init__(self, state_label):
        if state_label:
            self.state_label = state_label
        else:
            self.state_label = self.state_count
            State.state_count += 1

    def __str__(self):
        return self.state_label

    def clear_state_count(self):
        State.state_count = 0


class StatePair:
    def __init__(self, first_state, second_state):
        self.first_state = first_state
        self.second_state = second_state

    def __str__(self):
        return '[' + str(self.first_state) + ' : ' + str(self.second_state) + ']'
