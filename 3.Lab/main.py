from TableNode import TableNode

if __name__ == "__main__":
    table = TableNode()
    table.table.update({"a": {"type": "string"}})
    table.table["a"].update({"len": 10})
    #print(table.table["a"])

    child = TableNode()
    child.table.update({"b": {"type": "string"}})
    table.add_child(child)

    print(table.__str__(0))
    print(child.parent.table)