from Lexer.Lexer import Lexer
from Lexer.SymbolTable import SymbolTable
from Parser.CFG.ContextFreeGrammar import ContextFreGrammar as Cfg
from Parser.RecursiveDescentParser import RecursiveDescentParser

if __name__ == "__main__":
    symbol_table = SymbolTable(10)
    lexer = Lexer("token.in", symbol_table)
    #lexer = Lexer("simpleToken.in", symbol_table)
    #lexer = Lexer("mediumToken.in", symbol_table)

    lexer.tokenize("ptest.txt")
    #lexer.tokenize("simpleProgram.txt")
    #lexer.tokenize("mediumProgram.txt")
    print(lexer.pif)
    symbol_table.display()

    grammar1 = Cfg('grammar')
    """
    print(grammar1)
    print("Nonterminals:", grammar1.get_nonterminals())
    print("Terminals:", grammar1.get_terminals())
    print("Productions for A:", grammar1.get_productions_for('A'))
    print("Is valid CFG?", grammar1.is_valid_cfg())
    print('\n')
    """
    grammar2 = Cfg('g1')
    """
    print(grammar)
    print("Nonterminals:", grammar.get_nonterminals())
    print("Terminals:", grammar.get_terminals())
    print("Productions for A:", grammar.get_productions_for('A'))
    print("Is valid CFG?", grammar.is_valid_cfg())
    """
    #print(grammar2)

    #simpleGrammar = Cfg('simpleGrammar.txt')
    #mediumGrammar = Cfg('mediumGrammar.txt')

    # Initialize and run the parser
    parser = RecursiveDescentParser(grammar2)
    #parser = RecursiveDescentParser(simpleGrammar)
    #parser = RecursiveDescentParser(mediumGrammar)
    result = parser.parse(lexer.pif)
    # Output the result
    print(f"Result: {result}")
