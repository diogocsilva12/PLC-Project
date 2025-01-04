from LexTP import tokens
import ply.yacc as yacc
import sys
import os
#___________________________________________________________________________________________________________#

#### Program Structure ####
# This rule defines the overall structure of the program.
# A program consists of a header and code. The header is optional.
def p_Program(p):
    "Program : Header Code"
    p[0] = p[1] + "START\n" + p[2] + "STOP\n" # Adds start and stop labels around the code.

#___________________________________________________________________________________________________________#

#### Header Structure ####
# If the program does not have a header, only the code is processed.
def p_WOHeader(p):
    "Program : Code"
    p[0] = "START\n" + p[1] + "STOP\n" # Adds start and stop labels around the code.
    
# This rule handles the case where the header contains multiple declarations.
def p_MultHeader(p):
    "Header : Header Decl"
    p[0] = p[1] + p[2] # Adds new declarations to the header.

# This rule handles the case where the header contains only a single declaration.
def p_SingleHeader(p):
    "Header : Decl"
    p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declaration [Int - Array - Matrix] ####

# This rule processes declarations of integer variables.
def p_IntDecl(p):
    "Decl : VAR NameList" #Namelist permite declarar variáveis ao mesmo tempo. O que faz é adicionar à lista de variáveis.
    for name in p[2]:
        if name not in p.parser.trackmap:
            p.parser.trackmap.update({name: p.parser.memPointer}) # Track variable in memory.
            p[0] = (p[0] or "") + "PUSHI 0\n"# Initialize variable to 0.
            p.parser.memPointer += 1  # Move memory pointer to the next slot.
        else:
            raise Exception(f"Variable {name} already declared.") # Handle re-declaration errors.

# podemos declarar variaveis das seguintes formas: uma por linha : var a; var b; var c; ou var a,b,c;
def p_NameList(p):
    """NameList : NAME
                | NameList ',' NAME"""
    if len(p) == 2:  # Apenas um nome
        p[0] = [p[1]]
    else:  # Lista com vírgulas
        p[0] = p[1] + [p[3]]

# This rule processes declarations of arrays.
def p_ArrayDecl(p):
    "Decl : VAR NAME '[' NUM ']'" #example: Var a[3]  # Array tem de permitir Expr para ver índices (letras) nos ciclos
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]))}) # Track variable in memory.
        p[0] = f"PUSHN {p[4]}\n" # Push array size to memory
        p.parser.memPointer += int({p[4]}) # Update memory pointer by array size.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")  # Handle re-declaration errors.

def p_MatrixDecl(p):
    "Decl : VAR NAME '[' NUM ']' '[' NUM ']'" #example: Var a[3][4]   # Matriz tem de permitir Expr para ver índices (letras) nos ciclos 
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]), int(p[7]))})
        memSpace = int(p[4]) * int(p[7]) # Calculate total memory required for the matrix.
        p[0] = f"PUSHN {memSpace}\n"  # Allocate memory for the matrix.
        p.parser.memPointer += memSpace  # Update memory pointer.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.") # Prevent redeclaration.

#___________________________________________________________________________________________________________#

#### Code Structure ####

# This rule handles the concatenation of multiple code blocks.
def p_MultCode(p):
    "Code : Code Codes"
    p[0] = p[1] + p[2] # Combine code sections

# This rule handles the case of a single block of code.
def p_SingleCode(p):
    "Code : Codes"
    p[0] = p[1]

# This rule defines the various code structures allowed.
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

# This rule handles an if-then statement.
def p_CondIfThen(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"l{p.parser.idLabel}: NOP\n" # JZ - Jump Zero: Salta para o l{label} se a condição tiver valor 0 (false)
    p.parser.idLabel += 1                                                            # NOP - No Operation (não percebi porque isto é preciso)

# This rule handles an if-then-else statement.
def p_CondIfThenOtherwise(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}' OTHERWISE '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[7] + f"JUMP l{p.parser.idLabel}f\nl{p.parser.idLabel}: NOP\n" + p[11] + f"l{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1

# This rule handles a while-do loop.
def p_WhileDo(p):
    "WhileDo : WHILE '(' Condition ')' DO '{' Code '}'"
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[3] + f"JZ l{p.parser.idLabel}f\n" + p[7] + f"JUMP l{p.parser.idLabel}c\nl{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1

# This rule handles a repeat-until loop.
def p_RepeatUntil(p):
    "RepeatUntil : REPEAT '{' Code '}' UNTIL '(' Condition ')'" 
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[7] + f"JZ l{p.parser.idLabel}f\n" + p[3] + f"JUMP l{p.parser.idLabel}c\nl{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1
     
#___________________________________________________________________________________________________________#

#### Assigning ####

# This rule handles variable assignments.
def p_ExpressionAssign(p):
    "Assign : NAME '=' Expr"  #exemplo : b = 2 
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = p[3] + f"STOREG {var}\n" # Store expression result in variable.
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} ## is not an integer.") # Ensure variable is an integer.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

# This rule handles array assignments.
def p_ArrayAssign(p):
     "Assign : NAME '[' Expr ']' '=' Expr"   # Array tem de permitir Expr para ver índices (letras) nos ciclos
     if p[1] in p.parser.trackmap:
          varInfo = p.parser.trackmap.get(p[1])
          if len(varInfo) == 2:
                p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + p[6] + 'STOREN\n' # Store to array position.
          else:
               raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

# This rule handles matrix assignments.
def p_MatrixAssign(p): # Nome[Expr][Expr] = Expr
     "Assign : NAME '[' Expr ']' '[' Expr ']' '=' Expr"     # Matriz tem de permitir Expr para ver índices (letras) nos ciclos
     if p[1] in p.parser.trackmap:
            varInfo = p.parser.trackmap.get(p[1])
            if len(varInfo) == 3:
                  p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n{p[3]}PUSHI {varInfo[2]}\nMUL\n{p[6]}ADD\n{p[9]}STOREN\n'
            else:
                  raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not a matrix.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

#___________________________________________________________________________________________________________#

#### Expressions ####

# This rule handles conditions as expressions.
def p_Expr_condition(p):
    'Expr : Condition'
    p[0] = p[1]

# This rule processes a variable as an expression.
def p_Expr_Variable(p):
    'Expr : Variable'
    p[0] = p[1]

# This rule processes numeric constants as expressions.
def p_expression_number(p):
    "Expr : NUM"
    p[0] = f"PUSHI {p[1]}\n"

'''
def p_opBasicSUM(p):
    'Expr : Expr "+" Expr'
    p[0] = p[1] + p[3] + 'ADD\n'
'''

# This rule processes basic operations like addition, subtraction, multiplication, division, and modulus.

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
        p[0] = p[1] + p[3] + "EQUAL \n"
    elif (p[2] == "!="):
          p[0] = p[1] + p[3] + "EQUAL\nNOT \n"
    elif (p[1] == '!'):
        p[0] = p[2] + "NOT \n"
    elif (p[2] == '>'):
        p[0] = p[1] + p[3] + "SUP \n"
    elif (p[2] == ">="):
        p[0] = p[1] + p[3] + "SUPEQ \n"
    elif (p[2] == '<'):
        p[0] = p[1] + p[3] + "INF \n"
    elif (p[2] == "<="):
        p[0] = p[1] + p[3] + "INFEQ \n"
    elif (p[2] == "&&"):
        p[0] = p[1] + p[3] + 'ADD\nPUSHI 2\nEQUAL\n'
    elif (p[2] == "||"):
        p[0] = p[1] + p[3] + "ADD\nPUSHI 1\nSUPEQ\n"
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
    "Variable : NAME '[' Expr ']'"
    if p[1] in p.parser.trackmap:
        varInfo = p.parser.trackmap.get(p[1])
        if len(varInfo) == 2:
            p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + 'LOADN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_VarMatrix(p):
    "Variable : NAME '[' Expr ']' '[' Expr ']'"
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
    input_file = sys.argv[1]
    # Generate output filename by prepending "res" to input filename
    output_file = "Assembly_" + os.path.basename(input_file)
    
    with open(input_file, 'r') as file:
        assembly = parser.parse(file.read())
        if assembly:
            with open(output_file, 'w') as output:
                output.write(assembly)
                print(f"{input_file} compiled successfully!\nCheck the output in {output_file}.")
        else:
            print("Empty!")
else:
    # Interactive mode
    line = input(">")
    while line != "\n":
        print(parser.parse(line))
        line = input(">")


#___________________________________________________________________________________________________________#
'''
Example usage:
-------------------------------------------------
Content of "test_input.txt":
    var a,b;
    a = 5;
    b = a * 10;
    if( a > 40 ) then {
       b = b + 1;
    }
    print a;
    print b;
-------------------------------------------------
Invocation:
    python YaccTP.py test_input.txt output_file.txt
Check output_file.txt for generated assembly code.
'''


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


'''

DEBUGGING:

Acho que tem bug na forma como definimos as 'Expr', temos de confirmar o que uma 'Expr'
pode ser, i.e., ver se uma Expr pode ser uma variável qql, por exemplo um i (iteração).


PARA VER, TALVEZ:

Alterar o IdLabels para dividir entre IfLabel e CycleLabel

'''