class Token:
    def __init__(self, token: str):
        self.token = token

    def __str__(self):
        return f"<{self.token}>"

    def __repr__(self):
        return self.__str__()


class Nonterminal(Token):
    def __init__(self, token: str, derivation_id: int = 0):
        super().__init__(token)
        self.derivation_id = derivation_id

    def __str__(self):
        return f"[N <{self.token}, {self.derivation_id}>]"


class Terminal(Token):
    def __init__(self, token: str):
        super().__init__(token)

    def __str__(self):
        return f"[T <{self.token}>]"
