package lexer

import "errors"

type Token struct {
	Type    string
	Literal string
}

func NewToken(tokenType string, ch byte) Token {
	return Token{Type: tokenType, Literal: string(ch)}
}

func lookupIdentifier(identifier string) (string, error) {
	if len(identifier) == 0 {
		return "", errors.New("LexerError: LookupIdentifier() identifier StringLength must be greater than 0")
	}

	if token, ok := keywords[identifier]; ok {
		return token, nil
	}

	return IDENTIFIER, nil
}

var keywords = map[string]string{
	"str": STR,
	"num": NUM,
}

const (
	EOF   = "EOF"
	ERROR = "ERROR"

	NUMBER     = "NUMBER"
	STRING     = "STRING"
	IDENTIFIER = "IDENTIFIER"

	NUM = "NUM"
	STR = "STR"

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
	ARROW     = "ARROW"
	DOT       = "DOT"

	LPAREN  = "LPAREN"
	RPAREN  = "RPAREN"
	LSQUARE = "LSQUARE"
	RSQUARE = "RSQUARE"
	LBRACE  = "LBRACE"
	RBRACE  = "RBRACE"
)
