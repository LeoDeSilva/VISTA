from multiprocessing.dummy import Array
from tracemalloc import start
from typing import List, Dict

from idna import valid_contextj
from lexer.token import *
from parse.nodes import IdentifierNode


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
DIGITS = "0123456789"

class Lexer:
    def __init__(self, program : str) -> None:
        self.program = program
        self.position = 0
        self.readPosition = 1
        self.char = self.program[self.position]

    def advance(self, inc : int = 1) -> None:
        if self.readPosition >= len(self.program):
            self.char = ""
        else:
            self.char = self.program[self.readPosition]

        self.position = self.readPosition
        self.readPosition += inc

    def retreat_until(self, char : str) -> None:
        while self.char != char:
            self.retreat()

    def retreat(self, inc : int = 1) -> None:
        if self.position - inc < 0:
            self.char = ""
        else:
            self.char = self.program[self.position - inc]
        
        self.position -= inc
        self.readPosition -= inc

    def reset(self, pos : int) -> None:
        self.position = pos
        self.readPosition = pos + 1
        self.char = self.program[self.position]

    def peek(self, inc : int = 0) -> str:
        if self.readPosition + inc >= len(self.program):
            return ""
        return self.program[self.readPosition + inc]


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
            token,err = self.lex_double(DIV,{"/":COMMENT})
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
            token, err = self.lex_type()
            if err != None: return None, err
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

    def valid_type(self, type) -> bool:
        if len(type) < 3:
            return False
        i = 0
        while i < len(type):
            letter = type[i]
            if letter == "[":
                if type[i+1] != "]":
                    return False
                i+=1
            elif letter not in LETTERS:
                return False
            i+=1
        return True

    def lex_type(self) -> Token and Exception:
        start_pos = self.position
        while self.char in ("[]") or self.char in LETTERS:
            self.advance()

        identifier = self.program[start_pos:self.position]
        self.retreat()

        if not self.valid_type(identifier):
            self.reset(start_pos)
            return Token(LSQUARE, "["), None

        return Token(IDENTIFIER, identifier), None

        
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

        return token, None


