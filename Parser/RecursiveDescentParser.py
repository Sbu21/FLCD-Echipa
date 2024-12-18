from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException


class RecursiveDescentParser:
    NORMAL: str = "normal"
    BACKTRACK: str = "backtrack"
    ERROR: str = "error"
    FINAL: str = "final"
    NO_PARENT: int = -1
    NO_SIBLING: int = -1

    def error(self) -> None:
        self.state = RecursiveDescentParser.ERROR

    def all_good(self) -> None:
        self.state = RecursiveDescentParser.NORMAL

    def insuccess(self) -> None:
        self.state = RecursiveDescentParser.BACKTRACK

    def end(self) -> None:
        self.state = RecursiveDescentParser.FINAL

    def __init__(self, grammar: ContextFreGrammar) -> None:
        self.grammar: ContextFreGrammar = grammar
        self.input_sequence: list | None = None
        self.state: str = RecursiveDescentParser.NORMAL
        self.index: int = 0
        self.working_stack: list[str | tuple[str, int]] = []
        self.input_stack = [grammar.start_symbol]
        self.parse_table: list[str] = []
        self.production_index_stack: list[int] = []
        self.tree: list[tuple[str, int, int]] = []
        if not self.grammar.get_productions():
            raise ParseException("Provided grammar does not contain any productions")

    def __str__(self) -> str:
        result = f'\nInput stack: {self.input_stack}\nWorking stack:{self.working_stack}\nTree:\n'
        for index, production in enumerate(self.tree):
            result += f"[{index}] {production}\n"
        return result

    def expand(self) -> None:
        print(f"EXPAND: {self}")
        if 0 == len(self.input_stack):
            self.error()
            print("Error: Attempted to expand an empty input stack")
            return

        current = self.input_stack.pop(0)
        if current not in self.grammar.get_nonterminals():
            self.error()
            print(f"Error: Attempted to expand a terminal ({current})")
            return
        productions = self.grammar.get_productions_for(current)
        if 0 == len(productions):
            self.error()
            print(f"Error: Nonterminal {current} has no productions")
            return
        first_production = productions[0]
        self.input_stack = list(first_production) + self.input_stack
        parent_index = len(self.tree) - 1
        sibling_index = RecursiveDescentParser.NO_SIBLING
        for symbol in first_production:
            self.tree.append((symbol, parent_index, sibling_index))
            sibling_index += 1

        self.working_stack.append((current, 1))

    def advance(self) -> None:
        """
        Perform the Advance action:
        - Match the terminal at the head of the input stack with the current input symbol.
        - Update the working stack, input stack, and current index.
        """
        print(f"ADVANCE: {self}")
        self.index += 1
        if len(self.input_stack) == 0:
            self.error()
            print("Tried advancing with an empty input stack")
            return
        self.working_stack.append(self.input_stack.pop(0))

    def momentary_insuccess(self) -> None:
        """
        Perform the Momentary Insuccess action:
        - If the terminal at the head of the input stack does not match the current input symbol,
        transition to the backtrack state.
        """
        print(f"MOMENTARY INSUCCESS: {self}")
        self.state = RecursiveDescentParser.BACKTRACK

    def back(self):
        """
        Perform the Back action:
        - If the head of the working stack is a terminal, move it back to the input stack
          and step back in the input sequence.
        """
        print(f"BACK: {self}")
        if 0 == len(self.working_stack):
            self.error()
            print("Error: Nowhere to backtrack")
            return

        terminal = self.working_stack.pop()
        while not isinstance(terminal, tuple):
            terminal = self.working_stack.pop()
            self.tree.pop()
            self.index -= 1

        self.input_stack.insert(0, terminal)
        self.tree.pop()

    def another_try(self) -> None:
        print(f"ANOTHER TRY: {self}")
        if 0 == len(self.working_stack):
            self.error()
            print("Error: Nowhere to backtrack")
            return

        last_terminal_maybe = self.working_stack.pop()
        while not isinstance(last_terminal_maybe, tuple):
            last_terminal_maybe = self.working_stack.pop()
            self.index -= 1

        if not (isinstance(last_terminal_maybe, tuple)
                and len(last_terminal_maybe) == 2
                and isinstance(last_terminal_maybe[0], str)
                and isinstance(last_terminal_maybe[1], int)):
            self.error()
            print(f"Error: Tried taking another choice for a terminal ({last_terminal_maybe})")
            return

        last_nonterminal, prod_index = last_terminal_maybe
        productions = self.grammar.get_productions_for(last_nonterminal)

        if prod_index >= len(productions) - 1:
            print(f"Exhausted all productions for {last_nonterminal}, backtracking further...")
            return self.another_try()  # Recursive call to try at a higher level
        else:
            next_prod = productions[prod_index + 1]
            self.input_stack = list(next_prod) + self.input_stack[len(productions[prod_index]):]

            parent_index = len(self.tree) - 1
            sibling_index = RecursiveDescentParser.NO_SIBLING
            for symbol in next_prod:
                self.tree.append((symbol, parent_index, sibling_index))
                sibling_index += 1

            self.working_stack.append((last_nonterminal, prod_index + 1))
            self.state = RecursiveDescentParser.NORMAL

    def success(self) -> None:
        """
        Perform the Success action:
        - If the input stack is empty, and we've reached the end of the input sequence,
          transition to the final state.
        - Otherwise, it's an error, because we haven't successfully parsed the input.
        """
        print(f"SUCCESS: {self}")
        if self.input_stack or self.index != (len(self.input_sequence) + 1):
            self.error()
            print("Error: Declared success but we didn't satisfy all reqs")

            return
        self.state = RecursiveDescentParser.FINAL

    def parse(self, pif: list):
        print(f"Length of input sequence is {len(pif)}")
        self.state = RecursiveDescentParser.NORMAL
        self.index = 1
        self.working_stack = []
        self.input_sequence = pif
        assert self.input_sequence is not None
        self.input_stack = [self.grammar.start_symbol]
        self.tree.append(
            (self.grammar.start_symbol, RecursiveDescentParser.NO_PARENT, RecursiveDescentParser.NO_SIBLING))

        while self.state not in [RecursiveDescentParser.ERROR, RecursiveDescentParser.FINAL]:
            print(f"MAIN LOOP: {self}")
            match self.state:
                case RecursiveDescentParser.NORMAL:
                    if self.index == 1 + len(self.input_sequence) and 0 == len(self.input_stack):
                        self.success()
                        continue
                    if 0 == len(self.input_stack):
                        print(self)
                        raise ParseException("Unexpected end of input sequence.")
                    current = self.input_stack[0]
                    if current in self.grammar.get_nonterminals():
                        self.expand()
                        continue
                    if current in self.grammar.get_terminals():
                        if current == self.input_sequence[self.index - 1]:
                            self.advance()
                        else:
                            self.momentary_insuccess()
                    continue
                case RecursiveDescentParser.BACKTRACK:
                    if 0 == len(self.working_stack):
                        print(self)
                        raise ParseException("Unexpected end of processed sequence.")
                    current = self.working_stack[0]
                    if current == self.input_sequence[self.index]:
                        self.back()
                    else:
                        self.another_try()
                    continue
                case _:
                    print(self)
                    raise ParseException(f"Unexpected state \"{self.state}\"")
        if self.state == self.FINAL:
            return "Sequence accepted"
        else:
            return "Error: Parsing failed"
