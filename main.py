from Automata import Automata
from regexToAutomata import transform

if __name__ == '__main__':
    automat = Automata()
    expression = '(\)a|b)\|\(|x*|y*'
    transform(expression, automat)
    print(automat.states)
    for key in automat.transitions:
        print('Par stanja: ' + str(key) + ' ; Vrijednost: ' + str(automat.transitions[key]))