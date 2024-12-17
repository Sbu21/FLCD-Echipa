import re


class Lexer:
    def __init__(self, token_file, symbol_table):
        self.tokens = self.load_tokens(token_file)
        self.symbol_table = symbol_table
        self.pif = []  # This will store tokens, "identifier", or "number"

    def load_tokens(self, token_file):
        tokens = {}
        with open(token_file, "r") as file:
            for line in file.readlines():
                token = line.strip()
                tokens[token] = token  # Map token to itself for easy lookup
        return tokens

    def tokenize(self, source_file):
        with open(source_file, "r") as file:
            source_code = file.readlines()

        line_number = 0
        errors = []
        for line in source_code:
            line_number += 1
            index = 0
            while index < len(line):
                if line[index].isspace():
                    index += 1
                    continue

                token, index = self.extract_token(line, index)
                if token in self.tokens:  # Reserved keywords or operators
                    self.pif.append(token)
                elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):  # Identifier
                    self.symbol_table.insert(token)
                    self.pif.append("identifier")
                elif re.match(r'^\d+$', token):  # Constant
                    self.symbol_table.insert(token)
                    self.pif.append("number")
                else:  # Unknown token
                    errors.append((line_number, token))

        if errors:
            for line, token in errors:
                print(f"Lexical error at line {line}: '{token}'")
        else:
            print("Lexically correct")

    def extract_token(self, line, index):
        operators = {'+', '-', '*', '/', '%', '=', '==', '<', '>', '->', '+=', '<=', '>='}
        token = ""

        # Handle alphanumeric tokens (IDENTIFIERS, CONSTANTS)
        if line[index].isalnum() or line[index] == '_':
            while index < len(line) and (line[index].isalnum() or line[index] == '_'):
                token += line[index]
                index += 1
        # Handle operators
        elif line[index] in '+-*/%<=>':
            while index < len(line) and token + line[index] in operators:
                token += line[index]
                index += 1
        # Handle single-character tokens (e.g., (), [], ;, ,)
        elif line[index] in '()[];,':
            token = line[index]
            index += 1
        else:  # Unrecognized character
            token = line[index]
            index += 1

        return token, index