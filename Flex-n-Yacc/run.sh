if [ $# -lt 2 ]; then
  echo "usage: ./run.sh <bison-file-with-no-suffix> <flex-file-with-no-suffix>";
else
  bison -d "$1".y
  flex "$2".lxi
  gcc lex.yy.c "$1".tab.c
fi;
read -r -p "press any key to continue"
