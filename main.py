from Lexer.Lexer import Lexer
from Lexer.SymbolTable import SymbolTable
from Parser.CFG.ContextFreeGrammar import ContextFreGrammar as Grammar
from Parser.RecursiveDescentParser import RecursiveDescentParser

if __name__ == "__main__":
    TOKEN_ID = 0
    PROGRAM_ID = 1
    GRAMMAR_ID = 2
    simple_config: tuple[str, str, str] = ("simpleToken.in", "simpleProgram.txt", "simpleGrammar.txt")
    medium_config: tuple[str, str, str] = ("mediumToken.in", "mediumProgram.txt", "mediumGrammar.txt")
    hard_config: tuple[str, str, str] = ("token.in", "ptest.txt", "g1")

    working_config = hard_config
    symbol_table = SymbolTable(10)
    lexer = Lexer(working_config[TOKEN_ID], symbol_table)

    lexer.tokenize(working_config[PROGRAM_ID])
    print(lexer.pif)
    symbol_table.display()

    grammar = Grammar(working_config[GRAMMAR_ID])
    print(grammar)

    parser = RecursiveDescentParser(grammar, lexer.pif)
