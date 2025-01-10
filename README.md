# PLC-Project

O QUE FUNCIONA:

- Declaração e atribuição
- While-Do
- Repeat-Until
- If-Then-Otherwise
- Print
- Matrizes
- Arrays
- Read (Input) do stdin
- Write (Print) no stdout

O QUE NÃO FUNCIONA:
- ?

O QUE FALTA:
- Alterar tudo para conter ';' ** IMPORTANTE ** 
- Retificar a gramática
- Fazer relatório
- Resolver warning do print

DEBUGGING:

Função responsável pelo PRINT gera os Warnings:

Generating LALR tables
WARNING: 183 shift/reduce conflicts
WARNING: 7 reduce/reduce conflicts
WARNING: reduce/reduce conflict in state 28 resolved using rule (Variable -> NAME)
WARNING: rejected rule (Print -> PRINT NAME) in state 28
WARNING: Rule (Print -> PRINT NAME) is never reduced

PARA VER, TALVEZ:

Alterar o IdLabels para dividir entre IfLabel e CycleLabel.