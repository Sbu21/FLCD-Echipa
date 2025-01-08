bison -d %1.y
flex %2
gcc lex.yy.c %1.tab.c
