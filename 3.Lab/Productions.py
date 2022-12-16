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
        if node_type_2 not in ["int", "char", "const int", "const char"]:
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

        return_type = node_type_0.split(" -> ")[1]
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

        if len(param) != len(arg):
            print(node.get_error())
            sys.exit()

        for param, arg in zip(node_params_0, node_args_2):
            if (param == "int" or param == "const int"):
                if arg not in ["int", "char", "const int", "const char"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "char" or param == "const char"):
                if arg not in ["char", "const char"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(int)"):
                if arg not in ["niz(int)", "niz(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(char"):
                if arg not in ["niz(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(const(int))"):
                if arg not in ["niz(int)", "niz(const(int))", "niz(char)", "niz(const(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif (param == "niz(const(char))"):
                if arg not in ["niz(char)", "niz(const(char)"]:
                    print(node.get_error())
                    sys.exit()
            elif "funkcija" in param and param != arg:
                print(node.get_error())
                sys.exit()

        node.props.update({"type": return_type, "l_expr": False})

    elif prod == "<postfiks_izraz> ::= <postfiks_izraz> OP_INC" or prod == "<postfiks_izraz> ::= <postfiks_izraz> OP_DEC":
        #1
        postfiks_izraz(node.children[0], table)

        #2
        l_expr = node.children[0].props["l_expr"]
        node_type_0 = node.children[0].props["type"]

        if l_expr == False or node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def lista_argumenata(node, tablica):
    prod = node.get_production()

    if prod == "<lista_argumenata> ::= <izraz_pridruzivanja>":
        izraz_pridruzivanja(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        node.props.update({"type_list": list(node_type_0)})

    elif prod == "<lista_argumenata> ::= <lista_argumenata> ZAREZ <izraz_pridruzivanja>":
        lista_argumenata(node.children[0], tablica)

        izraz_pridruzivanja(node.children[2], tablica)

        node_type_list_0 = list.copy(node.children[0].props["types"])
        node_type_list_0.append(node.children[2].props["type"])

        node.props.update({"type_list": node_type_list_0})

def unarni_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<unarni_izraz> ::= <postfiks_izraz>":
        postfiks_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]
        
        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<unarni_izraz> ::= OP_INC <unarni_izraz>" or prod == "<unarni_izraz> ::= OP_DEC <unarni_izraz>":
        #1
        unarni_izraz(node.children[1], tablica)

        #2
        node_type_1 = node.children[1].props["type"]
        l_expr = node.children[1].props["l_expr"]

        if l_expr == False or node_type_1 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

    elif prod == "<unarni_izraz> ::= <unarni_operator> <cast_izraz>":
        #1
        cast_izraz(node.children[1], tablica)

        #2
        node_type_1 = node.children[1].props["type"]
        if node_type_1 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

#def unarni_operator(node, tablica) -> u uputama pise da ne treba nista provjeravati

def cast_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<cast_izraz> ::= <unarni_izraz>":
        unarni_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]
        
        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<cast_izraz> ::= L_ZAGRADA <ime_tipa> D_ZAGRADA <cast_izraz>":
        #1
        ime_tipa(node.children[1], tablica)
        node_type_1 = node.children[1].props["type"]

        if node_type_1 == "void":
            print(node.get_error())
            sys.exit()

        #2 
        cast_izraz(node.children[3], tablica)
        node_type_3 = node.children[3].props["type"]

        if node_type_3 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3 
        #mislim da je provjeren s #1 i #2

        node.props.update({"type": node_type_1, "l_expr": False})

def ime_tipa(node, tablica):
    prod = node.get_production()

    if prod == "<ime_tipa> ::= <specifikator_tipa>":
        specifikator_tipa(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]

        node.props.update({"type": node_type_0})

    elif prod == "<ime_tipa> ::= KR_CONST <specifikator_tipa>":
        #1
        specifikator_tipa(node.children[1], tablica)
        
        #2
        node_type_1 = node.children[1].props["type"]

        if node_type_1 == "void":
            print(node.get_error())
            sys.exit()

        tip = "const(" + node_type_1 + ")"
        node.props.update({"type": tip})

def specifikator_tipa(node, tablica):
    prod = node.get_production()

    if prod == "<specifikator_tipa> ::= KR_VOID":
        node.props.update({"type": "void"})
    
    elif prod == "<specifikator_tipa> ::= KR_CHAR":
        node.props.update({"type": "char"})

    elif prod == "<specifikator_tipa> ::= KR_INT":
        node.props.update({"type": "int"})

def multiplikativni_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<multiplikativni_izraz> ::= <cast_izraz>":
        cast_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_PUTA <cast_izraz>" 
          or prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_DIJELI <cast_izraz>" 
          or prod == "<multiplikativni_izraz> ::= <multiplikativni_izraz> OP_MOD <cast_izraz>"):
        
        #1
        multiplikativni_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        cast_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def aditivni_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<aditivni_izraz> ::= <multiplikativni_izraz>":
        multiplikativni_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<aditivni_izraz> ::= <aditivni_izraz> PLUS <multiplikativni_izraz>" 
          or prod == "<aditivni_izraz> ::= <aditivni_izraz> MINUS <multiplikativni_izraz>"):
        
        #1
        aditivni_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        multiplikativni_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def odnosni_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<odnosni_izraz> ::= <aditivni_izraz>":
        aditivni_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_LT <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_GT <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_LTE <aditivni_izraz>"
          or prod == "<odnosni_izraz> ::= <odnosni_izraz> OP_GTE <aditivni_izraz>"):
        
        #1
        odnosni_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        aditivni_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def jednakosni_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<jednakosni_izraz> ::= <odnosni_izraz>":
        odnosni_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif (prod == "<jednakosni_izraz> ::= <jednakosni_izraz> OP_EQ <odnosni_izraz>"
          or prod == "<jednakosni_izraz> ::= <jednakosni_izraz> OP_NEQ <odnosni_izraz>"):
        
        #1
        jednakosni_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        odnosni_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_i_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<bin_i_izraz> ::= <jednakosni_izraz>":
        jednakosni_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_i_izraz> ::= <bin_i_izraz> OP_BIN_I <jednakosni_izraz>":
        #1
        bin_i_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        jednakosni_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_xili_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<bin_xili_izraz> ::= <bin_i_izraz>":
        bin_i_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_xili_izraz> ::= <bin_xili_izraz> OP_BIN_XILI <bin_i_izraz>":
        #1
        bin_xili_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_i_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def bin_ili_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<bin_ili_izraz> ::= <bin_xili_izraz>":
        bin_xili_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<bin_ili_izraz> ::= <bin_ili_izraz> OP_BIN_ILI <bin_xili_izraz>":
        #1
        bin_ili_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_xili_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})

def log_i_izraz(node, tablica):
    prod = node.get_production()

    if prod == "<log_i_izraz> ::= <bin_ili_izraz>":
        bin_ili_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<log_i_izraz> ::= <log_i_izraz> OP_I <bin_ili_izraz>":
        #1
        log_i_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        bin_ili_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})    

def log_ili_izraz(node, tablica):
    prod = node.get_production()  

    if prod == "<log_ili_izraz> ::= <log_i_izraz>":
        log_i_izraz(node.children[0], tablica)

        node_type_0 = node.children[0].props["type"]
        l_expr = node.children[0].props["l_expr"]

        node.props.update({"type": node_type_0, "l_expr": l_expr})

    elif prod == "<log_ili_izraz> ::= <log_ili_izraz> OP_ILI <log_i_izraz>":
        #1
        log_ili_izraz(node.children[0], tablica)

        #2
        node_type_0 = node.children[0].props["type"]
        if node_type_0 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        #3
        log_i_izraz(node.children[2], tablica)

        #4
        node_type_2 = node.children[2].props["type"]
        if node_type_2 not in ["int", "char", "const int", "const char"]:
            print(node.get_error())
            sys.exit()

        node.props.update({"type": "int", "l_expr": False})        