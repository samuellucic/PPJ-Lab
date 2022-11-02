class Node:

    def __init__(self, parent=None, data=None):
        self.children = None
        self.parent = parent
        self.data = data

    def add_child(self, child):
        if not self.children:
            self.children = list()
        self.children.append(child)
        child.parent = self

    def del_child(self, child):
        self.children.remove(child)

    def __str__(self, depth):
        output = self.data.__str__()

        if self.children:
            self.children.reverse()

            for child in self.children:
                output += "\n" + " " * (depth + 1) + child.__str__(depth + 1)
        
        return output