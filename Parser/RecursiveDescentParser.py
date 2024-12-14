from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException


class RecursiveDescentParser:
    NORMAL: str = "normal"
    BACKTRACK: str = "backtrack"
    ERROR: str = "error"
    FINAL: str = "final"

    def error(self) -> None:
        self.state = self.ERROR

    def all_good(self) -> None:
        self.state = self.NORMAL

    def insuccess(self) -> None:
        self.state = self.BACKTRACK

    def end(self) -> None:
        self.state = self.FINAL

    def current_input(self) -> str:
        if len(self.input_stack) <= self.index:
            raise ParseException(
                f"Could not retrieve current input for current index {self.index} and input stack of length {len(self.input_stack)}")
        return self.input_stack[self.index]

    def __init__(self, grammar: ContextFreGrammar, input_sequence) -> None:
        self.grammar: ContextFreGrammar = grammar
        self.input_sequence = input_sequence
        self.state: str = RecursiveDescentParser.NORMAL
        self.index: int = 0
        self.working_stack: list[str] = []
        self.input_stack = [grammar.start_symbol]
        self.parse_table: list[str] = []
        self.production_index_stack: list[int] = []

    def __str__(self) -> str:
        return f"State: {self.state}, Index: {self.index}, Input Stack: {self.input_stack}, Working Stack: {self.working_stack}"

    def expand(self) -> None:
        if not self.input_stack:
            raise ParseException("You should not call 'expand' when the input stack is empty!")

        current: str = self.input_stack.pop(0)
        if current not in self.grammar.get_nonterminals():
            raise ParseException(
                f"You should not call 'expand' when the top is a terminal!\nHead was {current}")

        productions: list[list[str]] = self.grammar.get_productions_for(current)

        if not productions:
            raise ParseException(
                f"You created a non-terminal with no productions\nThe terminal is {current}")

        # Push the first production index for this nonterminal
        self.production_index_stack.append(0)
        current_production = productions[0]

        self.working_stack.append(f"{current}1")
        self.input_stack = current_production + self.input_stack

    def advance(self) -> None:
        """
        Perform the Advance action:
        - Match the terminal at the head of the input stack with the current input symbol.
        - Update the working stack, input stack, and current index.
        """
        if not self.input_stack:
            raise ParseException("You should not call 'expand' when the input stack is empty!")

        head = self.input_stack.pop(0)
        if self.index >= len(self.input_sequence) or head != self.input_sequence[self.index]:
            self.error()
            return

        self.working_stack.append(head)
        self.index += 1

    def momentary_insuccess(self) -> None:
        """
        Perform the Momentary Insuccess action:
        - If the terminal at the head of the input stack does not match the current input symbol,
        transition to the backtrack state.
        """
        if not self.input_stack:
            raise ParseException("You should not call 'momentary_insuccess' when the input stack is empty!")

        current = self.input_stack[0]

        if self.index < len(self.input_sequence) and current != self.input_sequence[self.index]:
            self.insuccess()

    def back(self):
        """
        Perform the Back action:
        - If the head of the working stack is a terminal, move it back to the input stack
          and step back in the input sequence.
        """
        # we can't go back
        # so there are no more opportunities to explore
        if not self.working_stack or self.index <= 0:
            self.error()
            return

        current = self.working_stack.pop()

        # TODO not sure if this check needed here
        if current not in self.grammar.get_terminals():
            raise ParseException("You should not backtrack on a non-terminal")

        self.input_stack.insert(0, current)
        self.index -= 1

    def another_try(self) -> None:
        if not self.working_stack:
            raise ParseException("Cannot perform 'another_try' because the working stack is empty.")

        head = self.working_stack.pop()

        if head[-1].isdigit():
            nonterminal = head[:-1]
        else:
            raise ParseException("You should not call 'another_try' on a terminal.")

        if not self.production_index_stack:
            raise ParseException(f"No production index available for nonterminal {nonterminal}.")

        current_production_index = self.production_index_stack.pop()
        productions = self.grammar.get_productions_for(nonterminal)

        if current_production_index + 1 >= len(productions):
            self.input_stack.insert(0, nonterminal)
            if self.index == 0 and nonterminal == self.grammar.start_symbol:
                raise ParseException("Parsing failed: no more options for the start symbol.")
            self.insuccess()
            return

        next_production_index = current_production_index + 1
        self.production_index_stack.append(next_production_index)
        next_production = productions[next_production_index]

        self.working_stack.append(f"{nonterminal}{next_production_index + 1}")
        current_production = productions[current_production_index]

        for _ in current_production:
            self.input_stack.pop(0)

        self.input_stack = next_production + self.input_stack
        self.all_good()

    def success(self) -> None:
        """
        Perform the Success action:
        - If the input stack is empty, and we've reached the end of the input sequence,
          transition to the final state.
        - Otherwise, it's an error, because we haven't successfully parsed the input.
        """
        if self.index != len(self.input_sequence) or self.input_stack:
            raise ParseException(
                "Parsing unsuccessful: either input stack is not empty or input sequence is incomplete.")
        self.end()

    def parse(self):
        while self.state not in {self.ERROR, self.FINAL}:
            print(self.__str__())

            if self.state == self.NORMAL:
                if self.index == len(self.input_sequence) and not self.input_stack:
                    self.success()
                elif self.input_stack[0] in self.grammar.get_nonterminals():
                    self.expand()
                elif self.input_stack[0] in self.grammar.get_terminals():
                    if self.input_stack[0] == self.input_sequence[self.index]:
                        self.advance()
                    else:
                        self.momentary_insuccess()
                else:
                    self.error()

            elif self.state == self.BACKTRACK:
                if self.working_stack and self.working_stack[-1] in self.grammar.get_terminals():
                    self.back()
                else:
                    self.another_try()

        if self.state == self.FINAL:
            return "Sequence accepted"
        else:
            return "Error: Parsing failed"
