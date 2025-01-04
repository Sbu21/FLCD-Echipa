from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException


class Token:
    def __init__(self, token: str):
        self.token = token


class Nonterminal(Token):
    def __init__(self, token: str, derivation_id: int = 1):
        super().__init__(token)
        self.derivation_id = derivation_id


class Terminal(Token):
    def __init__(self, token: str):
        super().__init__(token)


class ResultItem:
    NO_PARENT: int = -1
    NO_SIBLING: int = -1

    def __init__(self, token: str, parent_id: int = NO_PARENT, sibling_id: int = NO_SIBLING):
        assert len(token) > 0
        assert parent_id == ResultItem.NO_PARENT or parent_id >= 0
        assert sibling_id == ResultItem.NO_SIBLING or sibling_id >= 0

        self.token: str = token
        self.parent_id: int = parent_id
        self.sibling_id: int = sibling_id

    def __str__(self):
        return f"<{self.token}, {self.parent_id}, {self.sibling_id}>"


class ParserState:
    NORMAL: str = "normal"
    BACKTRACK: str = "backtrack"
    ERROR: str = "error"
    FINAL: str = "final"

    def __init__(self):
        self.state = ParserState.NORMAL

    def __str__(self):
        return f"<{self.state}>"

    def error(self) -> None:
        self.state = ParserState.ERROR

    def is_error(self) -> bool:
        return self.state is ParserState.ERROR

    def reset(self) -> None:
        self.state = ParserState.NORMAL

    def is_normal(self) -> bool:
        return self.state is ParserState.NORMAL

    def insuccess(self) -> None:
        self.state = ParserState.BACKTRACK

    def is_backtrack(self) -> bool:
        return self.state is ParserState.BACKTRACK

    def end(self) -> None:
        self.state = ParserState.FINAL

    def is_final(self) -> bool:
        return self.state is ParserState.FINAL


class RecursiveDescentParser:

    def __init__(self, grammar: ContextFreGrammar) -> None:
        self.grammar: ContextFreGrammar = grammar
        self.input_sequence: list | None = None
        self.index: int = 0
        self.working_stack: list[Token] = []
        self.input_stack: list[str] = list(grammar.start_symbol)
        self.parse_table: list[str] = list()
        self.production_index_stack: list[int] = list()
        self.result: list[ResultItem] = list()
        self.state: ParserState = ParserState()

        if not self.grammar.get_productions():
            raise ParseException("Provided grammar does not contain any productions")

    def __str__(self) -> str:
        result = f'\nInput stack: {self.input_stack}\nWorking stack:{self.working_stack}\nTree:\n'
        for index, production in enumerate(self.result):
            result += f"[{index}] {production}\n"
        return result

    def expand(self) -> None:
        print(f"EXPAND: {self}")
        if 0 == len(self.input_stack):
            self.state.error()
            print("Error: Attempted to expand an empty input stack")
            return

        current = self.input_stack.pop(0)
        if current not in self.grammar.get_nonterminals():
            self.state.error()
            print(f"Error: Attempted to expand a terminal ({current})")
            return
        productions = self.grammar.get_productions_for(current)
        if 0 == len(productions):
            self.state.error()
            print(f"Error: Nonterminal {current} has no productions")
            return
        first_production = productions[0]
        self.input_stack = list(first_production) + self.input_stack
        parent_index = len(self.result) - 1
        sibling_index = ResultItem.NO_SIBLING
        for symbol in first_production:
            self.result.append(ResultItem(symbol, parent_index, sibling_index))
            sibling_index += 1

        self.working_stack.append(
            Nonterminal(current, 1)
        )

    def advance(self) -> None:
        """
        Perform the Advance action:
        - Match the terminal at the head of the input stack with the current input symbol.
        - Update the working stack, input stack, and current index.
        """
        print(f"ADVANCE: {self}")
        self.index += 1
        if len(self.input_stack) == 0:
            self.state.error()
            print("Tried advancing with an empty input stack")
            return
        self.working_stack.append(
            Terminal(self.input_stack.pop(0))
        )

    def momentary_insuccess(self) -> None:
        """
        Perform the Momentary Insuccess action:
        - If the terminal at the head of the input stack does not match the current input symbol,
        transition to the backtrack state.
        """
        print(f"MOMENTARY INSUCCESS: {self}")
        self.state.insuccess()

    def back(self):
        """
        Perform the Back action:
        - If the head of the working stack is a terminal, move it back to the input stack
          and step back in the input sequence.
        """
        print(f"BACK: {self}")
        if 0 == len(self.working_stack):
            self.state.error()
            print("Error: Nowhere to backtrack")
            return

        terminal = self.working_stack.pop()
        while isinstance(terminal, Terminal):
            terminal = self.working_stack.pop()
            self.result.pop()
            self.index -= 1

        self.input_stack.insert(0, terminal.token)
        self.result.pop()

    def another_try(self) -> None:
        print(f"ANOTHER TRY: {self}")
        if 0 == len(self.working_stack):
            self.state.error()
            print("Error: Nowhere to backtrack")
            return

        last_terminal_maybe = self.working_stack.pop()
        while isinstance(last_terminal_maybe, Nonterminal):
            last_terminal_maybe = self.working_stack.pop()
            self.index -= 1

        if isinstance(last_terminal_maybe, Terminal):
            self.state.error()
            print(f"Error: Tried taking another choice for a terminal ({last_terminal_maybe})")
            return

        last_nonterminal, prod_index = last_terminal_maybe
        productions = self.grammar.get_productions_for(last_nonterminal)

        if prod_index >= len(productions) - 1:
            print(f"Exhausted all productions for {last_nonterminal}, backtracking further...")
            return self.another_try()  # Recursive call to try at a higher level

        next_prod = productions[prod_index + 1]
        self.input_stack = list(next_prod) + self.input_stack[len(productions[prod_index]):]

        parent_index = len(self.result) - 1
        sibling_index = ResultItem.NO_SIBLING
        for symbol in next_prod:
            self.result.append(ResultItem(symbol, parent_index, sibling_index))
            sibling_index += 1

        self.working_stack.append(Nonterminal(last_nonterminal, prod_index + 1))
        self.state.reset()

    def success(self) -> None:
        """
        Perform the Success action:
        - If the input stack is empty, and we've reached the end of the input sequence,
          transition to the final state.
        - Otherwise, it's an error, because we haven't successfully parsed the input.
        """
        print(f"SUCCESS: {self}")
        if self.input_stack or self.index != (len(self.input_sequence) + 1):
            self.state.error()
            print("Error: Declared success but we didn't satisfy all reqs")
            return
        self.state.end()

    def parse(self, pif: list):
        print(f"Length of input sequence is {len(pif)}")
        self.state.reset()
        self.index = 1
        self.working_stack = []
        self.input_sequence = pif
        assert self.input_sequence is not None
        self.input_stack = [self.grammar.start_symbol]
        self.result.append(ResultItem(self.grammar.start_symbol))

        while not (self.state.is_error() or self.state.is_final()):
            print(f"MAIN LOOP: {self}")
            match True:
                case self.state.is_normal():
                    pass
                case self.state.is_backtrack():
                    pass
                case _:
                    pass

        return "Sequence accepted" if self.state.is_final() else "Error: Parsing failed"
