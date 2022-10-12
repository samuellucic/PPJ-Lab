from pickle import FALSE
from re import I
from sys import stdin
from json import loads
from time import sleep
from turtle import pos

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

# special_actions = input["special_actions"]
# states = input["states"]
line = stdin.read()
#negdje dodati da ako nije lex u pravom stanju da ne radi nista
#dodati da za svaki automat pohrani sto je našao
#pretraziti po onim pravilima i odraditi akciju
#nakon tog čuda postaviti vrijednosti zavrsetak posljednji i pocetak kak spada
lex_state = "S_a" #generic
row = 1 
pocetak_lex = 0
posljednji_lex = 0
zavrsetak_lex = 0

blokirani = []
while zavrsetak_lex != len(line):
    izraz = []
    lista = []
    for index, automata in enumerate(input["automatas"]):
        #print("-----------------------")
        accept_state = set([automata["states"][1]])
        zavrsetak = zavrsetak_lex
        posljednji = posljednji_lex
        pocetak = pocetak_lex
        
        #print(automata)
        r_set = epsilon_closure(automata, set([automata["states"][0]]))
        while zavrsetak != len(line):
            #print("R_SET", r_set)
            #print("INTERSECT", r_set.intersection(accept_state), accept_state)
            if r_set and not r_set.intersection(accept_state):
                #print("IF")
                a = line[zavrsetak]
                #print("CITAM", a)
                zavrsetak += 1
                q_set = r_set.copy()

            elif r_set and r_set.intersection(accept_state):
                #print("ELIF")
                if lex_state == automata["lex_state"] and index not in blokirani and index not in izraz:
                    izraz.append(index)
                posljednji = zavrsetak - 1
                a = line[zavrsetak]
                zavrsetak += 1
                q_set = r_set
                
                #print("citam", a)
            else:
                #print("ELSE")
                if index in izraz:
                    lista.append([automata, pocetak, posljednji, zavrsetak])
                break

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
        

            # #print("DRUGI", r_set)
    #print("IZRAZ", izraz)
    if izraz:
        #print("IMA IZRAZ")
        #print(izraz)
        
        #sada tu dodati za sve za sve specijalne akcije bla bla bla
        lista_duljina = list(map(lambda x: x[2] - x[1], lista))
        index = lista_duljina.index(max(lista_duljina))
        autom = lista[index]
        #print(autom)
        pocetak, posljednji, zavrsetak = autom[1:]
        special_actions = autom[0]["special_actions"]

        odbaci = False
        for action in special_actions:
            #print("AKCIJA", action)
            if "-" == action:
                odbaci = True
            if "NOVI_REDAK" == action:
                row += 1
            if "UDJI_U_STANJE" in action:
                lex_state = action.split("")[1]

        pocetak_lex, posljednji_lex, zavrsetak_lex = pocetak, posljednji, zavrsetak
        if not odbaci:
            print(action, row, line[pocetak:posljednji])
            pocetak_lex = posljednji_lex + 1
            zavrsetak_lex = pocetak_lex
            blokirani.clear()
        else:
            zavrsetak_lex = pocetak_lex
            #print("blokiran")
            blokirani.append(izraz[index])
    else:
        #print("NEMA IZRAZA")
        pocetak_lex += 1
        zavrsetak_lex = pocetak_lex
    #print(pocetak_lex, posljednji_lex, zavrsetak_lex)
    #r_set = epsilon_closure(automata, set(automata["states"][0]))
    #print("BLOKIRANI LISTA", blokirani)
    #sleep(1)
# #print(input["automatas"])