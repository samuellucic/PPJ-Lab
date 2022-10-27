from sre_parse import State
from sys import stdin
import re
from tokenize import group
from turtle import dot

#import numpy as np
#from json import dump

from Enka import Enka
from Grammar import Grammar
from State import StatePair
from Nka import Nka
from Dka import Dka


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

    nka = Nka()
    nka.states = enka.states

    states = enka.states
    transitions = enka.transitions
    symbols = sorted(set([transitions[transition] for transition in transitions if transitions[transition] != "epsilon"]))

    for state in states:
        for symbol in symbols:
            epsilon_closure_first = get_epsilon_closure({state})
            epsilon_closure_states = set([transition.second_state for transition in transitions if transition.first_state in epsilon_closure_first and transitions[transition] == symbol])
            
            if epsilon_closure_states:
                epsilon_closure = get_epsilon_closure(epsilon_closure_states)

                for eps_state in epsilon_closure:
                    nka.add_transition(state, eps_state, symbol)

    print(nka)

    def nka_to_dka(start_state: list) -> list:
        print("START", start_state, len(start_state[0]))
        states = start_state
        if len(start_state[0]) == 78:
            print("EVOOOOOOOOOOOOOOOOOOOOOOOOO GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        for current_state in states:
            for symbol in symbols:
                for transition in transitions:
                    if len(start_state[0]) == 82:
                        print(transition.first_state, current_state.split("#$#"), any(transition.first_state == segment for segment in current_state.split("#$#")), any(symbol == symb for symb in transitions[transition]))
                    if any(transition.first_state == segment for segment in current_state.split("#$#")) and any(symbol == symb for symb in transitions[transition]):
                        print(transition.second_state)

                new_state = "#$#".join(
                    sorted(
                        set(
                            [transition.second_state for transition in transitions if any(transition.first_state == segment for segment in current_state.split("#$#")) and any(symbol == symb for symb in transitions[transition])]
                        )
                    )
                )

                if new_state:
                    print("SIMBOL", symbol, "NEW STATE", new_state)
                    if new_state not in dka.states:
                        print("UŠAO")
                        dka.create_state(new_state)
                        nka_to_dka([new_state])
                        print("VRATIO", start_state)
                    dka.add_transition(current_state, new_state, symbol)

    dka = Dka()
    
    transitions = nka.transitions

    # for state_with_transition in states:
    #     if (state_with_transition not in dka.states 
    #             and state_with_transition.split(";")[0].strip()[-1] != "*"):
    #         dka.create_state(state_with_transition)
    #         nka_to_dka([state_with_transition])
    dka.create_state(states[1])
    nka_to_dka([states[1]])
    dka.create_state(states[0])
    nka_to_dka([states[0]])


    print(dka)
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

    dka_min = Dka()
    print(dka)

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
            # print("GROUP")
            # for i in group_list_a:
            #     print(i)
            print("---------------------")
            print("NEW")
            for i in new_list:
                print(i)
            if len(group_list_a) != len(new_list):
                is_changed = True
            group_list_a = new_list
        print(group_list_a)

    accept_set = states.copy()
    accept_set.remove("(None)")
    group_list = list()
    group_list.extend([accept_set, ["(None)"]])
    
    min_dka(group_list)
