from typing import List
from lexer.token import *

class Lexer:
    def __init__(self, program : str) -> None:
        self.program = program
        self.position = 0
        self.char = self.program[self.position]

    def lex(self) -> List[Token] and Exception:
        print(self.program)
        return [], None

