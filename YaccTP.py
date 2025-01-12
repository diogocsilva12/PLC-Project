from LexTP import tokens
import ply.yacc as yacc
import sys
import os
#___________________________________________________________________________________________________________#

#### Estrutura Programa ####
'''
Esta secção define a estrutura geral do programa que está a ser analisado pelo parser. Especifica 
se o programa consiste num cabeçalho opcional seguido pelo código principal. Adiciona as etiquetas "START" e
"STOP" no início e fim do código gerado, respetivamente, para demarcar claramente o bloco de execução.
'''

# Nome da função: p_Program
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Define a estrutura geral do programa, que consiste num cabeçalho opcional e o código principal.
#   Adiciona as etiquetas 'START' e 'STOP' no início e fim do código gerado.
# Exemplos de linguagem:
#   START 
#   var a, b
#   a = 5
#   STOP

def p_Program(p):
    "Program : Header Code"
    p[0] = p[1] + "START\n" + p[2] + "STOP\n"

#___________________________________________________________________________________________________________#
#### Estrutura do Header ####
'''Esta secção lida com a parte do cabeçalho do programa, que contem as declarações de variáveis.
Pode conter multiplas declarações, separadas por vírgulas, ou uma única declaração. O cabeçalho é
responsavel por alocar espaço na memória para as variáveis declaradas e inicializá-las.'''


# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata o caso onde o programa não possui um cabeçalho, e processa apenas o código.
#   Adiciona as etiquetas 'START' e 'STOP' no inicio e fim do código.
# Exemplos de linguagem:
#   a = 5
#   b = a * 10

def p_WOHeader(p): #WO = Without
    "Program : Code"
    p[0] = "START\n" + p[1] + "STOP\n" 
    

# Nome da função: p_MultHeader
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com múltiplas declarações no cabeçalho, adicionando cada declaração à estrutura do cabeçalho.
# Exemplos de linguagem:
#   var a
#   var b

def p_MultHeader(p):
    "Header : Header Decl"
    p[0] = p[1] + p[2] # Adiciona as novas declarações ao cabeçalho.
    

# Nome da função: p_SingleHeader
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com a declaração única no cabeçalho.
# Exemplos de linguagem:
#   var a

def p_SingleHeader(p):
    "Header : Decl"
    p[0] = p[1]

#___________________________________________________________________________________________________________#
#### Declaration [Int - Array - Matrix] ####
'''
Esta secção lida com a declaração de variáveis, que pode ser de três tipos: inteiro, array ou matriz.
Para cada tipo, existem regras específicas que gerenciam a alocação de memoria e garantem que as variaveis nao 
sejam re-declaradas.
'''

# Nome da função: p_IntDecl
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa declarações de variáveis inteiras, inicializando-as a zero e atualizando o apontador de memória.
#   Lança uma exceção se a variável já estiver declarada.
# Exemplos de linguagem:
#   var a, b, c
#   var x

def p_IntDecl(p):
    "Decl : VAR NameList ';'" #Namelist permite declarar variáveis ao mesmo tempo. O que faz é adicionar à lista de variáveis.
    for name in p[2]:
        if name not in p.parser.trackmap:
            p.parser.trackmap.update({name: p.parser.memPointer}) # Rastreia a variável na memória.
            p[0] = (p[0] or "") + "PUSHI 0\n"# Inicializa a variável a zero.
            p.parser.memPointer += 1  # Move o apontador de memória para o próximo slot.
        else:
            raise Exception(f"Variable {name} already declared.") # Trata erros de re-declaração.


# Nome da função: p_NameList
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Permite declarar uma ou múltiplas variáveis separadas por vírgulas.
# Exemplos de linguagem:
#   a
#   a, b, c

def p_NameList(p):
    """NameList : NAME
                | NameList ',' NAME"""
    if len(p) == 2:  # Apenas um nome
        p[0] = [p[1]]
    else:  # Lista com vírgulas
        p[0] = p[1] + [p[3]]


# Nome da função: p_ArrayDecl
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa declarações de arrays, alocando espaço na memória e atualiza o apontador de memória.
#   Lança uma exceção se o array já estiver declarado.
# Exemplos de linguagem:
#   var a[3]

def p_ArrayDecl(p):
    "Decl : VAR NAME '[' NUM ']' ';'" #example: Var a[3]  # Array tem de permitir Expr para ver índices (letras) nos ciclos
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]))}) # Rastreia o array na memória.
        memSpace = int(p[4]) # Calcula o espaço necessário para o array.
        p[0] = f"PUSHN {memSpace}\n"# Aloca espaço para o array na memória.
        p.parser.memPointer += int(p[4])# Atualiza o apontador de memória pelo tamanho do array.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")# Trata erros de re-declaração.


# Nome da função: p_MatrixDecl
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa declarações de matrizes, aloca espaço na memória e atualiza o apontador de memória.
#   Lança uma exceção se a matriz já estiver declarada.
# Exemplos de linguagem:
#   var a[3][4]

def p_MatrixDecl(p):
    "Decl : VAR NAME '[' NUM ']' '[' NUM ']' ';'" #example: Var a[3][4]   # Matriz tem de permitir Expr para ver índices (letras) nos ciclos 
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]), int(p[7]))})
        memSpace = int(p[4]) * int(p[7]) # Calcula o espaço total necessário para a matriz.
        p[0] = f"PUSHN {memSpace}\n"  # Aloca memória para a matriz.
        p.parser.memPointer += memSpace   # Atualiza o apontador de memória.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.") # Prevent redeclaration.

#___________________________________________________________________________________________________________#
#### Code Structure ####
'''
Definie a estrutura do código principal, que pode conter múltiplos blocos de código, como condições, loops, atribuições e impressões.
Permite a concatenação de múltiplos blocos de código, facilitando a construção de sequencias de instruções.
Esta secção assegura que o parser possa interpretar corretamente varias instruções em sequencias.
'''

# Nome da função: p_MultCode
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com a concatenação de múltiplos blocos de código.
# Exemplos de linguagem:
#   a = 5
#   b = a + 2

def p_MultCode(p):
    "Code : Code Codes"
    p[0] = p[1] + p[2]# Combina seções de código.


# Nome da função: p_SingleCode
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com um único bloco de código.
# Exemplos de linguagem:
#   a = 5

def p_SingleCode(p):
    "Code : Codes"
    p[0] = p[1]


# Nome da função: p_Codes
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Define as diversas estruturas de código permitidas, como condições, loops, atribuições e prints.
# Exemplos de linguagem:
#   if (a > b) then { ... }
#   while (a < b) do { ... }

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
'''
Gerencia as estruturas de controle de fluxo, como loops e condições. Cada estrutura é tratada individualmente. 
Gera as instruções de salto necessárias para implementar a lógica condicional e os ciclos de repetição,
permitindo que o programa execute diferentes blocos de código com base em certas condições.
'''

# Nome da função: p_CondIfThen
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata a estrutura de 'if-then', gera as instruções de salto para a lógica condicional.
# Exemplos de linguagem:
#   if (a > b) then { ... }

def p_CondIfThen(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[7] + f"l{p.parser.idLabel}: NOP\n" # JZ - Jump Zero: Salta para o l{label} se a condição tiver valor 0 (false)
    p.parser.idLabel += 1                                                            # NOP - No Operation (não percebi porque isto é preciso)


# Nome da função: p_CondIfThenOtherwise
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata a estrutura de 'if-then-else', gera as instruções de salto para a lógica condicional.
# Exemplos de linguagem:
#   if (a > b) then { ... } otherwise { ... }

def p_CondIfThenOtherwise(p):
    "Conditions : IF '(' Condition ')' THEN '{' Code '}' OTHERWISE '{' Code '}'"
    p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[7] + f"JUMP l{p.parser.idLabel}f\nl{p.parser.idLabel}: NOP\n" + p[11] + f"l{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1


# Nome da função: p_WhileDo
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata a estrutura de 'while-do', gera as instruções de loop com condição de saída.
# Exemplos de linguagem:
#   while (a < b) do { ... }

def p_WhileDo(p):
    "WhileDo : WHILE '(' Condition ')' DO '{' Code '}'"
    p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[3] + f"JZ l{p.parser.idLabel}f\n" + p[7] + f"JUMP l{p.parser.idLabel}c\nl{p.parser.idLabel}f: NOP\n"
    p.parser.idLabel += 1


# Nome da função: p_RepeatUntil
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata a estrutura de 'repeat-until', gera as instruções de loop com condição de término após a execução.
# Exemplos de linguagem:
#   repeat { ... } until (a == b)

def p_RepeatUntil(p):
    "RepeatUntil : REPEAT '{' Code '}' UNTIL '(' Condition ')' ';' " 
    p[0] = (
        f"l{p.parser.idLabel}c: NOP\n" + p[3]+ p[7]+ f"JZ l{p.parser.idLabel}c\n"+ f"JUMP l{p.parser.idLabel}f\n"+ f"l{p.parser.idLabel}f: NOP\n"
    )
    p.parser.idLabel += 1
     
#___________________________________________________________________________________________________________#

#### Assigning ####
'''
Lida com as atribuições de valores a variáveis, arrays e matrizes. Verifica se as variaveis foram previamente
declaradas e se os tipos são compativeis antes de armazenar os valores correspondentes na memoria. Garante
que as operações de atribuição atualizem corretamente o estado do programa.
'''

# Nome da função: p_ExpressionAssign
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com atribuições de valores a variáveis, armazenando o resultado da expressão na memória.
#   Verifica se a variável foi previamente declarada e se é do tipo correto.
# Exemplos de linguagem:
#   a = 5
#   b = a + 2

def p_ExpressionAssign(p):
    "Assign : NAME '=' Expr ';'"  #exemplo : b = 2 
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = p[3] + f"STOREG {var}\n" # Armazena o resultado da expressão na variável.
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an integer.")  # Verifica se a variável é um inteiro.
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")


# Nome da função: p_ArrayAssign
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com atribuições a posições específicas de um array, calculando o endereço correto e armazenando o valor.
#   Verifica se o array foi previamente declarado.
# Exemplos de linguagem:
#   a[2] = 10

def p_ArrayAssign(p):
     "Assign : NAME '[' Expr ']' '=' Expr ';'"   # Array tem de permitir Expr para ver índices (letras) nos ciclos
     if p[1] in p.parser.trackmap:
          varInfo = p.parser.trackmap.get(p[1])
          if len(varInfo) == 2:
                p[0] = f'PUSHGP\nPUSHI {varInfo[0]}\nPADD\n' + p[3] + p[6] + 'STOREN\n'  # Permite índices expressivos nos ciclos.
          else:
               raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
     else:
          raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")


# Nome da função: p_MatrixAssign
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Lida com atribuições a posições específicas de uma matriz, calculando o endereço correto e armazenando o valor.
#   Verifica se a matriz foi previamente declarada.
# Exemplos de linguagem:
#   a[2][3] = 15

def p_MatrixAssign(p): # Nome[Expr][Expr] = Expr
     "Assign : NAME '[' Expr ']' '[' Expr ']' '=' Expr ';'"     # Matriz tem de permitir Expr para ver índices (letras) nos ciclos
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
'''
Gerencia a avalição de expressões aritmeticas e logicas. Permite operações basicas como adição, subtração, multiplicação, divisão e módulo,
bem como condições logicas como igualdade, desigualdade, maior que, etc. Gera as intruções correspondentes para cada operação.
'''

# Nome da função: p_Expr_condition
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Permite que uma condição seja tratada como uma expressão.
# Exemplos de linguagem:
#   a > b

def p_Expr_condition(p):
    'Expr : Condition'
    p[0] = p[1]


# Nome da função: p_Expr_Variable
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Permite que uma variável seja tratada como uma expressão.
# Exemplos de linguagem:
#   a
#   b

def p_Expr_Variable(p):
    'Expr : Variable'
    p[0] = p[1]


# Nome da função: p_expression_number
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa constantes numéricas como expressões, gerando a instrução para empurrar o valor na pilha.
# Exemplos de linguagem:
#   5
#   10

def p_expression_number(p):
    "Expr : NUM"
    p[0] = f"PUSHI {p[1]}\n"


# Nome da função: p_Expr_OP
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa operações básicas (adição, subtração, multiplicação, divisão, módulo) como expressões.
#   Gera as instruções correspondentes para cada operação.
# Exemplos de linguagem:
#   a + b
#   c - d
#   e * f
#   g / h
#   i % j

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


# Nome da função: p_condLog
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Processa condições lógicas (igualdade, desigualdade, maior que, etc.) gerando as instruções correspondentes.
#   Inclui operações lógicas como AND e OR.
# Exemplos de linguagem:
#   a == b
#   c != d
#   !e
#   f > g
#   h >= i
#   j < k
#   l <= m
#   n && o
#   p || q

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


# Nome da função: p_Expr_base
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Permite o uso de parênteses para agrupar expressões.
# Exemplos de linguagem:
#   (a + b)

def p_Expr_base(p):
    "Expr : '(' Expr ')'"
    p[0] = p[2]


# Nome da função: p_condition_base
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Permite o uso de parênteses para agrupar condições.
# Exemplos de linguagem:
#   (a > b)
def p_condition_base(p):
    "Condition : '(' Condition ')'"
    p[0] = p[2]

#___________________________________________________________________________________________________________#

#### Acessing Vars (Num - Array - Matrix ) ####

'''
Trata do acesso a variáveis. Calcula os endereços corretos na memória para aceder aos valores armazenados e gera as instruções necessárias para
carregar esses valores para a pilha de execução.
'''


# Nome da função: p_VarNum
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Acede a uma variável inteira, gerando a instrução para empurrar seu valor na pilha.
#   Verifica se a variável foi previamente declarada e é do tipo correto.
# Exemplos de linguagem:
#   a
#   b
def p_VarNum(p):
    "Variable : NAME"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = f"PUSHG {var}\n"
        else:
            raise TypeError(f"Line {p.lineno(1)}, {p[1]} is not an integer.")
    else:
        raise Exception(f"Line {p.lineno(1)}, {p[1]} is not declared.")


# Nome da função: p_VarArray
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Acede a um elemento específico de um array, calculando seu endereço e gera a instrução para carregar o valor.
#   Verifica se o array foi previamente declarado.
# Exemplos de linguagem:
#   a[2]
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


# Nome da função: p_VarMatrix
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Acessa um elemento específico de uma matriz, calculando seu endereço e gera a instrução para carregar o valor.
#   Verifica se a matriz foi previamente declarada.
# Exemplos de linguagem:
#   a[2][3]
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

# Nome da função: p_error
# Parâmetros de entrada:
#   - p: objeto que contém informações sobre o erro
# Explicação da função:
#   Trata erros de sintaxe e exibe mensagens informativas sobre o token que causou o erro e sua localização.
# Exemplos de linguagem:
#   Sintaxe incorreta: a = 
def p_error(p):
    print(f"Syntax error: token {p.value} on line {p.lineno}.")

#___________________________________________________________________________________________________________#

#### Input (Assignments) ####

def p_Input_Array(p):
    "Assign : NAME '[' Expr ']' '=' INPUT ';'"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if len(var) == 2:
            p[0] = f'PUSHGP\nPUSHI {var[0]}\nPADD\n' + p[3] + f'READ\nATOI\nSTOREN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an array.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_Input_Matrix(p):
    "Assign : NAME '[' Expr ']' '[' Expr ']' '=' INPUT ';'"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if len(var) == 3:
            p[0] = f'PUSHGP\nPUSHI {var[0]}\nPADD\n{p[3]}PUSHI {var[2]}\nMUL\n{p[6]}ADD\nREAD\nATOI\nSTOREN\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not a matrix.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

def p_Input_Var(p):
    "Assign : NAME '=' INPUT ';'"
    if p[1] in p.parser.trackmap:
        var = p.parser.trackmap.get(p[1])
        if type(var) == int:
            p[0] = f'READ\nATOI\nSTOREG {var}\n'
        else:
            raise TypeError(f"Line{p.lineno(2)}, {p[1]} is not an integer.")
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[1]} is not declared.")

#___________________________________________________________________________________________________________#

#### Print ####
'''
Gerencia as instruções de impressão, permitindo que os valores de variáveis, arrays e matrizes sejam exibidos. Para variáveis simples,
imprime o valor seguido de uma nova linha. Para arrays e matrizes, itera sobre os elementos e imprime de forma formatada.
'''

# Nome da função: p_Print
# Parâmetros de entrada:
#   - p: lista que contém os elementos da regra
# Explicação da função:
#   Trata a instrução de impressão, gera as instruções correspondentes para exibir o valor da expressão.
#   Adiciona uma nova linha após a impressão.
# Exemplos de linguagem:
#   print a
#   print b
def p_Print(p):
    "Print : PRINT NAME ';'"
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
            p[0] = f'PUSHG {var}\nWRITEI\nPUSHS "\\n"\nWRITES\n'
    else:
        raise Exception(f"Line{p.lineno(2)}, {p[2]} is not declared.")
    
def p_PrintString(p):
    "Print : PRINT STRING ';'"
    p[0] = f'PUSHS "{p[2]}"\nWRITES\n'

#___________________________________________________________________________________________________________#

#### Parser Initializer ####

# Nome da função: Initialização do Parser
# Parâmetros de entrada:
#   - Nenhum
# Explicação da função:
#   Inicializa o parser utilizando o PLY (Python Lex-Yacc), configura as estruturas de rastreamento e os contadores para os labels e memória.
# Exemplos de linguagem:
#   Nenhum
parser = yacc.yacc()
parser.trackmap = dict()
parser.idLabel = 0
parser.memPointer = 0


#___________________________________________________________________________________________________________#

#### Main ####
'''
Explicação: Define a função principal do programa que executa o parser.
Se forem fornecidos argumentos de linha de comando, lê o arquivo de entrada, processa o código e gera o arquivo de saída com o código assembly correspondente. 
Se nenhum arquivo for fornecido, entra em modo interativo, permitindo que o utilizador insira linhas de código e veja os resultados de imediato.
'''
# Nome da função: Main
# Parâmetros de entrada:
#   - sys.argv: lista de argumentos de linha de comando
# Explicação da função:
#   Executa o parser, lendo o arquivo de entrada e gerando o código assembly correspondente.
#   Suporta modo interativo se nenhum arquivo for fornecido.
# Exemplos de linguagem:
#   python YaccTP.py test_input.txt output_file.txt
if len(sys.argv) > 1:
    input_file = sys.argv[1]
    if not os.path.exists("Outputs"):
        os.makedirs("Outputs")
    output_file = os.path.join("Outputs", "Assembly_" + os.path.basename(input_file))
    
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


