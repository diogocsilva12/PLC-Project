Program : Header Code
       | Code
Header : Header Decl
       | Decl
Decl : VAR NameList ';'
     | VAR NAME '[' NUM ']' ';'
     | VAR NAME '[' Expr ']' '[' Expr ']' ';'
NameList : NAME
         | NameList ',' NAME
Code : Code Codes
     | Codes
Codes : Conditions
      | WhileDo
      | RepeatUntil
      | Assign
      | Print
Conditions : IF '(' Condition ')' THEN '{' Code '}'
           | IF '(' Condition ')' THEN '{' Code '}' OTHERWISE '{' Code '}'
WhileDo : WHILE '(' Condition ')' DO '{' Code '}'
RepeatUntil : REPEAT '{' Code '}' UNTIL '(' Condition ')' ';'
Assign : NAME '=' Expr ';'
       | NAME '[' Expr ']' '=' Expr ';'
       | NAME '[' Expr ']' '[' Expr ']' '=' Expr ';'
       | NAME '[' Expr ']' '=' INPUT ';'
       | NAME '[' Expr ']' '[' Expr ']' '=' INPUT ';'
       | NAME '=' INPUT ';'                   
Expr : Condition
     | Variable
     | NUM
     | Expr '+' Expr
     | Expr '-' Expr
     | Expr '*' Expr
     | Expr '/' Expr
     | Expr '%' Expr
     | '(' Expr ')'
Condition : Expr EQ Expr
          | Expr NEQ Expr
          | '!' Expr
          | Expr '>' Expr
          | Expr MOREEQ Expr
          | Expr '<' Expr
          | Expr LESSEQ Expr
          | Expr AND Expr
          | Expr OR Expr
          | '(' Condition ')'
Variable : NAME
         | NAME '[' Expr ']'       
         | NAME '[' Expr ']' '[' Expr ']'   
Print : PRINT NAME ';'
      | PRINT STRING ';'