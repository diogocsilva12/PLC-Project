from myLex import tokens
import ply.yacc as yacc
import sys 
#___________________________________________________________________________________________________________#

#### Program Structure ####

def p_Program(p):
    "Program : Header Body"
    p[0] = p[1] + "START\n" + p[2] + "STOP\n"

#___________________________________________________________________________________________________________#

#### Header Structure ####

def p_WOHeader(p):
	"Program : Body"
	p[0] = "START\n" + p[1] + "STOP\n"

def p_MultHeader(p):
	"Header: Decl Decls"
	p[0] = p[1] + p[2]

def p_SingleHeader(p):
	"Header: Decl"
	p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declarations ####

def p_MultDecl(p):
	"Decls: Decl Decls"
	p[0] = p[1] + p[2]

def p_SingleDecl(p):
	"Decls: Decl"
	p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Declaration [Int - Array - Matrix] ####

def p_IntDecl(p):
	"Decl : Var Int Name"
	if p[3] not in p.parser.trackmap:
		p.parser.trackmap.update({p[3]: p.parser.memPointer})
		p[0] = f"PUSHI 0\n"
		p.parser.memPointer += 1
	else:
		print(f"Variable {p[3]} already declared")
		raise Exception(f"Line{p.lineno(2)}, {p[3]} is already declared.") # acho que isto faz 2 em 1


def p_ArrayDecl(p):
	"Decl : Var Name '[' Num ']'"
	if p[2] not in p.parser.trackmap:
		p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]))})
		p[0] = f"PUSHN {p[4]}\n"
		p.parser.memPointer += int({p[4]})
	else:
		raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")


def p_MatrixDecl(p):
    "Decl : Var Name '[' NUM ']' '[' NUM ']'"
    if p[2] not in p.parser.trackmap:
        p.parser.trackmap.update({p[2]: (p.parser.memPointer, int(p[4]), int(p[7]))})
        memSpace = int(p[3]) * int(p[7])
        p[0] = f"PUSHN {str(memSpace)}\n" # Porquê str e não int? 
        p.parser.memPointer += memSpace
    else:
    	raise Exception(f"Line{p.lineno(2)}, {p[2]} is already declared.")

#___________________________________________________________________________________________________________#

#### Body Structure ####

def p_MultBody(p):
    "Body : Code Codes"
    p[0] = p[1] + p[2]

def p_SingleBody(p):
	"Body : Code"
	p[0] = p[1]

def p_Codes(p):
	"""Codes: Conditions
			| WhileDo
			| RepeatUntil
			| Assigning
	"""
	p[0] = p[1]

#___________________________________________________________________________________________________________#

#### Cycles and Conditions ####

def p_CondIfThen(p):
	"IfCond : if '(' cond ')' then code"
	p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"l{p.parser.idLabel}: NOP\n" # JZ - Jump Zero: Salta para o l{label} se a condição tiver valor 0 (false)
	p.parser.idLabel += 1															 # NOP - No Operation (não percebi porque isto é preciso)

def p_CondIfThenOtherwise(p):
	"IfOtherwiseCond : if '(' cond ')' then code otherwise code"
	p[0] = p[3] + f"JZ l{p.parser.idLabel}\n" + p[6] + f"JUMP l{p.parser.idLabel}f\nl{p.parser.idLabel}: NOP\n" + p[8] + f"l{p.parser.idLabel}f: NOP\n"
	p.parser.idLabel += 1

def p_WhileDo(p):
	"WhileDo : while '(' cond ')' do code"
	p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[3] + f"JZ l{p.parser.idLabel}f\n" + p[6] + f"JUMP l{p.parser.labels}c\nl{p.parser.labels}f: NOP\n"
	p.parser.idLabel += 1

def p_RepeatUntil(p):
	"RepeatUntil : repeat '{' code '}' until '(' Cond ')'"
	p[0] = f"l{p.parser.idLabel}c: NOP\n" + p[7] + f"JZ l{p.parser.idLabel}f\n" + p[3] + f"JUMP l{p.parser.labels}c\nl{p.parser.labels}f: NOP\n"
	p.parser.idLabel += 1


#___________________________________________________________________________________________________________#

#### Parser Initializer ####
parser = yacc.yacc()
parser.trackmap = dict()
parser.idLabel = 0
parser.memPointer = 0