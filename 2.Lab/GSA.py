from sys import stdin
import re
from turtle import dot
#import numpy as np

#from json import dump

from Enka import Enka
from Grammar import Grammar

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
    #states_cnt = 1
    lr1_units = dict()
    enka = Enka()
    enka.create_state('q0')
    enka.create_state(lr0_units[0])
    enka.lr1_sets.update({lr0_units[0]:'(kraj)'})
    #enka.create_state('{' + lr0_units[0] + ', (kraj)}')
    enka.add_epsilon_transition('q0', lr0_units[0])
    #enka.add_epsilon_transition('q0', '{' + lr0_units[0] + ', (kraj)}')
    lr1_units.update({lr0_units[0]: '(kraj)'})

    #print(enka)
    #print(list(lr1_units.keys()))

    def create_enka(enka, lr0_units, lr1_units, parent_transition):
        #Find next character
        #print(parent_transition)
        dot_index = parent_transition.find('*')
        leftover_string = parent_transition[dot_index + 1:]
        if (leftover_string == ''):
            return
        next_char = parent_transition[dot_index + 1:].split(' ')[0]
        #print(next_char)

        #Move dot in expression
        space_index = leftover_string.find(' ')
        if (space_index == -1):
            leftover_string += '*'
        else:
            leftover_string = leftover_string[:space_index] + '*' + leftover_string[space_index + 1:]
        if parent_transition[dot_index - 2: dot_index] == '->':
            final_transition = parent_transition[:dot_index] + leftover_string
        else:
            final_transition = parent_transition[:dot_index] + ' ' + leftover_string
        #print(final_transition)

        if next_char in grammar.nonfinal_chars or next_char in grammar.final_chars:
            enka.create_state(final_transition)
            enka.add_transition(parent_transition, final_transition, next_char)
            if final_transition not in enka.lr1_sets.keys():
                enka.lr1_sets[final_transition] = enka.lr1_sets[parent_transition]
                lr1_units[final_transition] = lr1_units[parent_transition]
                create_enka(enka, lr0_units, lr1_units, list(lr1_units.keys())[-1])
        if next_char in grammar.nonfinal_chars:
            ...
            #implementiraj ostatak algo
        
    create_enka(enka, lr0_units, lr1_units, list(lr1_units.keys())[0])

    print(enka)
    #print(lr0_units)
    #print(enka.lr1_sets)
    #print(lr1_units)