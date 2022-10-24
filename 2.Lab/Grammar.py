class Grammar:
    def __init__(self, starting_char='', nonfinal_chars=list(), final_chars=list(), syn_chars=list(), productions=dict()):
        self.starting_char = starting_char
        self.nonfinal_chars = nonfinal_chars
        self.final_chars = final_chars
        self.syn_chars = syn_chars
        self.productions = productions

    def __str__(self):
        nonfinal = 'Nezavrsni znakovi: \n'
        for char in self.nonfinal_chars:
            nonfinal += (str(char) + ' ')
        final = 'Zavrsni znakovi \n'
        for char in self.final_chars:
            final += (str(char) + ' ')
        syn = 'Sinkronizacijski znakovi \n'
        for char in self.syn_chars:
            syn += (str(char) + ' ')
        prods = 'Produkcije: \n'
        for production in self.productions:
            prods += (str(production) + '->' + str(self.productions[production]) + '\n')
        return ('Gramatika\n--------------------\nPocetni znak gramatike: \n' + self.starting_char + '\n--------------------\n' + nonfinal + '\n--------------------\n' + final + '\n--------------------\n' + syn + '\n--------------------\n' + prods).strip()

    def add_production(self, left_side, right_side):
        if left_side in self.productions.keys():
            self.productions[left_side].extend([right_side])
        else:
            self.productions[left_side] = [right_side]