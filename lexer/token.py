EOF = "EOF"
ERROR = "ERROR"

LOAD = "LOAD"

LOCAL = "LOCAL"
GLOBAL = "GLOBAL"
CONDITIONAL = "CONDITIONAL"
FLAG = "FLAG"
COMMENT = "COMMENT"

PROGRAM = "PROGRAM"
FUNCTION = "FUNCTION"
INITIALISE = "INITIALISE"
ASSIGN = "ASSIGN"
BIN_OP = "BIN_OP"
UNARY_OP = "UNARY_OP"
INVOKE = "INVOKE"

PARAMETER = "PARAMETER"
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

CONDITION = "CONDITION"
IF     = "IF"
ELIF = "ELIF"
ELSE = "ELSE"
FOR    = "FOR"
WHILE  = "WHILE"
ELSE   = "ELSE"
RETURN = "RETURN"
BREAK = "BREAK"
INDEX = "INDEX"
REPLACE = "REPLACE"

AND = "AND"
OR = "OR"

TRUE = "TRUE"
FALSE = "FALSE"

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
    def __init__(self, primary_type: str,literal: str)  -> None:
        super().__init__(IDENTIFIER, literal)
        self.primary_type = primary_type

class ArrayType(Type):
    def __init__(self, secondary_type: str, literal: str) -> None:
        super().__init__(ARRAY, literal)
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

def lookup_identifier(identifier : str) -> Token and Exception:
    if len(identifier) == 0:
        return None, LexerException("LookupIdentifier: Expected String Length > 0") 

    if identifier in keywords:
        return Token(keywords[identifier], identifier), None
    # elif identifier in types:
    #     return Type(identifier, types[identifier]), None

    return Token(IDENTIFIER, identifier), None
