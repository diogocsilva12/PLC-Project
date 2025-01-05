from LexTP import tokens
import ply.yacc as yacc
import sys
#___________________________________________________________________________________________________________#

#### Program Structure ####

def p_Program(p):
    "Program : Header Code"
    p[0] = p[1] + "START\n" + p[2] + "STOP\n"

#___________________________________________________________________________________________________________#

#### Header Structure ####

def p_WOHeader(p):
    "Program : Code"
    p[0] = "START\n" + p[1] + "STOP\n"

def p_MultHeader(p):
    "Header : Header Decl"
    p[0] = p[1] + p[2]

def p_SingleHeader(p):
    "Header : Decl"
    p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declaration [Int - Array - Matrix] ####

def p_IntDecl(p):
    "Decl : VAR NAME"  #example: Var a
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: p.parser.memPointer})
        p[0] = "PUSHI 0\n"
        p.parser.memPointer += 1
    else:
        print(f"Variable {p[2]} already declared")
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.") # acho que isto faz 2 em 1

def p_ArrayDecl(p):
    "Decl : VAR NAME '[' NUM ']'" #example: Var a[3]  # Array tem de permitir Expr para ver índices (letras) nos ciclos
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]))})
        p[0] = f"PUSHN {p[4]}\n"
        p.parser.memPointer += int({p[4]})
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")

def p_MatrixDecl(p):
    "Decl : VAR NAME '[' Expr ']' '[' Expr ']'" #example: Var a[3][4]   # Matriz tem de permitir Expr para ver índices (letras) nos ciclos 
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]), int(p[7]))})
        memSpace = int(p[4]) * int(p[7])
        p[0] = f"PUSHN {str(memSpace)}\n" # Porquê str e não int? R: Porque memSpace é inteiro e queremos converter para string
        p.parser.memPointer += memSpace
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")

#___________________________________________________________________________________________________________#

#### Code Structure ####

def p_MultCode(p):
    "Code : Code Codes"
    p[0] = p[1] + p[2]

def p_SingleCode(p):
    "Code : Codes"
    p[0] = p[1]

def p_Codes(p):
    """Codes : Conditions
            | WhileDo
            | RepeatUntil
            | Assign
            | Print
    """
    p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Cycles and Conditions ####

def p_CondIfThen(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"l{p.parser.idLabel}: NOP\n" # JZ - Jump Zero: Salta para o l{label} se a condição tiver valor 0 (false)
    p.parser.idLabel += 1                                                            # NOP - No Operation (não percebi porque isto é preciso)

def p_CondIfThenOtherwise(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}' OTHERWISE '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[7] + f"JUMP l{p.parser.idLabel}f\nl{p.parser.idLabel}: NOP\n" + p[11] + f"l{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1

def p_WhileDo(p):
    "WhileDo : WHILE '(' Condition ')' DO '{' Code '}'"
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[3] + f"JZ l{p.parser.idLabel}f\n" + p[7] + f"JUMP l{p.parser.idLabel}c\nl{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1

def p_RepeatUntil(p):
    "RepeatUntil : REPEAT '{' Code '}' UNTIL '(' Condition ')'" 
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[7] + f"JZ l{p.parser.idLabel}f\n" + p[3] + f"JUMP l{p.parser.idLabel}c\nl{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1
     
#___________________________________________________________________________________________________________#

#### Assigning ####

def p_ExpressionAssign(p):
    "Assign : NAME '=' Expr"  #exemplo : b = 2 
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = p[3] + f"STOREG {var}\n"
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} ## is not an integer.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_ArrayAssign(p):
     "Assign : NAME '[' NUM ']' '=' Expr"   # Array tem de permitir Expr para ver índices (letras) nos ciclos
     if p[1] in p.parser.trackmap:
          varInfo = p.parser.trackmap.get(p[1])
          if len(varInfo) == 2:
                p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + p[6] + 'STOREN\n'
          else:
               raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_MatrixAssign(p):
     "Assign : NAME '[' Expr ']' '[' Expr ']' '=' Expr"     # Matriz tem de permitir Expr para ver índices (letras) nos ciclos
     if p[1] in p.parser.trackmap:
            varInfo = p.parser.trackmap.get(p[1])
            if len(varInfo) == 3:
                  p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + f'PUSHI {varInfo[2]}\nMUL\n' + p[6] + 'ADD\n' + p[9] + 'STOREN\n'
            else:
                  raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not a matrix.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

#___________________________________________________________________________________________________________#

#### Expressions ####
def p_Expr_condition(p):
    'Expr : Condition'
    p[0] = p[1]

def p_Expr(p):
    'Expr : Variable'
    p[0] = p[1]

def p_expression_number(p):
    "Expr : NUM"
    p[0] = f"PUSHI {p[1]}\n"

'''
def p_opBasicSUM(p):
    'Expr : Expr "+" Expr'
    p[0] = p[1] + p[3] + 'ADD\n'
'''

def p_Expr_OP(p):
    """Expr : Expr "+" Expr
            | Expr "-" Expr
            | Expr "*" Expr
            | Expr "/" Expr
            | Expr "%" Expr
    """
    if (p[2] == '+'):
        p[0] = p[1] + p[3] + "ADD \n"
    elif (p[2] == '-'):
        p[0] = p[1] + p[3] + "SUB \n"
    elif (p[2] == '*'):
        p[0] = p[1] + p[3] + "MUL \n"
    elif (p[2] == '/'):
        p[0] = p[1] + p[3] + "DIV \n"
    elif (p[2] == '%'):
        p[0] = p[1] + p[3] + "MOD \n"            


def p_condLog(p):
    """Condition : Expr EQ Expr
                  | Expr NEQ Expr
                  | '!' Expr
                  | Expr '>' Expr
                  | Expr MOREEQ Expr
                  | Expr '<' Expr
                  | Expr LESSEQ Expr
                  | Expr AND Expr
                  | Expr OR Expr
                  """
     
    if (p[2] == "=="):
        p[0] = p[1] + p[3] + "EQ \n"
    elif (p[2] == "!="):
          p[0] = p[1] + p[3] + "NEQ \n"
    elif (p[1] == '!'):
        p[0] = p[2] + "NOT \n"
    elif (p[2] == '>'):
        p[0] = p[1] + p[3] + "MORE \n"
    elif (p[2] == ">="):
        p[0] = p[1] + p[3] + "MOREEQ \n"
    elif (p[2] == '<'):
        p[0] = p[1] + p[3] + "LESS \n"
    elif (p[2] == "<="):
        p[0] = p[1] + p[3] + "LESSEQ \n"
    elif (p[2] == "&&"):
        p[0] = p[1] + p[3] + "AND \n"
    elif (p[2] == "||"):
        p[0] = p[1] + p[3] + "OR \n"
    elif (p[1] == "Var"):
        p[0] = p[1]
    
    
def p_Expr_base(p):
    "Expr : '(' Expr ')'"
    p[0] = p[2]

def p_condition_base(p):
    "Condition : '(' Condition ')'"
    p[0] = p[2]

#___________________________________________________________________________________________________________#

#### Acessing Vars (Num - Array - Matrix ) ####

def p_VarNum(p):
    "Variable : NAME"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = f"PUSHG {var}\n"
        else:
            raise TypeError(f"Line {p.lineno(1)}, {p[1]} %% is not an integer.")
    else:
        raise Exception(f"Line {p.lineno(1)}, {p[1]} is not declared.")

def p_VarArray(p):
    "Variable : NAME '[' NUM ']'"
    if p[1] in p.parser.trackmap:
        varInfo = p.parser.trackmap.get(p[1])
        if len(varInfo) == 2:
            p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + 'LOADN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_VarMatrix(p):
    "Variable : NAME '[' NUM ']' '[' NUM ']'"
    if p[1] in p.parser.trackmap:
        varInfo = p.parser.trackmap.get(p[1])
        if len(varInfo) == 3:
            p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + f'PUSHI {varInfo[2]}\nMUL\n' + p[6] + 'ADD\n' + 'LOADN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not a matrix.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

#___________________________________________________________________________________________________________#

def p_error(p):
    print(f"Syntax error: token {p.value} on line {p.lineno}.")

#___________________________________________________________________________________________________________#

#### Print ####

def p_Print(p):
    "Print : PRINT Expr"
    p[0] = p[2] + 'WRITEI\nPUSHS "\\n"\nWRITES\n'

def p_PrintArrMat(p):
    "Print : PRINT NAME"
    if p[2] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[2])
        if type(var) == tuple:
            if len(var) == 2:
                array = f'PUSHS "[ "\nWRITES\n'
                for i in range(var[1]):
                    array += f'PUSHGP\nPUSHI {var[0]}\nPADD\nPUSHI {i}\nLOADN\nWRITEI\nPUSHS " "\nWRITES\n'
                array += f'PUSHS "]"\nWRITES\n'
                p[0] = array + 'PUSHS "\\n"\nWRITES\n'

            elif len(var) == 3:
                matrix = ""
                for i in range(var[1]):
                    matrix += f'PUSHS "[ "\nWRITES\n'
                    for j in range(var[2]):
                        matrix += f'PUSHGP\nPUSHI {var[0]}\nPADD\nPUSHI {var[2] * i + j}\nLOADN\nWRITEI\nPUSHS " "\nWRITES\n'
                    matrix += 'PUSHS "]\\n"\nWRITES\n'
                p[0] = matrix
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[2]} is not an array or matrix.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is not declared.")

#___________________________________________________________________________________________________________#

#### Parser Initializer ####
parser = yacc.yacc()
parser.trackmap = dict()
parser.idLabel = 0
parser.memPointer = 0


#___________________________________________________________________________________________________________#

#### Main ####

if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as file:
        assembly = parser.parse(file.read())
        if assembly:
            
            if len(sys.argv) > 2:
                with open(sys.argv[2], 'w') as output:
                    output.write(assembly)
                    print(f"{sys.argv[1]} compiled successfully!\nCheck the output in {sys.argv[2]}.")
            else:
                print(f"{sys.argv[1]} compiled successfully!")
        else:
            print("Empty!")
else:
    line = input(">")
    while line!="\n":
        print(parser.parse(line))
        line = input(">")


#___________________________________________________________________________________________________________#

