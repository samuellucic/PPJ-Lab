from sys import stdin
from json import loads


def epsilon_closure(automata: dict, stack: set) -> set:
    y = stack.copy()

    while stack:
        state_t = stack.pop()

        for state_v in [state_v for state_v in automata["states"] if automata["transitions"].get(f"{state_t}:{state_v}") == "epsilon"]:
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

lex_state = input["analizer_states"][0] #generic

row = 1 
pocetak_lex = 0
posljednji_lex = 0
zavrsetak_lex = 0

blokirani = []
while zavrsetak_lex != len(line):
    izraz = []
    lista = []

    for index, automata in enumerate(automatas):
        accept_state = set([automata["states"][1]])
        zavrsetak = zavrsetak_lex
        posljednji = posljednji_lex
        pocetak = pocetak_lex
        
        r_set = epsilon_closure(automata, set([automata["states"][0]]))
        while True:
            if not r_set or zavrsetak == len(line):
                if index in izraz:
                    lista.append([automata, pocetak, posljednji, zavrsetak])
                break

            if r_set and not r_set.intersection(accept_state):
                a = line[zavrsetak]
                zavrsetak += 1
                q_set = r_set.copy()
            elif r_set and r_set.intersection(accept_state):
                if lex_state == automata["lex_state"] and index not in blokirani and index not in izraz:
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
                                lambda transition: transition.split(":")[0] in q_set and automata["transitions"][transition] == a, 
                                automata["transitions"]
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
                #implementiraj reset stvari

        pocetak_lex, posljednji_lex, zavrsetak_lex = pocetak, posljednji, zavrsetak
        if not odbaci:
            print(special_actions[0], row, line[pocetak:posljednji+1])
            pocetak_lex = posljednji_lex + 1
            zavrsetak_lex = pocetak_lex
            blokirani.clear()
        else:
            zavrsetak_lex = pocetak_lex
            blokirani.append(izraz[index])
    else:
        pocetak_lex += 1
        zavrsetak_lex = pocetak_lex