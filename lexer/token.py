from sre_constants import IN
from xml.dom.minidom import Identified


EOF = "EOF"
ERROR = "ERROR"

IDENTIFIER = "IDENTIFIER"
NUMBER     = "NUMBER"
TYPE = "TYPE"
INT        = "INT"
FLOAT      = "FLOAT"
STRING     = "STRING"
BOOL       = "BOOL"
NULL       = "NULL"
VOID = "VOID"
ARRAY = "ARRAY"

IF     = "IF"
FOR    = "FOR"
WHILE  = "WHILE"
ELSE   = "ELSE"
RETURN = "RETURN"

ADD = "ADD"
SUB = "SUB"
DIV = "DIV"
MUL = "MUL"
MOD = "MOD"
POW = "POW"
NOT = "NOT"

EE  = "EE"
EQ  = "EQ"
NE  = "NE"
LT  = "LT"
GT  = "GT"
LTE = "LTE"
GTE = "GTE"

COMMA     = "COMMA"
SEMICOLON = "SEMICOLON"
COLON     = "COLON"
ARROW     = "ARROW"

LPAREN  = "LPAREN"
RPAREN  = "RPAREN"
LSQUARE = "LSQUARE"
RSQUARE = "RSQUARE"
LBRACE  = "LBRACE"
RBRACE  = "RBRACE"

class LexerException(Exception):
    pass

class Token:
    def __init__(self, type : str, literal : str) -> None:
        self.type = type
        self.literal = literal

    def __str__(self) -> str:
        return self.type + " : " + self.literal

class Type(Token):
    def __init__(self, primary_type: str,literal: str, secondary_type=None)  -> None:
        super().__init__(TYPE, literal)
        self.primary_type = primary_type
        self.secondary_type = secondary_type

types = {
    "string":   STRING,
	"int":      INT,
	"float":    FLOAT,
	"bool":     BOOL,
    "void": VOID,
}

keywords = {
	"if":     IF,
	"for":    FOR,
	"while":  WHILE,
	"else":   ELSE,
	"return": RETURN,
}

def lookup_identifier(identifier : str) -> Token and Exception:
    if len(identifier) == 0:
        return None, LexerException("LookupIdentifier: Expected String Length > 0") 

    if identifier in keywords:
        return  Token(keywords[identifier], identifier), None

    if identifier in types:
        return Type(types[identifier],identifier), None

    return Token(IDENTIFIER, identifier), None
