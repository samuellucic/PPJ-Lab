class TableNode:

    def __init__(self):
        self.parent = None
        self.children = None
        self.table = dict()
        #dict:
        # a (dict): type: string
        # fun (dict): defined: boolean
        #             return_type: string
        #             params: list<string>
        # ako je params void -> prazna lista

    def add_child(self, child):
        if not self.children:
            self.children = list()
        self.children.append(child)
        child.parent = self

    def __str__(self, depth):
        output = self.props["name"].__str__()

        if self.children:
            for child in self.children:
                output += "\n" + " " * (depth + 1) + child.__str__(depth + 1)
        
        return output