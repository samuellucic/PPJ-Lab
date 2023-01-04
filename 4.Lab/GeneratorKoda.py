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

root_table = TableNode()
prijevodna_jedinica(root_node, root_table)

if (not root_table.table.get("main (func)") 
    or root_table.table["main (func)"]["return_type"] != "int"
    or len(root_table.table["main (func)"]["params"]) != 0):
    print("main")

def check_functions(root_tbl, table):
    error = False
    for name in table.table:
        if " (func)" in name:
            root_entry = root_tbl.table.get(name)
            curr_entry = table.table.get(name)
            if (not root_entry or not root_entry["defined"]
                or root_entry["return_type"] != curr_entry["return_type"]
                or root_entry["params"] != curr_entry["params"]):
                print("funkcija")
                error = True
                break

    if table.children and not error:
        for child in table.children:
            error = check_functions(root_tbl, child)
            if error:
                break

    return error
with open("a.frisc", "w") as file:
    file.write(" MOVE 40000, R7\n")
    file.write(" JP LABEL_0\n")

    file.write("MASK DW 0FFFFFFFF\n")

    file.write("H_COMP LOAD R0, (SP+4)\n")
    file.write(" LOAD R1, (MASK)\n")
    file.write(" XOR R0, R1, R0\n")
    file.write(" ADD R0, 1, R6\n")    
    file.write(" RET\n")

    file.write("MASK_J DW 1\n")

    file.write("H_JEDAN\n")
    file.write(" LOAD R6, (MASK_J)\n")
    file.write(" RET\n")


    #množenje
    file.write("H_MULT LOAD R4, (SP+8)\n")
    file.write(" LOAD R1, (SP+4)\n")
    file.write(" MOVE 0, R2\n")
    file.write(" XOR R0, R1, R3\n")
    
    file.write("TEST_1 OR R4, R4, R4\n")
    file.write(" JR_P TEST_2\n")

    file.write("NEGAT_1 XOR R4, -1, R4\n")
    file.write(" ADD R4, 1, R4\n")

    file.write("TEST_2 OR R1, R1, R1\n")
    file.write(" JR_P PETLJA\n")

    file.write("NEGAT_2 XOR R1, -1, R1\n")
    file.write(" ADD R1, 1, R1\n")
    
    file.write("PETLJA ADD R4, R2, R2\n")
    file.write(" SUB R1, 1, R1\n")
    file.write(" JR_NZ PETLJA\n")

    file.write(" ROTL R3, 1, R3\n")
    file.write(" JR_NC GOTOVO_1\n")

    file.write(" XOR R2, -1, R2\n")
    file.write(" ADD R2, 1, R2\n")

    file.write("GOTOVO_1 ADD R2, 0, R6\n")
    file.write(" RET\n")

    #DIJELJENJE
    file.write("H_DIV LOAD R0, (SP+8) \n")
    file.write(" LOAD R1, (SP+4)\n")
    file.write(" MOVE -1, R2\n")
    file.write(" XOR R0, R1, R3\n")

    file.write("TEST_3 OR R0, R0, R0\n")
    file.write(" JR_P TEST_4\n")

    file.write("NEGAT_3 XOR R0, -1, R0\n")
    file.write(" ADD R0, 1, R0\n")

    file.write("TEST_4 OR R1, R1, R1\n")
    file.write(" JR_P PETLJA_2\n")

    file.write("NEGAT_4 XOR R1, -1, R1\n")
    file.write(" ADD R1, 1, R1\n")
    
    file.write("PETLJA_2 ADD R2, 1, R2\n")
    file.write(" SUB R0, R1, R0\n")
    file.write(" JR_UGE PETLJA_2\n")

    file.write(" ROTL R3, 1, R3\n")
    file.write(" JR_NC GOTOVO_2\n")

    file.write(" XOR R2, -1, R2\n")
    file.write(" ADD R2, 1, R2\n")

    file.write("GOTOVO_2 ADD R2, 0, R6\n")
    file.write(" RET\n")

    # OSTATAK
    file.write("H_MOD LOAD R0, (SP+8) \n")
    file.write(" LOAD R1, (SP+4)\n")
    file.write(" MOVE -1, R2\n")

    file.write("PETLJA_3 SUB R0, R1, R3\n")
    file.write(" JP_SLT GOTOVO_3\n")

    file.write(" ADD R2, 1, R2\n")
    file.write(" SUB R0, R1, R0\n")
    file.write(" JR_UGE PETLJA_3\n")

    file.write("GOTOVO_3 ADD R0, 0, R6\n")
    file.write(" RET\n")

    file.write("LABEL_0")

check_functions(root_table, root_table)

#print(root_table.__str__(0))

