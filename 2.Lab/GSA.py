from sys import stdin
#from json import dump

from Enka import Enka
from Grammar import Grammar

if __name__ == '__main__':

    #Parsing input data
    nonfinal = input().strip()
    nonfinal_chars = nonfinal.split(" ")[1:]
    starting_char = nonfinal_chars[0]

    final = input().strip()
    final_chars = final.split(" ")[1:]

    syn = input().strip()
    syn_chars = syn.split(" ")[1:]

    #Creating a grammar container
    grammar = Grammar(starting_char, nonfinal_chars, final_chars, syn_chars)

    #Parsing productions
    for line in stdin:
        if line[0] == '<':
            left_side = line.strip()
        else:
            grammar.add_production(left_side, line.strip())

    print(grammar)

