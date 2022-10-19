from util import is_operator

def transform(expression, automata):
    options = []
    brackets_cnt = 0
    start_ind = 0
    for i in range(len(expression)):
        if expression[i] == '(' and is_operator(expression, i):
            brackets_cnt += 1
        elif expression[i] == ')' and is_operator(expression, i):
            brackets_cnt -= 1
        elif brackets_cnt == 0 and expression[i] == '|' and is_operator(expression, i):
            options.append(expression[start_ind:i])
            start_ind = i + 1
    if options:
        options.append(expression[start_ind:])

    left_state = automata.create_state()
    right_state = automata.create_state()

    if options:
        for i in range(len(options)):
            #print(options[i])
            temp_left, temp_right = transform(options[i], automata)
            automata.add_epsilon_transition(left_state, temp_left)
            automata.add_epsilon_transition(temp_right, right_state)
    else:
        prefix = False
        last_state = left_state
        i = 0
        while i < len(expression):
            #print(str(i) + ' ' + str(expression[i]))
            a = None
            b = None
            if prefix:
                prefix = False
                transitional_char = None
                if expression[i] == 't':
                    transitional_char = '\t'
                elif expression[i] == 'n':
                    transitional_char = '\n'
                elif expression[i] == '_':
                    transitional_char = ' '
                else:
                    transitional_char = expression[i]
                a = automata.create_state()
                b = automata.create_state()
                automata.add_transition(a, b, transitional_char)
            else:
                if expression[i] == '\\':
                    prefix = True
                    i += 1
                    continue
                if expression[i] != '(':
                    a = automata.create_state()
                    b = automata.create_state()
                    if expression[i] == '$':
                        automata.add_epsilon_transition(a, b)
                    else:
                        automata.add_transition(a, b, expression[i])
                else:
                    j = None
                    brackets_cnt = 0
                    for k in range(i, len(expression)):
                        if expression[k] == '(' and is_operator(expression, k):
                            brackets_cnt += 1
                        elif expression[k] == ')' and is_operator(expression, k):
                            brackets_cnt -= 1
                        if brackets_cnt == 0:
                            j = k
                            break
                    # find matching closing parentheses
                    temp_left, temp_right = transform(expression[i+1:j], automata)
                    a = temp_left
                    b = temp_right
                    i = j
            if i + 1 < len(expression) and expression[i + 1] == '*':
                x = a
                y = b
                a = automata.create_state()
                b = automata.create_state()
                automata.add_epsilon_transition(a, x)
                automata.add_epsilon_transition(y, b)
                automata.add_epsilon_transition(a, b)
                automata.add_epsilon_transition(y, x)
                i += 1
            automata.add_epsilon_transition(last_state, a)
            last_state = b
            i += 1
        automata.add_epsilon_transition(last_state, right_state)
    return left_state, right_state
