from Automata import Automata
from regexToAutomata import transform

if __name__ == '__main__':
    automat = Automata()
    expression = '((0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*|0x((0|1|2|3|4|5|6|7|8|9)|a|b|c|d|e|f|A|B|C|D|E|F)((0|1|2|3|4|5|6|7|8|9)|a|b|c|d|e|f|A|B|C|D|E|F)*)'
    transform(expression, automat)
    print(automat.states)
    for key in automat.transitions:
        print('Par stanja: ' + str(key) + ' ; Vrijednost: ' + str(automat.transitions[key]))