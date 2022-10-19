from sys import stdin, stderr
from json import loads

def epsilon_closure(automata: dict, stack: set) -> set:
    y = stack.copy()
    automata_transitions = dict(
        map(
            lambda x: (x, automata["transitions"][x]), 
            filter(
                lambda x: automata["transitions"][x] == "epsilon", 
                automata["transitions"]
            )
        )
    ).keys()
    automata_states = automata["states"]

    while stack:
        state_t = stack.pop()
        for state_v in [state_v for state_v in automata_states if f"{state_t}:{state_v}" in automata_transitions]:
            if state_v not in y:
                y.add(state_v)
                stack.add(state_v)
    return y

with open("prijelazi.json", "r") as file:
    input = loads(file.read())

line = stdin.read()


automatas = input["automatas"]
analizer_states = input["analizer_states"]
char_categories = input["char_categories"]
lex_state = input["analizer_states"][0]

row = 1 
pocetak_lex = 0
posljednji_lex = 0
zavrsetak_lex = 0

automatas_by_state = dict()

for automata in automatas:
    if automata["lex_state"] in automatas_by_state.keys():
        curr_list = automatas_by_state[automata["lex_state"]]
    else:
        curr_list = list()
    curr_list.append(automata)
    automatas_by_state.update({automata["lex_state"]: curr_list})

if not automatas:
    automatas_by_state.update({lex_state: list()})

while zavrsetak_lex != len(line):
    izraz = []
    lista = []

    for index, automata in enumerate(automatas_by_state[lex_state]):
        automata_states = automata["states"]
        automata_transitions = dict(
            map(
                lambda x: (x, automata["transitions"][x]), 
                filter(
                    lambda x: automata["transitions"][x] != "epsilon", 
                    automata["transitions"]
                )
            )
        )
        accept_state = set([automata_states[1]])

        zavrsetak = zavrsetak_lex
        posljednji = posljednji_lex
        pocetak = pocetak_lex

        r_set = epsilon_closure(automata, set([automata_states[0]]))
        while True:
            if not r_set or zavrsetak == len(line):
                if r_set and r_set.intersection(accept_state) and index not in izraz:
                    posljednji = zavrsetak - 1
                    izraz.append(index)

                if index in izraz:
                    lista.append([automata, pocetak, posljednji, zavrsetak])

                break

            if r_set and not r_set.intersection(accept_state):
                a = line[zavrsetak]
                zavrsetak += 1
                q_set = r_set
            elif r_set and r_set.intersection(accept_state):
                if index not in izraz:
                    izraz.append(index)

                posljednji = zavrsetak - 1
                a = line[zavrsetak]
                zavrsetak += 1
                q_set = r_set

            r_set = epsilon_closure(
                automata,
                set(
                    map(
                        lambda transition: transition.split(":")[1], 
                        list(
                            filter(
                                lambda transition: transition.split(":")[0] in q_set and automata_transitions[transition] == a, 
                                automata_transitions
                            )
                        )
                    )
                )
            )

    if izraz:
        lista_duljina = list(map(lambda x: x[2] - x[1], lista))
        index = lista_duljina.index(max(lista_duljina))
        autom = lista[index]

        pocetak, posljednji, zavrsetak = autom[1:]
        special_actions = autom[0]["special_actions"]

        odbaci = False
        for action in special_actions:
            if "-" == action:
                odbaci = True
            if "NOVI_REDAK" == action:
                row += 1
            if "UDJI_U_STANJE" in action:
                lex_state = action.split(" ")[1]
            if "VRATI_SE" in action:
                ind_vrati = action.split(" ")[1]
                posljednji = pocetak + int(ind_vrati) - 1

        pocetak_lex, posljednji_lex, zavrsetak_lex = pocetak, posljednji, zavrsetak
        if not odbaci:
            print(special_actions[0], row, line[pocetak:posljednji+1])

        pocetak_lex = posljednji_lex + 1
        zavrsetak_lex = pocetak_lex
    else:
        stderr.write(repr(line[pocetak_lex])[1:-1])
        pocetak_lex += 1
        zavrsetak_lex = pocetak_lex