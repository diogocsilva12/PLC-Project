# PLC-Project

O QUE FUNCIONA:

- Declaração e atribuição
- While-Do
- Repeat-Until
- If-Then-Otherwise
- Print
- Matrizes
- Arrays

O QUE NÃO FUNCIONA:
- Fazer READ do stdin e WRITE no stdout


DEBUGGING:

Função responsável pelo PRINT gera os Warnings:

Generating LALR tables
WARNING: 183 shift/reduce conflicts
WARNING: 7 reduce/reduce conflicts
WARNING: reduce/reduce conflict in state 28 resolved using rule (Variable -> NAME)
WARNING: Rule (Print -> PRINT NAME) is never reduced


PARA VER, TALVEZ:

Alterar o IdLabels para dividir entre IfLabel e CycleLabel.