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
        node_name_1_not_func = node.children[1].props["name"].split()[2]
        if fun:
            return_type = fun.get("return_type")
            params = fun.get("params")

            if return_type != node_type_0 or len(params) != 0:
                print(node.get_error())
                sys.exit()
        elif table.table.get(node_name_1_not_func):
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
        node_name_1_not_func = node.children[1].props["name"].split()[2]
        if fun:
            return_type = fun.get("return_type")
            params = fun.get("params")

            if return_type != node_type_0 or params != node_type_list_3:
                print(node.get_error())
                sys.exit()
        elif table.table.get(node_name_1_not_func):
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
                if type in ["char", "int", "niz(char)", "niz(int)"]:
                    node.props.update({"l_expr": True})
                else:
                    node.props.update({"l_expr": False})
                break       
            elif copy_child_func:
                type = "funkcija("
                type_list = ("[" + ", ".join(copy_child_func.get("params")) + "]") if len(copy_child_func.get("params")) > 0 else "void"
                type += (type_list + " -> " + copy_child_func.get("return_type") + ")")
                node.props.update({"type": type, "l_expr": False})
                break
            elif copy_table.parent:
                copy_table = copy_table.parent
            else:
                print(node.get_error())
                sys.exit()
            
    elif prod == "<primarni_izraz> ::= BROJ":
        node.props.update({"type": "int", "l_expr": False})
        child_value = int(node.children[0].props["name"].split()[2])
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

def postfiks_izraz(node, table):
    prod = node.get_production()

    if prod == "<postfiks_izraz> ::= <primarni_izraz>":
        primarni_izraz(node.children[0], table)

        node.props.update({"type": node.children[0].props["type"], "l_expr": node.children[0].props["l_expr"]})

    elif prod == "<postfiks_izraz> ::= <postfiks_izraz> L_UGL_ZAGRADA <izraz> D_UGL_ZAGRADA":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["niz(int)", "niz(char)", "niz(const(int))", "niz(const(char))"]:
            print(node.get_error())
            sys.exit()
        
        #3
        izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        type = node_type_0[4:-1]
        l_expr = node.children[0].props["l_expr"]
        node.props.update({"type": type, "l_expr": l_expr})

    elif prod == "<postfiks_izraz> ::= <postfiks_izraz> L_ZAGRADA D_ZAGRADA":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]

        if node_type_0.split(" -> ")[0] != "funkcija(void":
            print(node.get_error())
            sys.exit()

        return_type = node_type_0.split(" -> ")[1][:-1]
        node.props.update({"type": return_type, "l_expr": False})

    elif prod == "<postfiks_izraz> ::= <postfiks_izraz> L_ZAGRADA <lista_argumenata> D_ZAGRADA":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        lista_argumenata(node.children[2], table)

        #3
        node_type_0 = node.children[0].props["type"]
        if "funkcija([" not in node_type_0.split(" -> ")[0]:
            print(node.get_error())
            sys.exit()

        node_params_0 = node_type_0.split("[")[1].split("]")[0].split(', ')
        node_args_2 = node.children[2].props["type_list"]

        if len(node_params_0) != len(node_args_2):
            print(node.get_error())
            sys.exit()

        for param, arg in zip(node_params_0, node_args_2):
            if (param == "int" or param == "const(int)"):
                if arg not in ["int", "char", "const(int)", "const(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "char" or param == "const(char)"):
                if arg not in ["char", "const(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(int)"):
                if arg not in ["niz(int)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(char"):
                if arg not in ["niz(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(const(int))"):
                if arg not in ["niz(int)", "niz(const(int))"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(const(char))"):
                if arg not in ["niz(char)", "niz(const(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif "funkcija" in param and param != arg:
                print(node.get_error())
                sys.exit()

        return_type = node_type_0.split(" -> ")[1][:-1]
        node.props.update({"type": return_type, "l_expr": False})

    elif prod == "<postfiks_izraz> ::= <postfiks_izraz> OP_INC" or prod == "<postfiks_izraz> ::= <postfiks_izraz> OP_DEC":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        l_expr = node.children[0].props["l_expr"]
        node_type_0 = node.children[0].props["type"]

        if l_expr == False or node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def lista_argumenata(node, table):
    prod = node.get_production()

    if prod == "<lista_argumenata> ::= <izraz_pridruzivanja>":
        izraz_pridruzivanja(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        node.props.update({"type_list": [node_type_0]})

    elif prod == "<lista_argumenata> ::= <lista_argumenata> ZAREZ <izraz_pridruzivanja>":
        lista_argumenata(node.children[0], table)

        izraz_pridruzivanja(node.children[2], table)

        node_type_list_0 = list.copy(node.children[0].props["type_list"])
        node_type_list_0.append(node.children[2].props["type"])

        node.props.update({"type_list": node_type_list_0})

def unarni_izraz(node, table):
    prod = node.get_production()

    if prod == "<unarni_izraz> ::= <postfiks_izraz>":
        postfiks_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]
        
        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<unarni_izraz> ::= OP_INC <unarni_izraz>" or prod == "<unarni_izraz> ::= OP_DEC <unarni_izraz>":
        #1
        unarni_izraz(node.children[1], table)

        #2
        node_type_1 = node.children[1].props["type"]
        l_expr = node.children[1].props["l_expr"]

        if l_expr == False or node_type_1 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

    elif prod == "<unarni_izraz> ::= <unarni_operator> <cast_izraz>":
        #1
        cast_izraz(node.children[1], table)

        #2
        node_type_1 = node.children[1].props["type"]
        if node_type_1 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

#def unarni_operator(node, table) -> u uputama pise da ne treba nista provjeravati

def cast_izraz(node, table):
    prod = node.get_production()

    if prod == "<cast_izraz> ::= <unarni_izraz>":
        unarni_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]
        
        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<cast_izraz> ::= L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>":
        #1
        ime_tipa(node.children[1], table)
        node_type_1 = node.children[1].props["type"]

        if node_type_1 == "void":
            print(node.get_error())
            sys.exit()

        #2 
        cast_izraz(node.children[3], table)
        node_type_3 = node.children[3].props["type"]

        if node_type_3 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3 
        #mislim da je provjeren s #1 i #2

        node.props.update({"type": node_type_1, "l_expr": False})

def ime_tipa(node, table):
    prod = node.get_production()

    if prod == "<ime_tipa> ::= <specifikator_tipa>":
        specifikator_tipa(node.children[0], table)

        node_type_0 = node.children[0].props["type"]

        node.props.update({"type": node_type_0})

    elif prod == "<ime_tipa> ::= KR_CONST <specifikator_tipa>":
        #1
        specifikator_tipa(node.children[1], table)
        
        #2
        node_type_1 = node.children[1].props["type"]

        if node_type_1 == "void":
            print(node.get_error())
            sys.exit()

        tip = "const(" + node_type_1 + ")"
        node.props.update({"type": tip})

def specifikator_tipa(node, table):
    prod = node.get_production()

    if prod == "<specifikator_tipa> ::= KR_VOID":
        node.props.update({"type": "void"})
    
    elif prod == "<specifikator_tipa> ::= KR_CHAR":
        node.props.update({"type": "char"})

    elif prod == "<specifikator_tipa> ::= KR_INT":
        node.props.update({"type": "int"})

def multiplikativni_izraz(node, table):
    prod = node.get_production()

    if prod == "<multiplikativni_izraz> ::= <cast_izraz>":
        cast_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_PUTA <cast_izraz>" 
          or prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_DIJELI <cast_izraz>" 
          or prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_MOD <cast_izraz>"):
        
        #1
        multiplikativni_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        cast_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def aditivni_izraz(node, table):
    prod = node.get_production()

    if prod == "<aditivni_izraz> ::= <multiplikativni_izraz>":
        multiplikativni_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<aditivni_izraz> ::= <aditivni_izraz> PLUS <multiplikativni_izraz>" 
          or prod == "<aditivni_izraz> ::= <aditivni_izraz> MINUS <multiplikativni_izraz>"):
        
        #1
        aditivni_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        multiplikativni_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def odnosni_izraz(node, table):
    prod = node.get_production()

    if prod == "<odnosni_izraz> ::= <aditivni_izraz>":
        aditivni_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_LT <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_GT <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_LTE <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_GTE <aditivni_izraz>"):
        
        #1
        odnosni_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        aditivni_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def jednakosni_izraz(node, table):
    prod = node.get_production()

    if prod == "<jednakosni_izraz> ::= <odnosni_izraz>":
        odnosni_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<jednakosni_izraz> ::= <jednakosni_izraz> OP_EQ <odnosni_izraz>"
          or prod == "<jednakosni_izraz> ::= <jednakosni_izraz> OP_NEQ <odnosni_izraz>"):
        
        #1
        jednakosni_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        odnosni_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_i_izraz(node, table):
    prod = node.get_production()

    if prod == "<bin_i_izraz> ::= <jednakosni_izraz>":
        jednakosni_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_i_izraz> ::= <bin_i_izraz> OP_BIN_I <jednakosni_izraz>":
        #1
        bin_i_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        jednakosni_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_xili_izraz(node, table):
    prod = node.get_production()

    if prod == "<bin_xili_izraz> ::= <bin_i_izraz>":
        bin_i_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_xili_izraz> ::= <bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>":
        #1
        bin_xili_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_i_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_ili_izraz(node, table):
    prod = node.get_production()

    if prod == "<bin_ili_izraz> ::= <bin_xili_izraz>":
        bin_xili_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_ili_izraz> ::= <bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>":
        #1
        bin_ili_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_xili_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def log_i_izraz(node, table):
    prod = node.get_production()

    if prod == "<log_i_izraz> ::= <bin_ili_izraz>":
        bin_ili_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<log_i_izraz> ::= <log_i_izraz> OP_I <bin_ili_izraz>":
        #1
        log_i_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_ili_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})    

def log_ili_izraz(node, table):
    prod = node.get_production()  

    if prod == "<log_ili_izraz> ::= <log_i_izraz>":
        log_i_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<log_ili_izraz> ::= <log_ili_izraz> OP_ILI <log_i_izraz>":
        #1
        log_ili_izraz(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        log_i_izraz(node.children[2], table)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})  

def izraz_pridruzivanja(node, table):
    prod = node.get_production()

    if prod == "<izraz_pridruzivanja> ::= <log_ili_izraz>":
        log_ili_izraz(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<izraz_pridruzivanja> ::= <postfiks_izraz> OP_PRIDRUZI <izraz_pridruzivanja>":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        l_expr = node.children[0].props["l_expr"]
        if l_expr == False:
            print(node.get_error())
            sys.exit()

        #3
        izraz_pridruzivanja(node.children[2], table)

        #4
        node_type_0 = node.children[0].props["type"]
        node_type_2 = node.children[2].props["type"]

        if (node_type_0 == "int" or node_type_0 == "const(int)"):
            if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_type_0 == "char" or node_type_0 == "const(char)"):
            if node_type_2 not in ["char", "const(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_type_0 == "niz(int)"):
            if node_type_2 not in ["niz(int)"]:
                print(node.get_error())
                sys.exit()
        elif (node_type_0 == "niz(char"):
            if node_type_2 not in ["niz(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_type_0 == "niz(const(int))"):
            if node_type_2 not in ["niz(int)", "niz(const(int))"]:
                print(node.get_error())
                sys.exit()
        elif (node_type_0 == "niz(const(char))"):
            if node_type_2 not in ["niz(char)", "niz(const(char)"]:
                print(node.get_error())
                sys.exit()
        elif "funkcija" in node_type_0 and node_type_0 != node_type_2:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": node_type_0, "l_expr": False}) 

def izraz(node, table):
    prod = node.get_production()

    if prod == "<izraz> ::= <izraz_pridruzivanja>":
        izraz_pridruzivanja(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})
    
    elif prod == "<izraz> ::= <izraz> ZAREZ <izraz_pridruzivanja>":
        #1
        izraz(node.children[0], table)

        #2
        izraz(node.children[2], table)

        node_type_2 = node.children[2].props["type"]

        node.props.update({"type": node_type_2, "l_expr": False})

def slozena_naredba(node, table):
    prod = node.get_production()

    if prod == "<slozena_naredba> ::= L_VIT_ZAGRADA <lista_naredbi> D_VIT_ZAGRADA":
        lista_naredbi(node.children[1], table)

    elif prod == "<slozena_naredba> ::= L_VIT_ZAGRADA <lista_deklaracija> <lista_naredbi> D_VIT_ZAGRADA":
        lista_deklaracija(node.children[1], table)

        lista_naredbi(node.children[2], table)

def lista_naredbi(node, table):
    prod = node.get_production()

    if prod == "<lista_naredbi> ::= <naredba>":
        naredba(node.children[0], table)

    elif prod == "<lista_naredbi> ::= <lista_naredbi> <naredba>":
        lista_naredbi(node.children[0], table)

        naredba(node.children[1], table)

def naredba(node, table):
    prod = node.get_production()

    if prod == "<naredba> ::= <slozena_naredba>":
        child_table = TableNode()
        table.add_child(child_table)

        slozena_naredba(node.children[0], child_table)

    elif prod == "<naredba> ::= <izraz_naredba>":
        izraz_naredba(node.children[0], table)

    elif prod == "<naredba> ::= <naredba_grananja>":
        naredba_grananja(node.children[0], table)

    elif prod == "<naredba> ::= <naredba_petlje>":
        naredba_petlje(node.children[0], table)

    elif prod == "<naredba> ::= <naredba_skoka>":
        naredba_skoka(node.children[0], table)

def izraz_naredba(node, table):
    prod = node.get_production()

    if prod == "<izraz_naredba> ::= TOCKAZAREZ":
        node.props.update({"type": "int"})
    elif prod == "<izraz_naredba> ::= <izraz> TOCKAZAREZ":
        izraz(node.children[0], table)

        node.props.update({"type": node.children[0].props["type"]})

def naredba_grananja(node, table):
    prod = node.get_production()

    if prod == "<naredba_grananja> ::= KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba>":
        #1
        izraz(node.children[2], table)

        #2
        node_type_1 = node.children[2].props["type"]
        if node_type_1 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        naredba(node.children[4], table)
    elif prod == "<naredba_grananja> ::= KR_IF L_ZAGRADA <izraz> D_ZAGRADA <naredba> KR_ELSE <naredba>":
        #1
        izraz(node.children[2], table)

        #2
        node_type_1 = node.children[2].props["type"]
        if node_type_1 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        naredba(node.children[4], table)

        #4
        naredba(node.children[6], table)

def naredba_petlje(node, table):
    prod = node.get_production()

    if prod == "<naredba_petlje> ::= KR_WHILE L_ZAGRADA <izraz> D_ZAGRADA <naredba>":
        #1
        izraz(node.children[2], table)

        #2
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #3
        naredba(node.children[4], table)
    elif prod == "<naredba_petlje> ::= KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> D_ZAGRADA <naredba>":
        #1
        izraz_naredba(node.children[2], table)

        #2
        izraz_naredba(node.children[3], table)

        #3
        node_type_3 = node.children[3].props["type"]
        if node_type_3 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #4
        naredba(node.children[5], table)
    elif prod == "<naredba_petlje> ::= KR_FOR L_ZAGRADA <izraz_naredba> <izraz_naredba> <izraz> D_ZAGRADA <naredba>":
        #1
        izraz_naredba(node.children[2], table)

        #2
        izraz_naredba(node.children[3], table)

        #3
        node_type_3 = node.children[3].props["type"]
        if node_type_3 not in ["int", "char", "const(int)", "const(char)"]:
            print(node.get_error())
            sys.exit()

        #4
        izraz(node.children[4], table)

        #5
        naredba(node.children[6], table)

def naredba_skoka(node, table):
    prod = node.get_production()

    if (prod == "<naredba_skoka> ::= KR_CONTINUE TOCKAZAREZ"
            or prod == "<naredba_skoka> ::= KR_BREAK TOCKAZAREZ"):
        node_parent = node
        is_in_loop = False
        
        while node_parent.parent:
            node_parent = node_parent.parent
            if node_parent.props["name"] == "<naredba_petlje>":
                is_in_loop = True
                break

        if not is_in_loop:
            print(node.get_error())
            sys.exit()
    elif prod == "<naredba_skoka> ::= KR_RETURN TOCKAZAREZ":
        node_return_type = None
        table_parent = table
        while table_parent.parent:
            table_parent = table_parent.parent
            for name in table_parent.table:
                if "(func)" in name:
                    node_return_type = table_parent.table[name]["return_type"]

        if node_return_type != "void":
            print(node.get_error())
            sys.exit()
    elif prod == "<naredba_skoka> ::= KR_RETURN <izraz> TOCKAZAREZ":
        #1
        izraz(node.children[1], table)
        
        #2
        if not table.parent:
            print(node.get_error())
            sys.exit()

        node_return_type = None
        table_parent = table
        while table_parent.parent:
            table_parent = table_parent.parent
            for name in table_parent.table:
                if "(func)" in name:
                    node_return_type = table_parent.table[name]["return_type"]

        if not node_return_type or node_return_type == "void":
            print(node.get_error())
            sys.exit()

        node_type_1 = node.children[1].props["type"]

        if (node_return_type == "int" or node_return_type == "const(int)"):
            if node_type_1 not in ["int", "char", "const(int)", "const(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_return_type == "char" or node_return_type == "const(char)"):
            if node_type_1 not in ["char", "const(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_return_type == "niz(int)"):
            if node_type_1 not in ["niz(int)"]:
                print(node.get_error())
                sys.exit()
        elif (node_return_type == "niz(char"):
            if node_type_1 not in ["niz(char)"]:
                print(node.get_error())
                sys.exit()
        elif (node_return_type == "niz(const(int))"):
            if node_type_1 not in ["niz(int)", "niz(const(int))"]:
                print(node.get_error())
                sys.exit()
        elif (node_return_type == "niz(const(char))"):
            if node_type_1 not in ["niz(char)", "niz(const(char)"]:
                print(node.get_error())
                sys.exit()
        elif "funkcija" in node_return_type and node_return_type != node_type_1:
            print(node.get_error())
            sys.exit()

def lista_parametara(node, table):
    prod = node.get_production()

    if prod == "<lista_parametara> ::= <deklaracija_parametra>":
        deklaracija_parametra(node.children[0], table)

        node_type_0 = node.children[0].props["type"]
        node_name_0 = node.children[0].props["name"]

        node.props.update({"type_list": [node_type_0], "names": [node_name_0]})
    elif prod == "<lista_parametara> ::= <lista_parametara> ZAREZ <deklaracija_parametra>":
        lista_parametara(node.children[0], table)
        deklaracija_parametra(node.children[2], table)

        node_name_2 = node.children[2].props["name"]
        for name in node.children[0].props["names"]:
            if name == node_name_2:
                print(node.get_error())
                sys.exit()
                
        node.props.update({"type_list": node.children[0].props["type_list"] + [node.children[2].props["type"]], "names": node.children[0].props["names"] + [node_name_2]})
def deklaracija_parametra(node, table):
    prod = node.get_production()

    if prod == "<deklaracija_parametra> ::= <ime_tipa> IDN":
        #1
        ime_tipa(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 == "void":
            print(node.get_error())
            sys.exit()

        node.props.update({"type": node_type_0, "name": node.children[1].props["name"].split()[2]})
    elif prod == "<deklaracija_parametra> ::= <ime_tipa> IDN L_UGL_ZAGRADA D_UGL_ZAGRADA":
        #1
        ime_tipa(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 == "void":
            print(node.get_error())
            sys.exit()

        node.props.update({"type": f"niz({node_type_0})", "name": node.children[1].props["name"].split()[2]})

def lista_deklaracija(node, table):
    prod = node.get_production()

    if prod == "<lista_deklaracija> ::= <deklaracija>":
        deklaracija(node.children[0], table)
    elif prod == "<lista_deklaracija> ::= <lista_deklaracija> <deklaracija>":
        lista_deklaracija(node.children[0], table)
        deklaracija(node.children[1], table)

def deklaracija(node, table):
    prod = node.get_production()

    if prod == "<deklaracija> ::= <ime_tipa> <lista_init_deklaratora> TOCKAZAREZ":
        #1
        ime_tipa(node.children[0], table)

        #2
        node.children[1].props.update({"i_type": node.children[0].props["type"]})
        lista_init_deklaratora(node.children[1], table)

def lista_init_deklaratora(node, table):
    prod = node.get_production()

    if prod == "<lista_init_deklaratora> ::= <init_deklarator>":
        node.children[0].props.update({"i_type": node.props["i_type"]})
        init_deklarator(node.children[0], table)
    elif prod == "<lista_init_deklaratora> ::= <lista_init_deklaratora> ZAREZ <init_deklarator>":
        node.children[0].props.update({"i_type": node.props["i_type"]})
        lista_init_deklaratora(node.children[0], table)

        node.children[2].props.update({"i_type": node.props["i_type"]})
        init_deklarator(node.children[2], table)

def init_deklarator(node, table):
    prod = node.get_production()

    if prod == "<init_deklarator> ::= <izravni_deklarator>":
        #1
        node.children[0].props.update({"i_type": node.props["i_type"]})
        izravni_deklarator(node.children[0], table)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 in ["const(int)", "const(char)", "niz(const(int))", "niz(const(char))"]:
            print(node.get_error())
            sys.exit()
    elif prod == "<init_deklarator> ::= <izravni_deklarator> OP_PRIDRUZI <inicijalizator>":
        #1
        node.children[0].props.update({"i_type": node.props["i_type"]})
        izravni_deklarator(node.children[0], table)

        #2
        inicijalizator(node.children[2], table)

        #3
        node_type_0 = node.children[0].props["type"]
        if node_type_0 in ["int", "char", "const(int)", "const(char)"]:
            node_type_2 = node.children[2].props["type"]
            if node_type_0 in ["char", "const(char)"] and node_type_2 not in ["char", "const(char)"]:
                print(node.get_error())
                sys.exit()
            elif node_type_0 in ["int", "const(int)"] and node_type_2 not in ["int", "const(int)", "char", "const(char)"]:
                print(node.get_error())
                sys.exit()
        elif node_type_0 in ["niz(int)", "niz(char)", "niz(const(int))", "niz(const(char))"]:
            node_elem_num_0 = node.children[0].props["elem_num"]
            node_elem_num_2 = node.children[2].props["elem_num"]

            if node_elem_num_0 < node_elem_num_2:
                print(node.get_error())
                sys.exit()

            node_type_0_shortened = node_type_0.split("niz(")[1][:-1]

            for type in node.children[2].props["type_list"]:
                if node_type_0_shortened in ["char", "const(char)"] and type not in ["char", "const(char)"]:
                    print(node.get_error())
                    sys.exit()
                elif node_type_0_shortened in ["int", "const(int)"] and type not in ["int", "const(int)", "char", "const(char)"]:
                    print(node.get_error())
                    sys.exit()
        else:
            print(node.get_error())
            sys.exit()

def izravni_deklarator(node, table):
    prod = node.get_production()

    if prod == "<izravni_deklarator> ::= IDN":
        #1
        node_i_type = node.props["i_type"]
        if node_i_type == "void":
            print(node.get_error())
            sys.exit()
        
        #2
        node_name_0 = node.children[0].props["name"].split()[2]
        if table.table.get(node_name_0):
            print(node.get_error())
            sys.exit()

        #3
        table.table.update({
            node_name_0: {
                "type": node_i_type
            }
        })

        node.props["type"] = node_i_type
    elif prod == "<izravni_deklarator> ::= IDN L_UGL_ZAGRADA BROJ D_UGL_ZAGRADA":
        #1
        node_i_type = node.props["i_type"]
        if node_i_type == "void":
            print(node.get_error())
            sys.exit()
        
        #2
        node_name_0 = node.children[0].props["name"].split()[2]
        if table.table.get(node_name_0):
            print(node.get_error())
            sys.exit()

        #3
        node_value_2 = int(node.children[2].props["name"].split()[2])
        if node_value_2 <= 0 or node_value_2 > 1024:
            print(node.get_error())
            sys.exit()

        #4
        table.table.update({
            node_name_0: {
                "type": f"niz({node_i_type})"
            }
        })
        node.props["type"] = f"niz({node_i_type})"
        node.props["elem_num"] = node_value_2
    elif prod == "<izravni_deklarator> ::= IDN L_ZAGRADA KR_VOID D_ZAGRADA":
        #1
        node_i_type = node.props["i_type"]
        node_name_0_not_func = node.children[0].props["name"].split()[2]
        node_name_0 = node.children[0].props["name"].split()[2] + " (func)"
        if table.table.get(node_name_0):
            return_type = table.table.get(node_name_0)["return_type"]
            params = table.table.get(node_name_0)["params"]
            if return_type != node_i_type or len(params) != 0:
                print(node.get_error())
                sys.exit()
            # if node.parent.props["type"] != f"funkcija(void -> {node_i_type})":
            #     print(node.get_error())
            #     sys.exit()
        elif table.table.get(node_name_0_not_func):
            print(node.get_error())
            sys.exit()
    
        #2
        else:
            table.table.update({
                node_name_0: {
                    "defined": False,
                    "params": list(),
                    "return_type": node_i_type
                }
            })
        
        node.props["type"] = f"funkcija(void -> {node_i_type})"
    elif prod == "<izravni_deklarator> ::= IDN L_ZAGRADA <lista_parametara> D_ZAGRADA":
        #1
        lista_parametara(node.children[2], table)

        #2
        node_i_type = node.props["i_type"]
        node_type_list_2 = node.children[2].props["type_list"]
        node_name_0_not_func = node.children[0].props["name"].split()[2]
        node_name_0 = node.children[0].props["name"].split()[2] + " (func)"
        if table.table.get(node_name_0):
            return_type = table.table.get(node_name_0)["return_type"]
            params = table.table.get(node_name_0)["params"]
            if return_type != node_i_type or params != node_type_list_2:
                print(node.get_error())
                sys.exit()
            # if node.parent.props["type"] != f"funkcija({str(node_type_list_2)} -> {node_i_type})":
            #     print(node.get_error())
            #     sys.exit()
        elif table.table.get(node_name_0_not_func):
            print(node.get_error())
            sys.exit()
        #3
        else:
            table.table.update({
                node_name_0: {
                    "defined": False,
                    "params": node_type_list_2,
                    "return_type": node_i_type
                }
            })

        type_ = "funkcija("
        type_list_ = ("[" + ", ".join(node_type_list_2) + "]") if len(node_type_list_2) > 0 else "void"
        type_ += (type_list_ + " -> " + node_i_type + ")")
        node.props["type"] = type_
        #node.props["type"] = f"funkcija({str(node_type_list_2)} -> {node_i_type})" #str ostavi navodnike pa bude npr ['char'] umj [char]

def inicijalizator(node, table):
    prod = node.get_production()

    if prod == "<inicijalizator> ::= <izraz_pridruzivanja>":
        izraz_pridruzivanja(node.children[0], table)

        node_niz_znakova = check_for_child_node(node, "NIZ_ZNAKOVA")
        if node_niz_znakova:
            niz_znakova_value = " ".join(node_niz_znakova.props["name"].split()[2:])[1:-1]

            node.props.update({"elem_num": len(niz_znakova_value) + 1})

            node_type_list = list()
            for i in range(len(niz_znakova_value) + 1): #lista duljine br-elem?
                node_type_list.append("char")
            node.props.update({"type_list": node_type_list})
        else:
            node.props.update({"type": node.children[0].props["type"]})
    elif prod == "<inicijalizator> ::= L_VIT_ZAGRADA <lista_izraza_pridruzivanja> D_VIT_ZAGRADA":
        lista_izraza_pridruzivanja(node.children[1], table)

        node.props.update({"elem_num": node.children[1].props["elem_num"], "type_list": node.children[1].props["type_list"]})

def lista_izraza_pridruzivanja(node, table):
    prod = node.get_production()

    if prod == "<lista_izraza_pridruzivanja> ::= <izraz_pridruzivanja>":
        #1
        izraz_pridruzivanja(node.children[0], table)

        node.props.update({"type_list": [node.children[0].props["type"]], "elem_num": 1})
    elif prod == "<lista_izraza_pridruzivanja> ::= <lista_izraza_pridruzivanja> ZAREZ <izraz_pridruzivanja>":
        #1
        lista_izraza_pridruzivanja(node.children[0], table)

        #2
        izraz_pridruzivanja(node.children[2], table)
        node.props.update({"type_list": node.children[0].props["type_list"] + [node.children[2].props["type"]], "elem_num": node.children[0].props["elem_num"] + 1})
    
def check_for_child_node(node, name):
    exists = None    

    if node.props["name"].split()[0] == name:
        return node

    if node.children:
        for child in node.children:
            exists = check_for_child_node(child, name)

            if exists:
                break

    return exists

#ako bude bilo potrebe
# TODO
def check_for_parent_node(node, parameter_name, parameter):
    pass