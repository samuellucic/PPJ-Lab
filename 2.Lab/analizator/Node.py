class Node:

    def __init__(self, parent=None, data=None):
        self.children = None
        self.parent = parent
        self.data = data

    def add_child(self, child):
        if not self.children:
            self.children = list()
        self.children.append(child)

    def add_parent(self, parent):
        self.parent = parent

    def __str__(self, depth):
        # for i in self.children:
        output = self.data.__str__()

        if self.children:
            self.children.reverse()

            for child in self.children:
                output += "\n" + " " * (depth + 1) + child.__str__(depth + 1)
        
        return output
    # def __str__(self):
    #     return self.data.uniform