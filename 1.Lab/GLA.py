from sys import stdin
from json import dump

from Automata import Automata
from regexToAutomata import transform


if __name__ == '__main__':
    regular_definitions = {}
    analizer_states = []
    char_categories = []

    for line in stdin:
        line = line.strip()
        if line[0] != '{':
            for state in line.split(' ')[1:]:
                analizer_states.append(state)
            break
        name, definition = line.split('} ')
        regular_definitions.update({name[1:]: definition})
    categories_line = input()
    for category in categories_line.split(' ')[1:]:
        char_categories.append(category)

    for def_name in regular_definitions:
        for key in regular_definitions:
            if regular_definitions[key].find('{' + def_name + '}') != -1:
                new_definition = regular_definitions[key].replace('{' + def_name + '}', '(' + regular_definitions[def_name] + ')')
                regular_definitions.update({key: new_definition})

    # u automat dodat stanje u kojem je aktivan i listu specijalnih akcija
    # var za VRATI_SE, KLASA KOJU PRIHVACA, UDJI U STANJE
    automata = []
    states = []
    special_actions = []
    for line in stdin:
        line = line.strip()
        if line[0] == '<':
            char_index = line.find('>')
            state = line[1:char_index]
            regex = line[char_index+1: ]
            #state, regex = line.split('>')
            states.append(state)
            for def_name in regular_definitions:
                if regex.find('{' + def_name + '}') != -1:
                    regex = regex.replace('{' + def_name + '}', '(' + regular_definitions[def_name] + ')')
            new_automata = Automata()
            new_automata.lex_state = state
            transform(regex, new_automata)
            automata.append(new_automata)
        elif line[0] == '{':
            new_state = input()
            additional = input()
            lista = []
            lista.append(new_state)
            while additional != '}':
                lista.append(additional)
                additional = input()
            special_actions.append(lista)
            automata[-1].special_actions = lista

    with open(r"./analizator/prijelazi.json", "w") as f:
        output = dict()
        automatas = list()

        for automat in automata:
            automatas.append(
                dict(
                    states=list(map(str, automat.states)), 
                    transitions=dict(
                        map(
                            lambda x: (
                                x.__str__(), 
                                automat.transitions[x]
                            ), 
                            automat.transitions
                        )
                    ),
                    lex_state=automat.lex_state,
                    special_actions=automat.special_actions
                )
            )

        output["automatas"] = automatas
        output["analizer_states"] = analizer_states
        output["char_categories"] = char_categories
        #print(output)
        dump(output, f)
