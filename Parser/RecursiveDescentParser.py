from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException


class RecursiveDescentParser:
    NORMAL: str = "normal"
    BACKTRACK: str = "backtrack"
    ERROR: str = "error"
    FINAL: str = "final"

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
        if not self.grammar.get_productions():
            raise ParseException("Provided grammar does not contain any productions")

    def __str__(self) -> str:
        return f"State: {self.state}, Index: {self.index}, Input Stack: {self.input_stack}, Working Stack: {self.working_stack}"

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
        first = productions[0]
        self.input_stack = list(first) + self.input_stack
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
        self.index -= 1
        self.input_stack.insert(0, terminal)

    def another_try(self) -> None:
        print(f"ANOTHER TRY: {self}")
        if 0 == len(self.working_stack):
            self.error()
            print("Error: Nowhere to backtrack")
            return
        last = self.working_stack.pop()
        if not (isinstance(last, tuple)
                and len(last) == 2
                and isinstance(last[0], str)
                and isinstance(last[1], int)):
            self.error()
            print(f"Error: Tried taking another choice for a terminal ({last})")
            return

        last_nonterminal, prod_index = last
        productions = self.grammar.get_productions_for(last_nonterminal)
        if prod_index >= len(productions) - 1:
            if last_nonterminal == self.grammar.start_symbol and self.index == 1:
                self.error()
                print("Error: We have exhausted the search")
            return
        next_prod = productions[prod_index + 1]
        # self.input_stack = list(next_prod) + self.input_stack[len(next_prod):]
        self.input_stack = list(next_prod) + self.input_stack[len(productions[prod_index]):]

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
        self.input_stack = [_ for _ in pif]
        while self.state not in [RecursiveDescentParser.ERROR, RecursiveDescentParser.FINAL]:
            print(f"MAIN LOOP: {self}")
            match self.state:
                case RecursiveDescentParser.NORMAL:
                    if self.index == 1 + len(self.input_sequence) and 0 == len(self.input_stack):
                        self.success()
                        continue
                    if 0 == len(self.input_stack):
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
                    if len(self.working_stack):
                        raise ParseException("Unexpected end of processed sequence.")
                    current = self.working_stack[0]
                    if current == self.input_sequence[self.index]:
                        self.back()
                    else:
                        self.another_try()
                    continue
                case _:
                    raise ParseException(f"Unexpected state \"{self.state}\"")
        if self.state == self.FINAL:
            return "Sequence accepted"
        else:
            return "Error: Parsing failed"
