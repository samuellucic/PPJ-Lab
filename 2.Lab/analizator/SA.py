from sys import stdin, stderr
import pickle

from Data import Data
from Node import Node


if __name__ == '__main__':
    with open("tablica.json", "rb") as file:
        table = pickle.load(file)

    sync = table.sync
    
    stack = list()
    stack.append(0)

    root_node = None
    index = 0
    lines = list(map(lambda x: x.strip(), stdin.readlines()))
    lines.append("#")

    while(index < len(lines)):
        data = Data(line=lines[index]) if lines[index] != "#" else Data(uniform=lines[index])
        state = stack[-1]
        cmd = str(table.get(state, data.uniform))
    
        if "Pomakni" in cmd:
            node = Node(data=data)

            next_state = int((cmd.split("(")[1])[0:-1])
            stack.append(node)
            stack.append(next_state)
            index += 1
        elif "Reduciraj" in cmd:
            prod = (cmd.split("(")[1])[0:-1]
            prod = prod.split("->")
            left_side = prod[0]
            right_side = prod[1].split()
            right_side.reverse()
            
            node = Node(data=Data(uniform=left_side))
            if "epsilon" in right_side:
                eps_node = Node(data=Data(uniform="$"))
                node.add_child(eps_node)
            else:
                for char in right_side:
                    stack.pop()
                    child_node = stack.pop()
                    # if child_node.data.uniform != char:
                    #     #error handling
                    #     #to do later
                    #     #
                    #     pass
                    
                    node.add_child(child_node)
                    
            state = stack[-1]
            cmd = str(table.get(state, left_side))
            next_state = int((cmd.split("(")[1])[0:-1])

            stack.append(node)
            stack.append(next_state)
        elif "Prihvati" in cmd:
            stack.pop()
            root_node = stack.pop()
            break
        elif "nan" in cmd:
            row_error = "Pogreška u redu " + str(data.row)
            expected_uniform = "Očekivani znakovi " + " ".join(list(filter(lambda x: table.getRow(state)[x] != "nan", table.getRow(state))))
            stderr.write(row_error + "\n" + expected_uniform + "\n" + data.__str__() + "\n")
            
            while index < len(lines) - 1 and data.uniform not in sync:
                data = Data(line=lines[index]) if lines[index] != "#" else Data(uniform=lines[index])
                if data.uniform not in sync:
                    index += 1
            
            cmd = str(table.get(state, data.uniform))

            while cmd == "nan" and len(stack) > 1:
                stack.pop()
                node = stack.pop()
                state = stack[-1]
                cmd = str(table.get(state, data.uniform))
            
        #print(stack)
        #print(node.__str__())
    print(root_node.__str__(0))