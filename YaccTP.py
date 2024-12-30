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
    "Header : Decl Decls"
    p[0] = p[1] + p[2]

def p_SingleHeader(p):
    "Header : Decl"
    p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declarations ####

def p_MultDecl(p):
    "Decls : Decl Decls"
    p[0] = p[1] + p[2]

def p_SingleDecl(p):
    "Decls : Decl"
    p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declaration [Int - Array - Matrix] ####

def p_IntDecl(p):
    "Decl : Var NAME"
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: p.parser.memPointer})
        p[0] = f"PUSHI 0\n"
        p.parser.memPointer += 1
    else:
        print(f"Variable {p[2]} already declared")
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.") # acho que isto faz 2 em 1

def p_ArrayDecl(p):
    "Decl : Var NAME '[' Var ']'"
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]))})
        p[0] = f"PUSHN {p[4]}\n"
        p.parser.memPointer += int({p[4]})
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")

def p_MatrixDecl(p):
    "Decl : Var NAME '[' Var ']' '[' Var ']'"
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]), int(p[7]))})
        memSpace = int(p[3]) * int(p[7])
        p[0] = f"PUSHN {str(memSpace)}\n" # Porquê str e não int? 
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
    "Conditions : IF '(' cond ')' THEN '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"l{p.parser.idLabel}: NOP\n" # JZ - Jump Zero: Salta para o l{label} se a condição tiver valor 0 (false)
    p.parser.idLabel += 1                                                            # NOP - No Operation (não percebi porque isto é preciso)

def p_CondIfThenOtherwise(p):
    "Conditions : IF '(' cond ')' THEN '{' Code '}' OTHERWISE '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"JUMP l{p.parser.idLabel}f\nl{p.parser.idLabel}: NOP\n" + p[8] + f"l{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1

def p_WhileDo(p):
    "WhileDo : WHILE '(' cond ')' DO '{' Code '}'"
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[3] + f"JZ l{p.parser.idLabel}f\n" + p[6] + f"JUMP l{p.parser.labels}c\nl{p.parser.labels}f: NOP\n"
    p.parser.idLabel += 1

def p_RepeatUntil(p):
    "RepeatUntil : REPEAT '{' Code '}' UNTIL '(' cond ')'" 
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[7] + f"JZ l{p.parser.idLabel}f\n" + p[3] + f"JUMP l{p.parser.labels}c\nl{p.parser.labels}f: NOP\n"
    p.parser.idLabel += 1
     
#___________________________________________________________________________________________________________#

#### Assigning ####

def p_ExpressionAssign(p):
    "Assign : NAME '=' Expr"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = p[3] + f"STOREG {var}\n"
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an integer.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_ArrayAssign(p):
     "Assign : NAME '[' Var ']' '=' Expr"
     if p[1] in p.parser.trackmap:
          varInfo = p.parser.trackmap.get(p[1])
          if len(varInfo) == 2:
                p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + p[6] + 'STOREN\n'
          else:
               raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_MatrixAssign(p):
     "Assign : NAME '[' Var ']' '[' Var ']' '=' Expr"
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

def p_ExpressionOperations(p):
    """Expression : Expression '+' Expression
                  | Expression '-' Expression
                  | Expression EQ Expression
                  | Expression NEQ Expression
                  | '!' Expression
                  | Expression '>' Expression
                  | Expression MOREEQ Expression
                  | Expression '<' Expression
                  | Expression LESSEQ Expression
                  | Expression AND Expression
                  | Expression OR Expression
                  | Expression '*' Expression
                  | Expression '/' Expression
                  | Expression '%' Expression
                  | Var """

    if (p[2] == '+'):
          p[0] = p[1] + p[3] + "PLUS \n"
    elif (p[2] == '-'):
        p[0] = p[1] + p[3] + "MINUS \n"
    elif (p[2] == "=="):
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
    elif (p[2] == '*'):
        p[0] = p[1] + p[3] + "MULT \n"
    elif (p[2] == '/'):
        p[0] = p[1] + p[3] + "DIV \n"
    elif (p[2] == '%'):
        p[0] = p[1] + p[3] + "MOD \n"
    elif (p[1] == "Var"):
        p[0] = p[1]

def p_Expr_base(p):
    "Expr : '(' Expr ')'"
    p[0] = p[2]

def p_condition_base(p):
    "condition : '(' condition ')'"
    p[0] = p[2]

#___________________________________________________________________________________________________________#

#### Acessing Vars (Num - Array - Matrix ) ####

def p_VarNum(p):
    "Var : NAME"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = f"PUSHG {var}\n"
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an integer.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_VarArray(p):
    "Var : NAME '[' Var ']'"
    if p[1] in p.parser.trackmap:
        varInfo = p.parser.trackmap.get(p[1])
        if len(varInfo) == 2:
            p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + 'LOADN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_VarMatrix(p):
    "Var : NAME '[' Var ']' '[' Var ']'"
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
    "Print : print '(' Expr ')'"
    p[0] = p[3] + 'WRITEI\nPUSHS "\\n"\nWRITES\n'

def p_PrintArrMat(p):
    "Print : print '(' Var ')'"
    if p[3] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[3])
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
            raise TypeError(f"Line{p.lineno(2)}, {p[3]} is not an array or matrix.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[3]} is not declared.")

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

'''
# Test

def main():
    # Header
    int a;
    int b;
    
    # Code
    a = 5;
    b = 6;
    
    while (a < b) do {
        a = a + 1;
    }
    
    repeat {
        b = b - 1;
    } until (b == 0);
    
    if (a > b) then {
        a = a * 2;
    } otherwise {
        b = b * 2;
    }
    
    print a;
    
'''