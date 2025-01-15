from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException


class Token:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"{{ value:\"{self.value}\"}}"

    def __eq__(self, other):
        return self.value == other.value


class Terminal(Token):
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return f"Terminal: {super().__repr__()}"

    def __eq__(self, other):
        return isinstance(other, Terminal) and super().__eq__(other)


class NonTerminal(Token):
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return f"NonTerminal: {super().__repr__()}"

    def __eq__(self, other):
        return isinstance(other, NonTerminal) and super().__eq__(other)


class ResultItem:
    DEFAULT_ROW = 0
    NO_PARENT = -1
    NO_SIBLING = -1

    def __init__(self, token: Token, row: int = DEFAULT_ROW, parent_id: int = NO_PARENT, sibling_id: int = NO_SIBLING):
        self.token = token
        self.row = row
        self.parent_id = parent_id
        self.sibling_id = sibling_id

    def __repr__(self):
        return f"ResultItem: [ {self.row} ] \'{self.token}\', parent_id: {self.parent_id}, sibling_id: {self.sibling_id}}}"

    def __eq__(self, other):
        return (
                isinstance(other, ResultItem) and
                self.token == other.token and
                self.row == other.row and
                self.parent_id == other.parent_id and
                self.sibling_id == other.sibling_id
        )


class RecursiveDescentParser:
    def __init__(self, grammar: ContextFreGrammar, token_sequence: list[str]):
        self.grammar: ContextFreGrammar = grammar
        self.result_builder: [ResultItem] = [ResultItem(NonTerminal(grammar.start_symbol))]
        self.working_stack: [ResultItem] = [ResultItem(NonTerminal(grammar.start_symbol))]
        self.index = 0
        self.input = token_sequence
        try:
            self.parse()
            print(f"Parsing successful:\n{"\n".join([str(item) for item in self.result_builder])}")
        except ParseException as e:
            print(f"Parse failed: {e}")

    def __repr__(self):
        return (f"Index: {self.index}\n" +
                f"Input: {self.input}\n" +
                f"Current Symbol: {self.input[self.index] if self.index < len(self.input) else None}\n" +
                f"Working Stack: {self.working_stack}\n" +
                f"Working Symbol: {self.working_stack[0]}\n"
                )

    def backup(self) -> tuple[int, list[ResultItem], list[ResultItem]]:
        return self.index, self.result_builder[:], self.working_stack[:]

    def restore(self, state: tuple[int, list[ResultItem], list[ResultItem]]):
        print(f"\nRestoring {state}\n")
        self.index, self.result_builder, self.working_stack = state

    def consume_terminal(self):
        if self.index >= len(self.input):
            raise ParseException(f"Input exhausted while expecting a terminal.\nFull state:{self}")

        current_terminal = self.working_stack[0].token
        print(f"Consuming terminal \"{current_terminal}\"")

        if self.input[self.index] != current_terminal.value:
            raise ParseException(
                f"Expected terminal '{current_terminal.value}' but found '{self.input[self.index]}'\nFull state:{self}")
        self.working_stack.pop(0)
        self.index += 1

    def parse(self):
        if self.index == len(self.input) and not self.working_stack:
            return

        if not self.working_stack:
            raise ParseException(f"Stack mismatch at index {self.index}: input not fully consumed.")

        current_item = self.working_stack[0]

        if isinstance(current_item.token, Terminal):
            self.consume_terminal()
            self.parse()
            return
        elif isinstance(current_item.token, NonTerminal):
            non_terminal = current_item.token
            productions = self.grammar.get_productions().get(non_terminal.value, [])
            if not productions:
                raise ParseException(f"No productions for non-terminal '{non_terminal.value}'.")

            for production in productions:
                state = self.backup()
                print(f'Trying {non_terminal.value} -> {production}')
                parent_id = self.result_builder.index(current_item)
                self.working_stack.pop(0)

                previous_sibling = ResultItem.NO_SIBLING
                current_expansion = []
                for i, token in enumerate(production):
                    is_terminal = token in self.grammar.get_terminals()
                    new_item = ResultItem(
                        Terminal(token) if is_terminal else NonTerminal(token),
                        row=len(self.result_builder),
                        parent_id=parent_id,
                        sibling_id=previous_sibling
                    )
                    self.result_builder.append(new_item)
                    current_expansion.append(new_item)
                    previous_sibling = new_item.row
                self.working_stack = current_expansion + self.working_stack
                try:
                    self.parse()
                    return
                except ParseException as e:
                    print(e)
                    # Another try
                    self.restore(state)

            raise ParseException(f"Failed to expand non-terminal '{non_terminal.value}' at index {self.index}.")
