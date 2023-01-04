class TableNode:

    def __init__(self):
        self.parent = None
        self.children = None
        self.table = {"param size": 0, "local size": 0, "temp size": 0}
        #dict:
        # "a":      type: string ili "niz(string)" -> u slucaju da je array
        #           nepotreban (racuna se putem tipa): l_expr: boolean
        #           location (vrijednost local ili param)
        #           location_num (npr 4)
        #           ref (boolean)
        # "a (func)": defined: boolean -> imenovana kao npr. a func
        #             return_type: string
        #             params: list<string>
        #               ako je params void -> prazna lista
        # param size
        # local size
        # temp size
        self.is_func = False

    def add_child(self, child):
        if not self.children:
            self.children = list()
        self.children.append(child)
        child.parent = self

    def __str__(self, depth):
        output = self.table.__str__()

        if self.children:
            for child in self.children:
                output += "\n" + " " * (depth + 1) + child.__str__(depth + 1)
        
        return output