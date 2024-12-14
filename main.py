from Lexer.Lexer import Lexer
from Lexer.SymbolTable import SymbolTable
from Parser.CFG.ContextFreeGrammar import ContextFreGrammar as Cfg
from Parser.RecursiveDescentParser import RecursiveDescentParser

if __name__ == "__main__":
    symbol_table = SymbolTable(10)
    lexer = Lexer("token.in", symbol_table)

    lexer.tokenize("p2.txt")
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

    input_sequence = ["a", "c", "b"]  # for grammar 1

    input_sequence2 = [  # for grammar g1
        "function", "identifier", "(", "int", "a", ",", "string", "b", ",", "array", "identifier", ")",
        "a", "=", "10", ";",
        "if", "a", ">", "b",
        "cmpdstmt", "else",
        "cmpdstmt", "endif",
        "for", "(", "a", "=", "1", ";", "a", "<", "10", ";", "a", "=", "a", "+", "1", ")",
        "cmpdstmt", "endfor",
        "while", "a", ">", "5",
        "cmpdstmt", "endwhile",
        "return", "result", ";",
        "endfunction"
    ]

    # Initialize and run the parser
    parser = RecursiveDescentParser(grammar2, input_sequence2)
    result = parser.parse()
    # Output the result
    print(f"Result: {result}")
