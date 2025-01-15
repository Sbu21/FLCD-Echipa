    @echo off

if "%~2"=="" (
    echo usage: run.bat ^<bison-file-with-no-suffix^> ^<flex-file-with-no-suffix^>
    goto :eof
)

bison -d "%~1.y"
if errorlevel 1 goto :eof

flex "%~2.lxi"
if errorlevel 1 goto :eof

gcc lex.yy.c "%~1.tab.c"
if errorlevel 1 goto :eof

pause