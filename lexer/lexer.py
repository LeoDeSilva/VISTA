from typing import List, Dict
from lexer.token import *


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
DIGITS = "0123456789"

class Lexer:
    def __init__(self, program : str) -> None:
        self.program = program
        self.position = 0
        self.readPosition = 1
        self.char = self.program[self.position]

    def advance(self) -> None:
        if self.readPosition >= len(self.program):
            self.char = ""
        else:
            self.char = self.program[self.readPosition]

        self.position = self.readPosition
        self.readPosition += 1

    def peek(self) -> str:
        if self.readPosition >= len(self.program):
            return ""
        return self.program[self.readPosition]


    def lex(self) -> List[Token] and Exception:
        tokens = []
        while self.char != "":
            tok, err = self.lex_token()
            if err != None: return [], err
            tokens.append(tok)
        tokens.append(Token(EOF,""))
        return tokens, None

    def lex_token(self) -> Token and Exception:
        token = Token(ERROR, "")
        self.consume_whitespace()

        if self.char == "+":
            token = Token(ADD, self.char)
        elif self.char == "-":
            token = Token(SUB, self.char)
        elif self.char == "*":
            token = Token(MUL, self.char)
        elif self.char == "/":
            token = Token(DIV, self.char)
        elif self.char == "%":
            token = Token(MOD, self.char)
        elif self.char == "^":
            token = Token(POW, self.char)

        elif self.char == ",":
            token = Token(COMMA, self.char)
        elif self.char == ":":
            token = Token(COLON, self.char)
        elif self.char == ";":
            token = Token(SEMICOLON, self.char)

        elif self.char == "(":
            token = Token(LPAREN, self.char)
        elif self.char == ")":
            token = Token(RPAREN, self.char)
        elif self.char == "{":
            token = Token(LBRACE, self.char)
        elif self.char == "}":
            token = Token(RBRACE, self.char)
        elif self.char == "[":
            token = Token(LSQUARE, self.char)
        elif self.char == "]":
            token = Token(RSQUARE, self.char)

        elif self.char == "=":
            token,err = self.lex_double(EQ,{"=":EE,">":ARROW})
            if err != None: return None,err
        elif self.char == "!":
            token,err = self.lex_double(NOT,{"=":NE})
            if err != None: return None,err
        elif self.char == ">":
            token,err = self.lex_double(GT,{"=":GTE})
            if err != None: return None,err
        elif self.char == "<":
            token,err = self.lex_double(LT,{"=":LTE})
            if err != None: return None,err

        elif self.char == "&":
            token,err = self.lex_double(ERROR,{"&":AND})
            if err != None: return None,err
        elif self.char == "|":
            token,err = self.lex_double(ERROR,{"|":OR})
            if err != None: return None,err

        elif self.char in ("'",'"'):
            token, err = self.lex_string(self.char)
            if err != None: return None, err

        elif self.char in LETTERS:
            token, err = self.lex_identifier()
            if err != None: return None, err
            return token, None

        elif self.char in DIGITS:
            token, err = self.lex_number()
            if err != None: return None, err
            return token, None

        else:
            return None, LexerException("Lex_Char: Unexpected Character In Lexer: " + self.char)

        if token.type == ERROR:
            return None, LexerException("Lex_Char: Unexpected Character In Lexer: " + self.char)

        self.advance()
        return token, None

    def consume_whitespace(self) -> None:
        while self.char in (" ", "\t", "\r", "\n"):
            self.advance()

    def lex_double(self, primary_type : str, secondary_types : Dict[str, str]) -> Token and Exception:
        char = self.char
        if self.peek() in secondary_types:
            self.advance()
            return Token(secondary_types[self.char], char + self.char), None
        return Token(primary_type, char), None

    def lex_number(self):
        position = self.position
        while self.char in [*DIGITS, "."]:
            self.advance()

        number = self.program[position:self.position]
        numberType, err = self.is_float(number)
        if err != None: return None, err
        return Token(numberType, number), None

    def is_float(self, number : str) -> str and Exception:
        if number.count(".") > 1: return None, LexerException("lex_number: Unexpected Number of Decimal Points In Number: " + number)
        if number[-1] == ".": return None, LexerException("lex_number: Unexpected Decimal Point At End Of Number: "+ number)

        if number.count(".") == 1:
            return FLOAT, None

        return INT, None

    def lex_string(self, terminate : str) -> Token and Exception:
        self.advance()
        position = self.position
        while self.char != terminate:
            if self.char == "":
                return None, LexerException("lex_string: Expected String Terminator: '" + terminate + "' String: "  + self.program[position:self.position])
            self.advance()

        return Token(STRING, self.program[position:self.position]), None

    def lex_identifier(self) -> Token and Exception:
        position = self.position

        while self.char in  [*LETTERS, *DIGITS] and self.char != "":
            self.advance()

        identifier = self.program[position:self.position]
        token, err = lookup_identifier(identifier)
        if err != None: return None, err

        if token.type == TYPE and self.char == "[":
            self.advance()
            if self.char != "]":
                return None, LexerException("Lex_Identifier: Expected TOKEN ']'")
            self.advance()
            return Type(ARRAY, token.literal + "[]", token.primary_type), None

        return token, None


