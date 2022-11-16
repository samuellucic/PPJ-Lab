from sys import stdin
import re
import time
import pickle

#import numpy as np
#from json import dump

from Enka import Enka
from Grammar import Grammar
from Dka import Dka
from Table import Table


if __name__ == '__main__':
    start = time.time()
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

    productions_input = stdin.readlines()
    for line in productions_input:
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

    changed = True

    #Calculate startsWith table
    while(changed):
        changed = False
        for i in range(nonfinal_cnt):
            for j in range(no_of_chars):
                if starts_with[i][j] == 1 and i != j:
                    for k in range(no_of_chars):
                        if starts_with[j][k] == 1 and starts_with[i][k] != 1:
                            starts_with[i][k] = 1
                            changed = True

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
    #for key in startsWithDict:
    #    print(f"Kljuc: {key}")
    #    print(f"Vrijednosti: {startsWithDict[key]}")

    #Calculate lr0 units
    lr0_units = list()
    for production in productions:
        for right_side in productions[production]:
            if (right_side == '$'):
                lr0_units.append(production + '->.')
            else:
                lr0_units.append(production + '->.' + right_side)
                indices = [m.start() for m in re.finditer(' ', right_side)]
                for index in indices:
                    lr0_units.append(production + '->' + (right_side[:index] + '.' + right_side[index+1:]))
                lr0_units.append(production + '->' + right_side + '.')

    #print(lr0_units)

    #Calculate lr1 units
    enka = Enka()
    enka.create_state(lr0_units[0] + ' ; {#}')

    #enka.create_state('q0')
    #enka.create_state(lr0_units[0] + ' ; {#}')
    #enka.add_epsilon_transition('q0', lr0_units[0] + ' ; {#}')

    #print(enka)

    def create_enka(enka, lr0_units, parent_transition):
        #Find next character
        #print(parent_transition)
        parent_transition_new, parent_set = parent_transition.split(' ; ')
        dot_index = parent_transition_new.find('.')
        leftover_string = parent_transition_new[dot_index + 1:]
        if (leftover_string == ''):
            return
        next_char = parent_transition_new[dot_index + 1:].split(' ')[0]
        rest_of_string = parent_transition_new[dot_index + 1:].split(' ')[1:]
        rest_of_string = '' if rest_of_string == [] else rest_of_string
        
        #Move dot in expression
        space_index = leftover_string.find(' ')
        if (space_index == -1):
            leftover_string += '.'
        else:
            leftover_string = leftover_string[:space_index] + '.' + leftover_string[space_index + 1:]

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
                if unit.startswith(next_char + '->.'):
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
                            additional_chars = additional_chars.union(set(parent_set[1:-1].replace("'", "").split(',')))
                        #print(parent_set)
                        
                        lr1_unit = unit + ' ; ' + str(additional_chars).replace(' ', '')
                        #print("JEDINICA __________________ " + lr1_unit)
                        if lr1_unit not in enka.states:
                            enka.create_state(lr1_unit)
                            enka.add_epsilon_transition(parent_transition, lr1_unit)
                            create_enka(enka, lr0_units, lr1_unit)
                        else:
                            enka.add_epsilon_transition(parent_transition, lr1_unit)

    create_enka(enka, lr0_units, enka.states[-1])
    #print(enka)
    print(enka.state_count)
    print(len(enka.transitions))
    #print(lr0_units)

    def get_epsilon_closure(stack: list) -> list:
        epsilon_closure = stack.copy()

        while stack:
            state_t = stack.pop()
            if transitions.get(state_t) and transitions.get(state_t).get("epsilon"):
                for state_v in transitions.get(state_t).get("epsilon"):
                    if state_v not in epsilon_closure:
                        epsilon_closure.append(state_v)
                        if state_v not in stack:
                            stack.append(state_v)

        return list(sorted(set(epsilon_closure)))

    def transition_closure(states, symbol):
        new = []

        for state in states:
            new_state = None
            if transitions.get(state):
                new_state = transitions.get(state).get(symbol)

            if new_state:
                new.extend(new_state)

        return get_epsilon_closure(new)

    def build_dka(states):
        added = []

        for state in states:
            for symbol in symbols:
                new = transition_closure(state.split("#$#"), symbol)

                if new:
                    new = "#$#".join(new)

                    if new not in dka.states:
                        dka.create_state(new)
                        added.append(new)

                    dka.add_transition(state, new, symbol)

        for state in added:
            build_dka([state])

    transitions = dict()
    for transition in enka.transitions:
        if transitions.get(transition.first_state) == None:
            transitions.update({transition.first_state: dict()})

        if transitions.get(transition.first_state).get(enka.transitions[transition]) == None:
            transitions.get(transition.first_state).update({enka.transitions[transition]: list()})

        transitions.get(transition.first_state).get(enka.transitions[transition]).append(transition.second_state)

    states = enka.states
    symbols = nonfinal_chars[1:] + final_chars

    start_goto = get_epsilon_closure([states[0]])
    start_goto.sort()

    dka = Dka()
    dka.create_state("#$#".join(start_goto))
    end = time.time()
    print(end - start)
    start = time.time()
    build_dka(["#$#".join(start_goto)])
    end = time.time()
    print(end - start)

    #print(dka)
    
    nonfinal_chars = nonfinal_chars[1:]
    final_chars.append("#")
    #print(nonfinal_chars)
    #print(final_chars)
    #print(dka)
    #print("\n\n\n")

    start = time.time()
    table = Table(dka.state_count, final_chars + nonfinal_chars, syn_chars)
    
    states = dka.states
    transitions = dka.transitions

    def find_only_available_uniform(state):
        uniform_list = list()

        uniform_list.extend(
            state.split(";")[0]
                    .split("->")[1]
                    .replace(".", " ")
                    .split(), 
        )
        uniform_list.extend(
            state.split(";")[1]
                    .replace("{", "")
                    .replace("}", "")
                    .replace("'", "")
                    .strip()
                    .split(",")
        )
        
        return uniform_list

    for table_state in range(dka.state_count):
        state_set = states[table_state].split("#$#")
        state_chars = list(
            map(
                lambda state: find_only_available_uniform(state),
                state_set
            )
        )
        state_chars = list(set([char.strip() for chars in state_chars for char in chars]))
        state_chars.append("#")

        for char in final_chars + nonfinal_chars:
            if char not in state_chars:
               continue

            move_list = list()
            reduce_list = list()

            for state in state_set:
                state, lr1 = state.split(";")
                state, lr1 = state.strip(), lr1.replace("{", "").replace("}", "").replace("'", "").strip()

                dot_index = state.find(".")
                if char == "#" and state == f"<%>->{nonfinal_chars[0]}." and lr1 == "#":
                    table.put(table_state, "#", "Prihvati()")
                    break
                elif char in final_chars and dot_index != len(state) - 1 and state[dot_index + 1:].split()[0] in final_chars:
                    if transitions.get(states[table_state]):
                        new_state = transitions.get(states[table_state]).get(char)

                        if new_state:
                            index = states.index(new_state)
                            move_list.append([table_state, char, f"Pomakni({index})"])
                elif char in final_chars and dot_index == len(state) - 1:
                    if char in lr1.split(","):
                        state = state.replace('.', ' ')
                        state = state.split("->")[0] + "->" + state.split("->")[1].strip()
                        if len(state.split("->")[1]) == 0:
                            state += "epsilon"
                        reduce_list.append([table_state, char, f"Reduciraj({state})"])
                elif char in nonfinal_chars:
                    if transitions.get(states[table_state]):
                        new_state = transitions.get(states[table_state]).get(char)

                        if new_state:
                            index = states.index(new_state)
                            table.put(table_state, char, f"Stavi({index})")
                            break

                        
            if move_list:
                table.put(*move_list[0])
            elif reduce_list:
                if len(reduce_list) > 1:
                    lr0_units = list(map(lambda x: x.replace(".", " "), lr0_units))
                    lr0_units = list(map(lambda x: x.split("->")[0] + "->" + x.split("->")[1].strip(), lr0_units))
                    productions = list(map(lambda x: x[2].replace("Reduciraj", "").replace("(", "").replace(")", ""), reduce_list))

                    for production in lr0_units:
                        #production = production.strip()

                        if production in productions:
                            table.put(*reduce_list[productions.index(production)])
                            break
                else:
                    table.put(*reduce_list[0])

    with open(r"./analizator/tablica.json", "wb") as file:
        pickle.dump(table, file)
    #print(table.df)
    end = time.time()
    print(end - start)
    #print()