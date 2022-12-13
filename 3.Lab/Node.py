class Node:

    def __init__(self):
        self.parent = None
        self.children = None
        self.props = dict()

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