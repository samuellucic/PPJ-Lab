from sys import stdin
import re

#import numpy as np
#from json import dump

from Enka import Enka
from Grammar import Grammar
from State import StatePair
from Dka import Dka
from Table import Table


if __name__ == '__main__':

    #Parsing input data
    nonfinal = input().strip()
    nonfinal_chars = nonfinal.split(" ")[1:]
    nonfinal_chars.insert(0, '<%>')
    starting_char = nonfinal_chars[0]

    final = input().strip()
    final_chars = final.split(" ")[1:]

    syn = input().strip()
    syn_chars = syn.split(" ")[1:]

    #Creating a grammar container
    grammar = Grammar(starting_char, nonfinal_chars, final_chars, syn_chars)

    #Parsing productions
    grammar.add_production(nonfinal_chars[0], nonfinal_chars[1])
    for line in stdin:
        if line[0] == '<':
            left_side = line.strip()
        else:
            grammar.add_production(left_side, line.strip())

    #print(grammar)

    #Determine empty characters
    empty_chars = list()
    productions = grammar.productions
    changed = True
    while changed:
        changed = False
        for production in productions:
            for right_side in productions[production]:
                if (right_side == '$' or all(x in empty_chars for x in right_side.split(' '))) and production not in empty_chars:
                    empty_chars.append(production)
                    changed = True

    #print(empty_chars)

    #Calculate startsDirectlyWith table
    final_cnt = len(grammar.final_chars)
    nonfinal_cnt = len(grammar.nonfinal_chars)
    no_of_chars = final_cnt + nonfinal_cnt
    starts_with = [ [0] * no_of_chars for i in range(no_of_chars)]
    
    for production in productions:
        left_ind = grammar.nonfinal_chars.index(production)
        for right_side in productions[production]:
            for char in right_side.split(' '):
                if (char != '$'):
                    right_ind = grammar.nonfinal_chars.index(char) if char in grammar.nonfinal_chars else grammar.final_chars.index(char) + nonfinal_cnt
                    starts_with[left_ind][right_ind] = 1
                    if (char not in empty_chars):
                        break

    for i in range(no_of_chars):
        for j in range(no_of_chars):
            if i == j:
                starts_with[i][j] = 1

    #print(np.matrix(starts_with))

    #Calculate startsWith table
    for i in range(nonfinal_cnt):
        for j in range(no_of_chars):
            if starts_with[i][j] == 1 and i != j:
                for k in range(no_of_chars):
                    if starts_with[j][k] == 1:
                        starts_with[i][k] = 1

    #print(np.matrix(starts_with))

    #Calculate startsWith dict
    startsWithDict = dict()
    for i in range(no_of_chars):
        left_char = grammar.nonfinal_chars[i] if i < nonfinal_cnt else grammar.final_chars[i - nonfinal_cnt]
        for j in range(no_of_chars):
            if starts_with[i][j] == 1 and i != j:
                right_char = grammar.nonfinal_chars[j] if j < nonfinal_cnt else grammar.final_chars[j - nonfinal_cnt]
                if right_char not in grammar.final_chars:
                    continue
                if left_char in startsWithDict.keys():
                    startsWithDict[left_char].extend([right_char])
                else:
                    startsWithDict[left_char] = [right_char]

    for char in final_chars:
        startsWithDict[char] = [char]
    #print(startsWithDict)

    #Calculate lr0 units
    lr0_units = list()
    for production in productions:
        for right_side in productions[production]:
            if (right_side == '$'):
                lr0_units.append(production + '->*')
            else:
                lr0_units.append(production + '->*' + right_side)
                indices = [m.start() for m in re.finditer(' ', right_side)]
                for index in indices:
                    lr0_units.append(production + '->' + (right_side[:index] + '*' + right_side[index+1:]))
                lr0_units.append(production + '->' + right_side + '*')

    #print(lr0_units)

    #Calculate lr1 units
    enka = Enka()
    enka.create_state('q0')
    enka.create_state(lr0_units[0] + ' ; {#}')
    enka.add_epsilon_transition('q0', lr0_units[0] + ' ; {#}')

    #print(enka)

    def create_enka(enka, lr0_units, parent_transition):
        #Find next character
        parent_transition_new, parent_set = parent_transition.split(' ; ')
        dot_index = parent_transition_new.find('*')
        leftover_string = parent_transition_new[dot_index + 1:]
        if (leftover_string == ''):
            return
        next_char = parent_transition_new[dot_index + 1:].split(' ')[0]
        rest_of_string = parent_transition_new[dot_index + 1:].split(' ')[1:]
        rest_of_string = '' if rest_of_string == [] else rest_of_string
        
        #Move dot in expression
        space_index = leftover_string.find(' ')
        if (space_index == -1):
            leftover_string += '*'
        else:
            leftover_string = leftover_string[:space_index] + '*' + leftover_string[space_index + 1:]

        if parent_transition_new[dot_index - 2: dot_index] == '->':
            final_transition = parent_transition_new[:dot_index] + leftover_string
        else:
            final_transition = parent_transition_new[:dot_index] + ' ' + leftover_string
        #print(final_transition)
        
        if next_char in grammar.nonfinal_chars or next_char in grammar.final_chars:
            lr1_unit = final_transition + ' ; ' + parent_set
            #print(lr1_unit)          
            if lr1_unit not in enka.states:
                enka.create_state(lr1_unit)
                enka.add_transition(parent_transition, lr1_unit, next_char)
                create_enka(enka, lr0_units, lr1_unit)

        if next_char in grammar.nonfinal_chars:
            for unit in lr0_units:
                if unit.startswith(next_char + '->*'):
                    #print(rest_of_string)
                    #add eps trans
                    if rest_of_string == '':
                        lr1_unit = unit + ' ; ' + parent_set
                        if lr1_unit not in enka.states:
                            enka.create_state(lr1_unit)
                            enka.add_epsilon_transition(parent_transition, lr1_unit)
                            create_enka(enka, lr0_units, lr1_unit)
                        else:
                            enka.add_epsilon_transition(parent_transition, lr1_unit)
                    else:
                        foundNonEmpty = False
                        for char in rest_of_string:
                            if char not in empty_chars:
                                foundNonEmpty = True
                                break   
                        additional_chars = set()
                        for char in rest_of_string:
                            additional_chars.update(startsWithDict[char])
                            if char not in empty_chars:
                                break
                        if not foundNonEmpty:
                            additional_chars = additional_chars.union(set(parent_set[1:-1].split(',')))
                        
                        lr1_unit = unit + ' ; ' + str(additional_chars).replace(' ', '')
                        if lr1_unit not in enka.states:
                            enka.create_state(lr1_unit)
                            enka.add_epsilon_transition(parent_transition, lr1_unit)
                            create_enka(enka, lr0_units, lr1_unit)
                        else:
                            enka.add_epsilon_transition(parent_transition, lr1_unit)

    create_enka(enka, lr0_units, enka.states[-1])
    print(enka)
    #print(enka.state_count)
    #print(len(enka.transitions))
    #print(lr0_units)

    def get_epsilon_closure(stack: set) -> set:
        epsilon_closure = stack.copy()

        while stack:
            state_t = stack.pop()

            for state_v in [state_v for state_v in states if transitions.get(StatePair(state_t, state_v)) == "epsilon"]:
                if state_v not in epsilon_closure:
                    epsilon_closure.add(state_v)
                    stack.add(state_v)

        return epsilon_closure

    states = enka.states
    transitions = enka.transitions
    symbols = sorted(set([transitions[transition] for transition in transitions if transitions[transition] != "epsilon"]))
    
    def enka_to_dka(state):
        for symbol in symbols:
            is_added = False
            epsilon_closure_first = get_epsilon_closure({state})
            epsilon_closure_states = set([transition.second_state for transition in transitions if transition.first_state in epsilon_closure_first and transitions[transition] == symbol])

            if epsilon_closure_states:
                epsilon_closure = get_epsilon_closure(epsilon_closure_states.copy())

                if "#$#".join(epsilon_closure_first) not in dka.states:
                    dka.create_state("#$#".join(epsilon_closure_first))

                if "#$#".join(epsilon_closure) not in dka.states:
                    is_added = True
                    dka.create_state("#$#".join(epsilon_closure))

                dka.add_transition("#$#".join(epsilon_closure_first), "#$#".join(epsilon_closure), symbol)

                if is_added:
                    enka_to_dka(list(epsilon_closure_states)[0])

    dka = Dka()
    enka_to_dka(states[0])

    dka.create_state("(None)")
    transitions_by_left = dict()

    for ts in dka.transitions:
        for t in dka.transitions[ts]:
            if transitions_by_left.get(ts.first_state) == None:
                transitions_by_left.update({ts.first_state: dict()})
        
            transitions_by_left.get(ts.first_state).update({t: ts.second_state})

    for state_1 in dka.states:
        for symbol in symbols:
            if transitions_by_left.get(state_1) == None or transitions_by_left.get(state_1).get(symbol) == None:
                dka.add_transition(state_1, "(None)", symbol)
    
    transitions_by_left = dict()

    for ts in dka.transitions:
        for t in dka.transitions[ts]:
            if transitions_by_left.get(ts.first_state) == None:
                transitions_by_left.update({ts.first_state: dict()})
        
            transitions_by_left.get(ts.first_state).update({t: ts.second_state})
   
    dka.transitions = dict(sorted(dka.transitions.items(), key=lambda x: x[0].first_state))

    states = dka.states
    transitions = dka.transitions

    ####postoji šansa da odavde do idućeg komentara
    dka_min = Dka()

    def min_dka(group_list_a):
        
        is_changed = True

        while is_changed:
            is_changed = False
            new_list = list()

            for group in group_list_a:
                for index_1 in range(len(group) - 1):
                    if group[index_1] not in [elem for item in new_list for elem in item]:
                        new_list.append([group[index_1]])

                    for index_2 in range(index_1 + 1, len(group)):
                        is_same = True

                        for symbol in symbols:
                            check_1 = transitions_by_left.get(group[index_1]).get(symbol)
                            check_2 = transitions_by_left.get(group[index_2]).get(symbol)

                            check_index_1 = [index for index in range(len(group_list_a)) if check_1 in group_list_a[index]][0]
                            check_index_2 = [index for index in range(len(group_list_a)) if check_2 in group_list_a[index]][0]

                            if group_list_a[check_index_1][0] == "(None)" and group_list_a[check_index_2][0] == "(None)":
                                is_same = False
                                break

                            if check_index_1 != check_index_2:
                                is_same = False
                                break
                        
                        if is_same:
                            for item in new_list:
                                if group[index_1] in item and group[index_2] not in item:
                                    item.append(group[index_2])

                if group[-1] not in [elem for item in new_list for elem in item]:
                    new_list.append([group[-1]])

            if len(group_list_a) != len(new_list):
                is_changed = True

            group_list_a = new_list
        return group_list_a

    accept_set = states.copy()
    accept_set.remove("(None)")
    group_list = list()
    group_list.extend([accept_set, ["(None)"]])
    
    group_list = min_dka(group_list)

    for states_list in group_list:
        for states in states_list:
            merged_state = []

            if states == "(None)":
                continue

            for state in states.split("#$#"):
                merged_state.append(state)

            dka_min.create_state("#$#".join(sorted(set(merged_state))))

    dka_states = dka_min.states

    for states_list_index in range(len(group_list)):
        for symbol in symbols:
            merged_state_2 = []

            for states in group_list[states_list_index]:
                merged_state_2.append("#$#".join(sorted(set(transitions_by_left.get(states).get(symbol).split("#$#")))))

            number = None
            for index_dka_states in range(len(dka_states)):
                is_in = False
                for index_second_state in range(len(merged_state_2)):
                    if merged_state_2[index_second_state] in dka_states[index_dka_states]:
                        is_in = True
                        number = index_dka_states
                        break
                
                if is_in:
                    break

            if not number:
                print("NIJE PROSLO", dka_states[index_1])
                print("NIJE PROSLO", merged_state_2)
                continue

            index_1 = states_list_index
            index_2 = number

            dka_min.add_transition(dka_states[index_1], dka_states[index_2], symbol)
    ############## nema potrebe za ovim jer se sve grupira direktno, testirat ćemo oba načina pa vidjet  
    print(dka_min)
    #brisati <%> stanje ?
    #zasada hardkodirano
    #dka_min.states.remove("<%>-><S>* ; {#}")
    #dka_min.state_count -= 1

    nonfinal_chars = nonfinal_chars[1:]
    final_chars.append("#")
    print(nonfinal_chars)
    print(final_chars)
    print("\n\n\n")

    transitions_by_left = dict()

    for ts in dka_min.transitions:
        for t in dka_min.transitions[ts]:
            if transitions_by_left.get(ts.first_state) == None:
                transitions_by_left.update({ts.first_state: dict()})
        
            transitions_by_left.get(ts.first_state).update({t: ts.second_state})

    table = Table(dka_min.state_count, final_chars + nonfinal_chars)
    states = dka_min.states

    for table_state in range(dka_min.state_count):
        for char in final_chars + nonfinal_chars:
            for state in states[table_state].split("#$#"):
                if state == "q0":
                    continue

                state, lr1 = state.split(";")
                state, lr1 = state.strip(), lr1.replace("{", "").replace("}", "").replace("'", "").strip()

                dot_index = state.find("*")
                if char in final_chars and dot_index != len(state) - 1 and state[dot_index + 1] in final_chars:
                    if transitions_by_left.get(states[table_state]):
                        new_state = transitions_by_left.get(states[table_state]).get(char)

                        if new_state:
                            index = states.index(new_state)
                            table.put(table_state, char, f"Pomakni({index})")

                        break
                elif char in final_chars and dot_index == len(state) - 1:
                    if char in lr1.split(","):
                        state = state.replace('*', '').replace(' ', '')
                        if len(state.split("->")[1]) == 0:
                            state += "epsilon"

                        table.put(table_state, char, f"Reduciraj({state})")

                        break
                elif state == f"<%>->{nonfinal_chars[0]}*" and lr1 == "#":
                    table.put(table_state, "#", "Prihvati()")

                    break
                elif char in nonfinal_chars:
                    if transitions_by_left.get(states[table_state]):
                        new_state = transitions_by_left.get(states[table_state]).get(char)

                        if new_state:
                            index = states.index(new_state)
                            table.put(table_state, char, f"Stavi({index})")

                        break

    print(table.df)