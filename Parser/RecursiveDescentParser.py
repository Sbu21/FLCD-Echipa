from Parser.CFG.ContextFreeGrammar import ContextFreGrammar
from Parser.ParseException import ParseException
from Parser.Token import Token, Nonterminal, Terminal


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
    NORMAL: str = 0
    BACKTRACK: str = 1
    ERROR: str = 2
    FINAL: str = 3

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
        if not grammar.get_productions():
            raise ParseException("Provided grammar does not contain any productions")
        self.grammar: ContextFreGrammar = grammar
        self.input_sequence: list[str] = []
        self.index: int = 0
        self.working_stack: list[Token] = []
        self.input_stack: list[str] = [grammar.start_symbol]
        self.result: list[ResultItem] = []
        self.state: ParserState = ParserState()
        self.length: int = 0

    def __str__(self) -> str:
        result = f'\nInput stack: {self.input_stack}\nWorking stack:{self.working_stack}\nTree:\n'
        for index, production in enumerate(self.result):
            result += f"[{index}] {production}\n"
        return result

    def next_input(self):
        return self.input_sequence[self.index]

    def current_input(self):
        return self.input_sequence[self.index - 1]

    def no_more_input(self) -> bool:
        return 0 == len(self.input_stack)

    def no_more_work(self) -> bool:
        return 0 == len(self.working_stack)

    def expand(self) -> None:
        """
        Perform the Expand action
        Prerequisites
            - state is normal
            - the head of the input stack is a nonterminal
        Action
            (normal, i, [Alpha], [A, Beta]) -> (normal ,i , [Alpha, A1], [Gamma1, Beta])
                where  A -> Gamma1 | Gamma2 | ... represents all productions that correspond to A
                and Gamma1 is the first production of A
        """
        assert self.state.is_normal()
        assert self.input_stack and self.input_stack[0] in self.grammar.get_nonterminals()

        nonterminal = self.input_stack.pop(0)

        productions = self.grammar.get_productions()[nonterminal]
        if not productions:
            raise ParseException(f"No productions found for nonterminal \"{nonterminal}\"")

        production = productions[0]

        self.working_stack.append(Nonterminal(nonterminal, derivation_id=1))

        self.input_stack = list(production) + self.input_stack

        parent_id = len(self.working_stack) - 1
        for i, token in enumerate(production):
            sibling_id = len(self.result) - 1 if i > 0 else ResultItem.NO_SIBLING
            self.result.append(ResultItem(token, parent_id=parent_id, sibling_id=sibling_id))

    def advance(self) -> None:
        """
        Perform the Advance action
        Prerequisites:
            - state is normal
            - the head of the input stack is a terminal
            - the head of the input stack is equal to the current symbol in the input stack
        Action
            (normal, i, [Alpha], [a_i, Beta]) -> (normal, i + 1, [Alpha, a_i], [Beta])
        """
        assert self.state.is_normal()
        assert self.input_stack and self.input_stack[0] in self.grammar.get_terminals()
        # assert self.input_stack[0] == self.next_input()

        terminal = self.input_stack.pop(0)

        self.working_stack.append(Terminal(terminal))

        self.index += 1

    def momentary_insuccess(self) -> None:
        """
        Perform the Momentary Insuccess action
        Prerequisites
            - state is normal
            - head of input stack is a terminal
            - head of input stack is not equal to the current symbol in the input stack
        Action
            (normal, i, [Alpha], [a_i, Beta]) -> (backtrack, i, [alpha], [a_i, Beta])
        """
        assert self.state.is_normal()
        assert self.input_stack and self.input_stack[0] in self.grammar.get_terminals()
        assert self.input_stack[0] != self.next_input()

        self.state.insuccess()

    def back(self):
        """
        Perform the Back action:
        Prerequisites
            - state is backtrack
            - head of working stack is a terminal
        Action
            (backtrack , i, [Alpha, a], [Beta]) -> (backtrack , i - 1, [Alpha], [a, Beta])
        """
        assert self.state.is_backtrack()
        assert self.working_stack and isinstance(self.working_stack[-1], Terminal)

        terminal = self.working_stack.pop()

        self.input_stack.insert(0, terminal.token)

        self.index -= 1

    def another_try(self) -> None:
        """
        Perform the Another Try action
        Prerequisites
            - state is backtrack
            - head of working stack is a nonterminal
        Action
            (backtrack, i, [Alpha, A_j], [Gamma_j, Beta]) ->
                (normal, i, [Alpha, A_(j+1)], [Gamma_(j+1), Beta]) if there is a transition A->Gamma_(j+1)
                (error, i , [Alpha], [Beta]) if i is 1 or A is the start symbol of the grammar
                (backtrack, i, [Alpha], [A, Beta]) else
        """
        assert self.state.is_backtrack()
        assert self.working_stack
        nonterminal = self.working_stack.pop()
        assert isinstance(nonterminal, Nonterminal)
        current_derivation_id = nonterminal.derivation_id

        productions = self.grammar.get_productions()[nonterminal.token]
        if current_derivation_id >= len(productions):
            if self.index == 1 or nonterminal.token == self.grammar.start_symbol:
                self.state.error()
                return
            # Still backtrack, keep current nonterminal
            self.input_stack.insert(0, nonterminal.token)
            return

        next_derivation_id = current_derivation_id + 1
        self.working_stack.append(Nonterminal(nonterminal.token, derivation_id=next_derivation_id))

        next_derivation = productions[next_derivation_id - 1]
        current_derivation = productions[current_derivation_id - 1]
        self.input_stack = self.input_stack[len(current_derivation):]
        self.input_stack = list(next_derivation) + self.input_stack
        self.state.reset()

    def success(self) -> None:
        """
        Perform the Success action
        Action:
            (normal, self.length + 1, [Alpha], []) -> (final, self.length + 1, [Alpha], [])
        """
        assert self.state.is_normal()
        assert self.index == self.length + 1
        assert not self.input_stack
        self.state.end()

    def parse(self, pif: list):
        """
            Given a list of tokens represented by the pif, creates a list of ResultItems representing
                the parsed version of the input
        """
        print(f"Length of input sequence is {len(pif)}")
        self.state.reset()
        self.index = 1
        self.working_stack = []
        self.input_sequence = pif
        assert self.input_sequence is not None
        self.length = len(pif)
        self.input_stack = [self.grammar.start_symbol]
        self.result.append(ResultItem(self.grammar.start_symbol))

        while not (self.state.is_error() or self.state.is_final()):
            print(f"MAIN LOOP: {self}")
            if self.state.is_normal():
                if self.index > self.length and self.no_more_input():
                    self.success()
                    continue
                if self.no_more_input():
                    print(self)
                    raise ParseException("Unexpected end of input sequence.")
                current = self.input_stack[0]
                if current in self.grammar.get_nonterminals():
                    self.expand()
                    continue
                if current in self.grammar.get_terminals():
                    if current == self.current_input():
                        self.advance()
                    else:
                        self.momentary_insuccess()
                continue
            if self.state.is_backtrack():
                if self.no_more_work():
                    print(self)
                    raise ParseException("Unexpected end of processed sequence.")
                current = self.working_stack[0]
                if current == self.next_input():
                    self.back()
                else:
                    self.another_try()
                continue
            print(self)
            raise ParseException(f"Unexpected state \"{self.state}\"")
        return "Sequence accepted" if self.state.is_final() else "Error: Parsing failed"
