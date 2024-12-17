class ContextFreGrammar:
    NONTERMINALS: int = 0
    TERMINALS: int = 1
    PRODUCTIONS: int = 2
    START_SYMBOL: int = 3

    @staticmethod
    def str_to_section(string: str) -> int or None:
        match string.strip():
            case 'Non-terminals':
                return ContextFreGrammar.NONTERMINALS
            case 'Terminals':
                return ContextFreGrammar.TERMINALS
            case 'Productions':
                return ContextFreGrammar.PRODUCTIONS
            case 'Start symbol':
                return ContextFreGrammar.START_SYMBOL
            case _:
                return None

    @staticmethod
    def filter_lines(lines: list[str]) -> list[str]:
        return [line.strip()
                for line in lines
                if line and len(line.strip()) != 0]

    def __init__(self, filename: str):
        self.nonterminals: set[str] = set()
        self.terminals: set[str] = set()
        self.start_symbol: str = ""
        self.productions: dict[str, list[list[str]]] = {}

        with open(filename, 'r') as file:
            lines: [str] = ContextFreGrammar.filter_lines(file.readlines())

        section: int or None = None
        for line in lines:
            line = line.strip()

            if line.startswith("#"):
                section = ContextFreGrammar.str_to_section(line.strip("#").strip())
                continue

            if section is not None:
                match section:
                    case ContextFreGrammar.NONTERMINALS:
                        self.nonterminals.add(line)
                    case ContextFreGrammar.TERMINALS:
                        self.terminals.add(line.strip('"'))
                    case ContextFreGrammar.PRODUCTIONS:
                        lhs, rhs = line.split("->")
                        lhs = lhs.strip()
                        rhs = [item.strip() for item in rhs.strip().split()]
                        if rhs == ['eps']:
                            rhs = []
                        if lhs in self.productions:
                            self.productions[lhs].extend([rhs])
                        else:
                            self.productions[lhs] = [rhs]
                    case ContextFreGrammar.START_SYMBOL:
                        self.start_symbol = line.strip()

    def __str__(self):
        return (f"Non-Terminals: {self.nonterminals}\n"
                f"Terminals: {self.terminals}\n"
                f"Start Symbol: {self.start_symbol}\n"
                f"Productions:\n" +
                "\n".join(f"{nonterminal} -> {' | '.join(' '.join(blabla) for blabla in self.productions[nonterminal])}"
                          for nonterminal in self.productions))

    def get_nonterminals(self) -> set[str]:
        return self.nonterminals

    def get_terminals(self) -> set[str]:
        return self.terminals

    def get_productions(self) -> dict[str, list[list[str]]]:
        return self.productions

    def get_productions_for(self, nonterminal):
        return self.productions.get(nonterminal, [])

    def is_valid_cfg(self):
        return all(lhs in self.nonterminals for lhs in self.productions)


