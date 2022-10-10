from sys import stdin
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
            states.append(state[1:])
            for def_name in regular_definitions:
                if regex.find('{' + def_name + '}') != -1:
                    regex = regex.replace('{' + def_name + '}', '(' + regular_definitions[def_name] + ')')
            new_automata = Automata()
            transform(regex, new_automata)
            automata.append(new_automata)
        elif line[0] == '{':
            new_state = input()
            additional = input()
            list = []
            list.append(new_state)
            while additional != '}':
                list.append(additional)
                additional = input()
            special_actions.append(list)

    f = open("prijelazi.txt", "w")

    for automat in automata:
        print(automat)
        print('====================')
        f.write(automat.__str__())
        f.write('====================\n')

    f.close()
