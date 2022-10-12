from re import I
from sys import stdin
from json import loads
from turtle import pos

def epsilon_closure(automata: dict, stack: set) -> set:
    y = stack.copy()

    while stack:
        state_t = stack.pop()

        for state_v in [state_v for state_v in automata["states"] if automata["transitions"].get(f"{state_t}:{state_v}") == "$"]:
            if state_v not in y:
                y.add(state_v)
                stack.add(state_v)

    return y

with open("prijelazi.json", "r") as file:
    input = loads(file.read())

# special_actions = input["special_actions"]
# states = input["states"]
line = stdin.read()
#negdje dodati da ako nije lex u pravom stanju da ne radi nista
#dodati da za svaki automat pohrani sto je našao
#pretraziti po onim pravilima i odraditi akciju
#nakon tog čuda postaviti vrijednosti zavrsetak posljednji i pocetak kak spada
lex_state = "S_poc" #generic
row = 1 
pocetak_lex = 1
posljednji_lex = 1
zavrsetak_lex = 0


while zavrsetak_lex != len(line):
    izraz = []
    lista = []

    for index, automata in enumerate(input["automatas"]):
        accept_state = automata["states"][1]
        zavrsetak = zavrsetak_lex
        posljednji = posljednji_lex
        pocetak = pocetak_lex

        r_set = epsilon_closure(automata, set(automata["states"][0]))
        while zavrsetak != len(line):
            if r_set and not r_set.intersection(accept_state):
                #print("IF")
                a = line[zavrsetak]
                zavrsetak += 1
                q_set = r_set.copy()
            elif r_set and r_set.intersection(accept_state):
                #print("ELIF")
                if lex_state == automata["lex_state"]:
                    izraz.append(index)
                posljednji = zavrsetak
                zavrsetak += 1
                if zavrsetak == len(line):
                    if index in izraz:
                        lista.append([automata, pocetak, posljednji, zavrsetak])
                    break
                q_set = r_set
                a = line[zavrsetak]
            else:
                #print("ELSE")
                if index in izraz:
                    lista.append([automata, pocetak, posljednji, zavrsetak])
                break

            r_set = epsilon_closure(
                automata,
                stack = set(
                    map(
                        lambda transition: transition[2], 
                        list(
                            filter(
                                lambda transition: transition[0] in q_set and automata["transitions"][transition] == a, 
                                automata["transitions"]
                            )
                        )
                    )
                )
            )
        

            # print("DRUGI", r_set)
    if izraz:
        #print(izraz)
        print(lista)
        #sada tu dodati za sve za sve specijalne akcije bla bla bla
        lista_duljina = list(map(lambda x: x[2] - x[1], lista))
        index = lista_duljina.index(max(lista_duljina))
        autom = lista[index]
        pocetak, posljednji, zavrsetak = lista[index][1:]
        special_actions = autom[0]["special_actions"]

        for action in special_actions:
            #if ovo blablabla:
            print(action, row, line[pocetak-1:posljednji])

        pocetak_lex, posljednji_lex, zavrsetak_lex = pocetak, posljednji, zavrsetak
        pocetak_lex = posljednji_lex + 1
        zavrsetak_lex = posljednji_lex
    else:
        zavrsetak_lex = pocetak_lex
        pocetak_lex += 1
    #r_set = epsilon_closure(automata, set(automata["states"][0]))

# print(input["automatas"])