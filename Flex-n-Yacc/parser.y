%%
program: function
        ;

function: FUNCTION IDENTIFIER '(' param_list ')' cmpdstmt ENDFUNCTION
        ;

param_list: param
          | param ',' param_list
          ;

param: INT IDENTIFIER
     | STRING IDENTIFIER
     | ARRAY IDENTIFIER
     ;

cmpdstmt: stmt_list
        ;

stmt_list: stmt
          | stmt stmt_list
          ;

stmt: assignstmt
    | ifstmt
    | forstmt
    | whilestmt
    | returnstmt
    ;

assignstmt: IDENTIFIER '=' expression ';'
          ;

ifstmt: IF condition cmpdstmt ENDIF
      | IF condition cmpdstmt ELSE cmpdstmt ENDIF
      ;

forstmt: FOR '(' assignstmt condition ';' assignstmt ')' cmpdstmt ENDFOR
       ;

whilestmt: WHILE condition cmpdstmt ENDWHILE
         ;

returnstmt: RESULT ARROW expression ';'
          ;

expression: expression '+' term
          | expression '-' term
          | term
          ;

term: term '*' factor
    | term '/' factor
    | term '%' factor
    | factor
    ;

factor: '(' expression ')'
      | IDENTIFIER
      ;

condition: expression RELATION expression
         ;

RELATION: '<'
        | LE
        | EQ
        | '>'
        | GE
        ;
%%
