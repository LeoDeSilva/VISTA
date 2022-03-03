from multiprocessing.dummy import Array
from operator import contains
from tracemalloc import start
from typing import List, Dict

from idna import valid_contextj
from lexer.token import *
from parse.nodes import IdentifierNode


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
DIGITS = "0123456789"


class Lexer:
    def __init__(self, program_string: str) -> None:
        self.program_string = program_string
        self.char_position = 0
        self.read_position = 1
        self.line_number = 1
        self.current_char = self.program_string[self.char_position]

    def advance(self) -> None:
        if self.read_position >= len(self.program_string):
            self.current_char = ""  # Used to determine end of file
        else:
            self.current_char = self.program_string[self.read_position]

        self.char_position = self.read_position
        self.read_position += 1

    def retreat_to_position(self, position: int) -> None:
        self.char_position = position
        self.read_position = position + 1
        self.current_char = self.program_string[self.char_position]

    def peek(self) -> str:
        if self.read_position >= len(self.program_string):
            return ""
        return self.program_string[self.read_position]

    def lex_program(self) -> List[Token] and Exception:
        lexed_tokens = []
        while self.current_char != "":
            tok, err = self.lex_next_character()
            if err != None:
                return [], err

            lexed_tokens.append(tok)

        lexed_tokens.append(
            Token(EOF, "", self.line_number)
        )

        return lexed_tokens, None

    def lex_next_character(self) -> Token and Exception:
        token, err = None, None
        self.consume_whitespace()

        if self.current_char == "+":
            token = Token(ADD, self.current_char, self.line_number)
        elif self.current_char == "-":
            token = Token(SUB, self.current_char, self.line_number)
        elif self.current_char == "*":
            token = Token(MUL, self.current_char, self.line_number)
        elif self.current_char == "%":
            token = Token(MOD, self.current_char, self.line_number)
        elif self.current_char == "^":
            token = Token(POW, self.current_char, self.line_number)

        elif self.current_char == ",":
            token = Token(COMMA, self.current_char, self.line_number)
        elif self.current_char == ":":
            token = Token(COLON, self.current_char, self.line_number)
        elif self.current_char == ";":
            token = Token(SEMICOLON, self.current_char, self.line_number)

        elif self.current_char == "(":
            token = Token(LPAREN, self.current_char, self.line_number)
        elif self.current_char == ")":
            token = Token(RPAREN, self.current_char, self.line_number)
        elif self.current_char == "{":
            token = Token(LBRACE, self.current_char, self.line_number)
        elif self.current_char == "}":
            token = Token(RBRACE, self.current_char, self.line_number)
        elif self.current_char == "[":
            token, err = self.lex_type_identifier()
        elif self.current_char == "]":
            token = Token(RSQUARE, self.current_char, self.line_number)

        elif self.current_char == "/":
            token, err = self.lex_multichar_token(DIV, {"/": COMMENT})

        elif self.current_char == "=":
            token, err = self.lex_multichar_token(EQ, {"=": EE, ">": ARROW})
        elif self.current_char == "!":
            token, err = self.lex_multichar_token(NOT, {"=": NE})
        elif self.current_char == ">":
            token, err = self.lex_multichar_token(GT, {"=": GTE})
        elif self.current_char == "<":
            token, err = self.lex_multichar_token(LT, {"=": LTE})

        elif self.current_char == "&":
            token, err = self.lex_multichar_token(ERROR, {"&": AND})
        elif self.current_char == "|":
            token, err = self.lex_multichar_token(ERROR, {"|": OR})

        elif self.current_char in ("'", '"'):
            token, err = self.lex_string(self.current_char)

        elif self.current_char in LETTERS:
            return self.lex_identifier()

        elif self.current_char in DIGITS:
            return self.lex_number()

        else:
            return None, LexerException(self.line_number, "Lex_Char: Unexpected Character In Lexer: " + self.current_char)

        self.advance()
        return token, err

    def is_type_identifier(self, type_string: str) -> bool:
        if len(type_string) <= 0:
            return False

        pending_brackets = 0
        for type_character in type_string:
            if type_character == "[":
                pending_brackets += 1

            elif type_character == "]":
                pending_brackets -= 1

        terminates_with_letter = type_string[-1] in LETTERS

        return terminates_with_letter and pending_brackets == 0

    def lex_type_identifier(self) -> Token and Exception:
        identifier_start_position = self.char_position

        while self.current_char in "[]" + LETTERS:
            self.advance()

        type_identifier = self.program_string[identifier_start_position:self.char_position]

        if not self.is_type_identifier(type_identifier):
            self.retreat_to_position(identifier_start_position)
            return Token(LSQUARE, "[", self.line_number), None

        return Token(IDENTIFIER, type_identifier, self.line_number), None

    def consume_whitespace(self) -> None:
        while self.current_char in (" ", "\t", "\r", "\n"):
            if self.current_char == "\n":
                self.line_number += 1
            self.advance()

    def lex_multichar_token(self, primary_type: str, secondary_types: Dict[str, str]) -> Token and Exception:
        char = self.current_char

        if self.peek() in secondary_types:
            self.advance()
            return Token(secondary_types[self.current_char], char + self.current_char, self.line_number), None

        return Token(primary_type, char, self.line_number), None

    def is_float_or_int(self, number: str) -> str and Exception:
        if number.count(".") > 1:
            return None, LexerException(self.line_number, "lex_number: Unexpected Number of Decimal Points In Number: " + number)
        if number[-1] == ".":
            return None, LexerException(self.line_number, "lex_number: Unexpected Decimal Point At End Of Number: " + number)

        if number.count(".") == 1:
            return FLOAT, None

        return INT, None

    def lex_number(self):
        number_start_position = self.char_position
        while self.current_char in [*DIGITS, "."]:
            self.advance()

        number_string = self.program_string[number_start_position:self.char_position]
        number_type, err = self.is_float_or_int(number_string)

        return Token(number_type, number_string, self.line_number), err

    def lex_string(self, terminate_char: str) -> Token and Exception:
        self.advance()

        string_start_position = self.char_position

        while self.current_char != terminate_char:
            if self.current_char == "":
                return None, LexerException(self.line_number, "lex_string: Expected String Terminator: '" + terminate_char)
            self.advance()

        return Token(STRING, self.program_string[string_start_position:self.char_position], self.line_number), None

    def lex_identifier(self) -> Token and Exception:
        identifier_start_position = self.char_position

        while self.current_char in [*LETTERS, *DIGITS] and self.current_char != "":
            self.advance()

        identifier_string = self.program_string[identifier_start_position:self.char_position]
        return lookup_identifier(identifier_string, self.line_number)
