import ply.lex as lex

reserved = {
    'int': 'INT',
    'array': 'ARRAY',
    'matrix': 'MATRIX',
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
    'or': 'OR'
}


# Tokens
tokens = [
    'NAME',
    'VAR',
    'NUM'
] + list(reserved.values())

literals = [':',',','=','{','}','|','"','','[',']','(',')',';','+','-','*','/','%','>','<','!']

#Regras
t_EQ = r'\=\=' #igual
t_NEQ = r'\!\=' #diferente

t_MOREEQ = r'\>\=' #maior ou igual
t_LESSEQ  = r'\<\=' # menor ou igual

t_AND = r'\&\&' # e/and
t_OR = r'\|\|' # ou/or


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

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

t_ignore  = ' \r\t'

lexer = lex.lex()