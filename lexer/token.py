EOF = "EOF"
ERROR = "ERROR"

IDENTIFIER = "IDENTIFIER"
INT         = "INT"
FLOAT       = "FLOAT"
STRING      = "STRING"
INT_ARRAY   = "INT_ARRAY"
FLOAT_ARRAY = "FLOAT_ARRAY"
STR_ARRAY   = "STRING_ARRAY"
BOOL        = "BOOL"
BOOL_ARRAY  = "BOOL_ARRAY"
NULL        = "NULL"

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

class ExpectedLengthError(Exception):
    pass

keywords = {
    "string":   STRING,
	"int":      INT,
	"float":    FLOAT,
	"string[]": STR_ARRAY,
	"int[]":    INT_ARRAY,
	"float[]":  FLOAT_ARRAY,
	"bool":     BOOL,
	"bool[]":   BOOL_ARRAY,
	"null":     NULL,

	"if":     IF,
	"for":    FOR,
	"while":  WHILE,
	"else":   ELSE,
	"return": RETURN,
}

def lookup_identifier(identifier : str) -> str and Exception:
    if len(identifier) == 0:
        return "", ExpectedLengthError("LookupIdentifier: Expected String Length > 0") 

    if identifier in keywords:
        return keywords[identifier], None

    return IDENTIFIER, None

class Token:
    def __init__(self, type : str, literal : str) -> None:
        self.type = type
        self.literal = literal