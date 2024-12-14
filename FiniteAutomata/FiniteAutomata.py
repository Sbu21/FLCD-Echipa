import re

class FiniteAutomaton:
    def __init__(self, filename):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.initial_state = None
        self.final_states = set()
        self.load_fa(filename)

    def load_fa(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            section = None

            for line in lines:
                line = line.strip()
                if line == "":
                    continue

                if line.startswith("#"):
                    section = line
                elif section == "#STATES":
                    self.states.update(line.split())
                elif section == "#ALPHABET":
                    self.alphabet.update(line.split())
                elif section == "#TRANSITIONS":
                    parts = line.split()
                    self.add_transition(parts[0], parts[1], parts[2])
                elif section == "#INITIAL_STATE":
                    self.initial_state = line
                elif section == "#FINAL_STATES":
                    self.final_states.update(line.split())

    def add_transition(self, start_state, symbol, end_state):
        if start_state not in self.transitions:
            self.transitions[start_state] = {}
        if symbol in self.transitions[start_state]:
            print(f"Warning: Duplicate transition detected for {start_state} with symbol {symbol}.")
        self.transitions[start_state][symbol] = end_state

    def display(self):
        print("\nFinite Automaton:")
        print("States:", self.states)
        print("Alphabet:", self.alphabet)
        print("Transitions:")
        for state, transitions in self.transitions.items():
            for symbol, next_state in transitions.items():
                print(f"  {state} --({symbol})--> {next_state}")
        print("Initial State:", self.initial_state)
        print("Final States:", self.final_states)

    def is_dfa(self):
        for state, transitions in self.transitions.items():
            symbols_seen = set()
            for symbol in transitions:
                if symbol in symbols_seen:
                    return False
                symbols_seen.add(symbol)
        return True

    def validate_sequence(self, sequence):
        if not self.is_dfa():
            print("The FA is not a DFA. Sequence validation cannot be performed.")
            return False

        current_state = self.initial_state
        for symbol in sequence:
            if symbol not in self.alphabet:
                print(f"Invalid symbol: {symbol}")
                return False
            if symbol not in self.transitions.get(current_state, {}):
                print(f"No transition for symbol {symbol} from state {current_state}")
                return False
            current_state = self.transitions[current_state][symbol]

        return current_state in self.final_states


def menu(finite_automata):
    while True:
        print("\nMenu:")
        print("1. Display FA elements")
        print("2. Validate a sequence")
        print("3. Detect tokens from source code")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            finite_automata.display()
        elif choice == "2":
            sequence = input("Enter the sequence: ")
            if finite_automata.validate_sequence(sequence):
                print("Sequence accepted.")
            else:
                print("Sequence not accepted.")
        elif choice == "3":
            source_code = input("Enter source code: ")
            detect_tokens(source_code, finite_automata)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def detect_tokens(source_code, finite_automata):
    tokens = source_code.split()
    for token in tokens:
        if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token):  # Identifier pattern
            if finite_automata.validate_sequence(token):
                print(f"Token <IDENTIFIER>: {token}")
            else:
                print(f"Invalid identifier: {token}")
        elif re.fullmatch(r'\d+', token):
            if finite_automata.validate_sequence(token):
                print(f"Token <INTEGER CONSTANT>: {token}")
            else:
                print(f"Invalid integer constant: {token}")


if __name__ == "__main__":
    fa = FiniteAutomaton("FA.in")
    menu(fa)
