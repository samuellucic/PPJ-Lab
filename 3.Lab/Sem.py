from sys import stdin
from Node import Node
from TableNode import TableNode

from Productions import *

tree_input = stdin.readlines()

root_node = Node()
root_node.props.update({"name": tree_input[0].strip()})

previous_node = root_node
previous_space_count = 0

for line in tree_input[1:]:
    stripped_line = line.lstrip()
    space_count = len(line) - len(stripped_line)

    node = Node()
    node.props.update({"name": line.strip()})
    
    if space_count == previous_space_count:
        previous_node.parent.add_child(node)
    elif space_count > previous_space_count:
        previous_node.add_child(node)
    else:
        temp_node = previous_node.parent

        for i in range(previous_space_count - space_count):
            temp_node = temp_node.parent
        temp_node.add_child(node)

    previous_node = node
    previous_space_count = space_count

#print(root_node.__str__(0))
#print(root_node.get_children())

root_table = TableNode()
prijevodna_jedinica(root_node, root_table)

conditions = [False, True]

def check_functions(table, conditions):
    for name in table.table:
        if (name == "main (func)" 
                and table.table[name]["return_type"] == "int" 
                and len(table.table[name]["params"]) == 0):
            conditions[0] = True
        if "(func)" in name and not table.table[name]["defined"]:
            conditions[1] = False        

    if table.children:
        for child in table.children:
            check_functions(child, conditions)

check_functions(root_table, conditions)

if not conditions[0]:
    print("main")
elif not conditions[1]:
    print("funkcija")
