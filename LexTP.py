import ply.lex as lex


#___________________________________________________________________________________________________________#
#### Definição de Palavras Reservadas ####
'''
Esta secção define as palavras reservadas da linguagem que estão a ser analisadas pelo lexer.
As palavras reservadas são mapeadas para tipos de tokens específicos que serão utilizados pelo parser.
'''
reserved = {
    'print': 'PRINT',
    'input': 'INPUT',
    'while': 'WHILE',
    'do': 'DO',
    'repeat': 'REPEAT',
    'until': 'UNTIL',
    'if': 'IF',
    'then': 'THEN',
    'otherwise': 'OTHERWISE',
    'eq': 'EQ',
    'neq': 'NEQ',
    'moreeq': 'MOREEQ',
    'lesseq': 'LESSEQ',
    'and': 'AND',
    'or': 'OR',
}

#___________________________________________________________________________________________________________#
#### Definição de Tokens ####
'''
Define os diferentes tipos de tokens que o lexer irá reconhecer. Isto inclui identificadores, variáveis, números
e as palavras reservadas previamente definidas.
'''
# Tokens
tokens = [
    'NAME',
    'VAR',
    'NUM'
] + list(reserved.values())


#___________________________________________________________________________________________________________#
#### Definição de Literais ####
'''
Define os caracteres literais que são reconhecidos diretamente pelo lexer. Estes incluem símbolos como
dois pontos, vírgulas, iguais, chavetas, colchetes, parênteses, ponto e vírgula e operadores aritméticos e lógicos.
'''
literals = [':',',','=','{','}','|','"','','[',']','(',')',';','+','-','*','/','%','>','<','!']

#___________________________________________________________________________________________________________#
#### Regras de Expressões Regulares ####
'''
Esta secção define as expressões regulares para reconhecer operadores lógicos e comparativos.
Cada função representa uma regra que, quando correspondida, gera o token apropriado.
'''
t_EQ = r'\=\=' #igual
t_NEQ = r'\!\=' #diferente
t_MOREEQ = r'\>\=' #maior ou igual
t_LESSEQ  = r'\<\=' # menor ou igual
t_AND = r'\&\&' # e/and
t_OR = r'\|\|' # ou/or

#___________________________________________________________________________________________________________#
#### Regras de Tokens ####
'''
Define as regras para reconhecer palavras-chave, identificadores e números. Utiliza funções para tokens que exigem
processamento adicional, como conversão de tipos ou verificação de palavras reservadas.
'''
def t_VAR(t):
    r'var'
    return t

def t_NAME(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value, 'NAME')
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t


#___________________________________________________________________________________________________________#
#### Gestão de Linhas Novas ####
'''
Atualiza o número da linha do lexer cada vez que uma nova linha é encontrada.
'''
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#___________________________________________________________________________________________________________#
#### Gestão de Erros ####
'''
Esta função é chamada sempre que um caractere ilegal é encontrado pelo lexer. Imprime uma mensagem de erro e faz o
lexer passar caractere inválido para continuar a análise.
'''
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

#___________________________________________________________________________________________________________#
#### Ignorar Espaços em Branco ####
'''
Define os caracteres que o lexer deve ignorar. Neste caso, espaços, retornos de carro e tabulações são ignorados.
'''
t_ignore  = ' \r\t'


#___________________________________________________________________________________________________________#
#### Inicialização do Lexer ####
'''
Cria uma instância do lexer usando as regras e definições acima.
'''
lexer = lex.lex()