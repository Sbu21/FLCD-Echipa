%{
#include "parser.tab.h"
#include <stdlib.h>
#include <string.h>
%}

%%

FUNCTION         { return FUNCTION; }
IF               { return IF; }
ENDIF            { return ENDIF; }
ELSE             { return ELSE; }
FOR              { return FOR; }
ENDFOR           { return ENDFOR; }
WHILE            { return WHILE; }
ENDWHILE         { return ENDWHILE; }
RESULT           { return RESULT; }
INT              { return INT; }
STRING           { return STRING; }
ARRAY            { return ARRAY; }
AND              { return AND; }
OR               { return OR; }

"+"              { return '+'; }
"-"              { return '-'; }
"*"              { return '*'; }
"/"              { return '/'; }
"%"              { return '%'; }
"="              { return '='; }
"<"              { return '<'; }
"<="             { return LE; }
"=="             { return EQ; }
">"              { return '>'; }
">="             { return GE; }
"->"             { return ARROW; }

"("              { return '('; }
")"              { return ')'; }
"["              { return '['; }
"]"              { return ']'; }
";"              { return ';'; }
","              { return ','; }

[a-zA-Z][a-zA-Z0-9]* {
    return IDENTIFIER;
}

[+-]?[0-9]+ {
    return INT_CONSTANT;
}

\"[^\"]*\" {
    return STRING_CONSTANT;
}

\\[[+-]?[0-9]+(,[+-]?[0-9]+)*\\] {
    return ARRAY_CONSTANT;
}

[ \\t\\n]+       { }

. {
    printf("Unexpected character: %s\\n", yytext);
}

%%

int yywrap() {
    return 1;
}
