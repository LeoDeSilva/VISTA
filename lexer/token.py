EOF = "EOF"
ERROR = "ERROR"

ANONYMOUS = "ANONYMOUS"
LOCAL = "LOCAL"
GLOBAL = "GLOBAL"
CONDITIONAL = "CONDITIONAL"
FLAG = "FLAG"
COMMENT = "COMMENT"

PARAMETER = "PARAMETER"
IDENTIFIER = "IDENTIFIER"
NUMBER = "NUMBER"
INT = "INT"
FLOAT = "FLOAT"
STRING = "STRING"
BOOL = "BOOL"
NULL = "NULL"
ARRAY = "ARRAY"

# Node Specific
PROGRAM = "PROGRAM"
FUNCTION = "FUNCTION"
INITIALISE = "INITIALISE"
ASSIGN = "ASSIGN"
BIN_OP = "BIN_OP"
UNARY_OP = "UNARY_OP"
INVOKE = "INVOKE"
CONDITION = "CONDITION"
INDEX = "INDEX"
REPLACE = "REPLACE"

# Keywords
LOAD = "LOAD"
IF = "IF"
ELIF = "ELIF"
ELSE = "ELSE"
FOR = "FOR"
WHILE = "WHILE"
ELSE = "ELSE"
RETURN = "RETURN"
BREAK = "BREAK"

# Token Specific
AND = "AND"
OR = "OR"

ADD = "ADD"
SUB = "SUB"
DIV = "DIV"
MUL = "MUL"
MOD = "MOD"
POW = "POW"
NOT = "NOT"

EE = "EE"
EQ = "EQ"
NE = "NE"
LT = "LT"
GT = "GT"
LTE = "LTE"
GTE = "GTE"

COMMA = "COMMA"
SEMICOLON = "SEMICOLON"
COLON = "COLON"
ARROW = "ARROW"

LPAREN = "LPAREN"
RPAREN = "RPAREN"
LSQUARE = "LSQUARE"
RSQUARE = "RSQUARE"
LBRACE = "LBRACE"
RBRACE = "RBRACE"


class LexerException(Exception):
    def __init__(self, line_number, message) -> None:
        self.line_number = line_number
        self.message = message
        super().__init__(f"Line #{self.line_number} " + self.message)


class Token:
    def __init__(self, type: str, literal: str, line_number: int) -> None:
        self.type = type
        self.literal = literal
        self.line_number = line_number

    def __str__(self) -> str:
        return self.type + " : " + self.literal


keywords = {
    "if":     IF,
    "elif": ELIF,
    "else": ELSE,
    "for":    FOR,
    "while":  WHILE,
    "else":   ELSE,
    "return": RETURN,
    "global": GLOBAL,
    "break": BREAK,
    "load": LOAD,
}


def lookup_identifier(identifier: str, lineNumber: int) -> Token and Exception:
    if len(identifier) == 0:
        return None, LexerException(lineNumber, "LookupIdentifier: Expected String Length > 0")

    if identifier in keywords:
        return Token(keywords[identifier], identifier, lineNumber), None

    return Token(IDENTIFIER, identifier, lineNumber), None
