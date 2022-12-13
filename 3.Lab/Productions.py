import sys

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

        if node_type_0 in ["const char", "const int"]:
            print(node.get_error())
            sys.exit()

        #3
        fun_name = node.children[1].props["name"].split()[2]
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
        slozena_naredba(node.children[5], table)

    elif prod == "<definicija_funkcije> ::= <ime_tipa> IDN L_ZAGRADA <lista_parametara> D_ZAGRADA <slozena_naredba>":
        #1
        ime_tipa(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        node_type_list_3 = node.children[0].props["type_list"]

        if node_type_0 in ["const char", "const int"]:
            print(node.get_error())
            sys.exit()

        #3
        fun_name = node.children[1].props["name"].split()[2]
        fun = table.table.get(fun_name)
 
        if fun and fun.get("defined"):
            print(node.get_error())
            sys.exit()
        #4
        lista_parametara(node.children[3], table)

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
        slozena_naredba(node.children[5], table)


        