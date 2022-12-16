import sys
from TableNode import TableNode

def prijevodna_jedinica(node, table):
    prod = node.get_production()

    if prod == "<prijevodna_jedinica> ::= <vanjska_deklaracija>":
        vanjska_deklaracija(node.children[0], table)
    elif prod == "<prijevodna_jedinica> ::= <prijevodna_jedinica> <vanjska_deklaracija>":
        prijevodna_jedinica(node.children[0], table)
        vanjska_deklaracija(node.children[1], table)

def vanjska_deklaracija(node, table):
    prod = node.get_production()

    if prod == "<vanjska_deklaracija> ::= <definicija_funkcije>":
        definicija_funkcije(node.children[0], table)
    elif prod == "<vanjska_deklaracija> ::= <deklaracija>":
        deklaracija(node.children[0], table)

def definicija_funkcije(node, table):
    prod = node.get_production()
    
    if prod == "<definicija_funkcije> ::= <ime_tipa> IDN L_ZAGRADA KR_VOID D_ZAGRADA <slozena_naredba>":
        #1
        ime_tipa(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]

        if node_type_0 not in ["int", "char", "void"]:
            print(node.get_error())
            sys.exit()

        #3
        fun_name = node.children[1].props["name"].split()[2] + " (func)"
        fun = table.table.get(fun_name)

        if fun and fun.get("defined"):
            print(node.get_error())
            sys.exit()
        
        #4
        if fun:
            return_type = fun.get("return_type")
            params = fun.get("params")

            if return_type != node_type_0 or len(params) != 0:
                print(node.get_error())
                sys.exit()

        #5
        table.table.update({
            fun_name: {
                "defined": True,
                "params": list(),
                "return_type": node_type_0
            }
        })

        #6
        child_table = TableNode()
        table.add_child(child_table)
        slozena_naredba(node.children[5], child_table)

    elif prod == "<definicija_funkcije> ::= <ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>":
        #1
        ime_tipa(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]

        if node_type_0 not in ["int", "char", "void"]:
            print(node.get_error())
            sys.exit()

        #3
        fun_name = node.children[1].props["name"].split()[2] + " (func)"
        fun = table.table.get(fun_name)
 
        if fun and fun.get("defined"):
            print(node.get_error())
            sys.exit()
        #4
        lista_parametara(node.children[3], table)
        node_type_list_3 = node.children[3].props["type_list"]
        node_names_3 = node.children[3].props["names"]

        #5
        if fun:
            return_type = fun.get("return_type")
            params = fun.get("params")

            if return_type != node_type_0 or params != node_type_list_3:
                print(node.get_error())
                sys.exit()
        #6
        table.table.update({
            fun_name: {
                "defined": True,
                "params": node_type_list_3,
                "return_type": node_type_0
            }
        })

        #7
        child_table = TableNode()
        table.add_child(child_table)
    
        for name, type in zip(node_names_3, node_type_list_3):
            child_table.table.update({name: {"type": type}})

        slozena_naredba(node.children[5], child_table)

def primarni_izraz(node, table):
    prod = node.get_production()

    if prod == "<primarni_izraz> ::= IDN":
        child_name = node.children[0].props["name"].split()[2]
        copy_table = table
        while True:
            copy_child = copy_table.table.get(child_name)
            copy_child_func = copy_table.table.get(child_name + " (func)")
            if copy_child:
                type = copy_child.get("type")
                node.props.update({"type": type})
                if type in ["char", "int"]:
                    node.props.update({"l_expr": True})
                else:
                    node.props.update({"l_expr": False})
                break       
            elif copy_child_func:
                type = "funkcija("
                types = ("[" + ", ".join(copy_child_func.get("params")) + "]") if len(copy_child_func.get("params")) > 0 else "void"
                type += (types + " -> " + copy_child_func.get("return_type") + ")")
                node.props.update({"type": type, "l_expr": False})
                break
            elif copy_table.parent:
                copy_table = copy_table.parent
            else:
                print(node.get_error())
                sys.exit()
            
    elif prod == "<primarni_izraz> ::= BROJ":
        node.props.update({"type": "int", "l_expr": False})
        child_value = node.children[0].props["name"].split()[2]

        if child_value < -2147483648 or child_value > 2147483647:
            print(node.get_error())
            sys.exit()

    elif prod == "<primarni_izraz> ::= ZNAK":
        node.props.update({"type": "char", "l_expr": False})
        child_value = " ".join(node.children[0].props["name"].split()[2:])[1:-1]

        if (len(child_value) > 1 and child_value not in [r'\t', r'\n', r'\0', r'\'', r'\"', r'\\']) or child_value == '\\':
            print(node.get_error())
            sys.exit()

    elif prod == "<primarni_izraz> ::= NIZ_ZNAKOVA":
        node.props.update({"type": "niz(const(char))", "l_expr": False})
        child_value = " ".join(node.children[0].props["name"].split()[2:])[1:-1]

        previous = False
        for i in range(len(child_value)):
            if previous:
                previous = False
                continue
            if child_value[i] == '\\':
                previous = True
            if child_value[i] == '\\' and (i == len(child_value) - 1 or child_value[i+1] not in ['t', 'n', '0', '\'', '"', '\\']):
                print(node.get_error())
                sys.exit()

        # for char in child_value:
        #     if ord(char) < 32 and child_value not in ['\t', '\n', '\0', '\'', '\"', '\\']:
        #         print(node.get_error())
        #         sys.exit()

    elif prod == "<primarni_izraz> ::= L_ZAGRADA <izraz> D_ZAGRADA":
        izraz(node.children[1], table)

        node.props.update({"type": node.children[1].props["type"], "l_expr": node.children[1].props["l_expr"]})

