class Node:

    def __init__(self):
        self.parent = None
        self.children = None
        self.props = dict()

        #props -> name (str)
        #         l_expr (boolean) 
        #         names (list<str>); (void = prazna lista) void ne bi trebalo ni biti moguce zbog sintaksne
        #         type (str) <- ako je niz: niz(const(char)), ako je funkcija: funkcija([char, char] -> int)
        #         type_list (list<str>); (void = prazna lista) void ne bi trebalo ni biti moguce zbog sintaksne
        #         i_type; (inherited type) za varijable brojeva ntip ce biti cijeli tip, za nizove ce biti tip elemenata niza,
        #                 a za fje ce biti povratni tip
        #         elem_num; broj elemenata
    def add_child(self, child):
        if not self.children:
            self.children = list()
        self.children.append(child)
        child.parent = self

    def __str__(self, depth):
        output = self.props["name"].__str__()
        # if self.props["name"].split()[0] == "ZNAK":
        #     string = " ".join(self.props["name"].split()[2:])[1:-1]
        #     if (len(string) > 1 and string not in [r'\t', r'\n', r'\0', r'\'', r'\"', r'\\']) or string == '\\':
        #         print("greska " + string)
        #     else:
        #         print("ok " + string)
        # if self.props["name"].split()[0] == "NIZ_ZNAKOVA":
        #     string = " ".join(self.props["name"].split()[2:])[1:-1]
        #     prosli = False
        #     for i in range(len(string)):
        #         if prosli:
        #             prosli = False
        #             continue
        #         if string[i] == '\\':
        #             prosli = True
        #         if string[i] == '\\' and (i == len(string) - 1 or string[i+1] not in ['t', 'n', '0', '\'', '"', '\\']):
        #             print("greska na znaku" + string[i])

        if self.children:
            for child in self.children:
                output += "\n" + " " * (depth + 1) + child.__str__(depth + 1)
        
        return output

    def get_production(self):
        return self.props["name"] + " ::= " + " ".join(list(map(lambda child: child.props["name"].split()[0], self.children)))

    def get_error(self):
        def lam(child):
            name = child.props["name"].split()

            if len(name) > 1:
                name = f"{name[0]}({name[1]},{name[2]})"
            else:
                name = name[0]

            return name

        return self.props["name"] + " ::= " + " ".join(list(map(lambda child: lam(child), self.children)))