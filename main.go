package main

import (
	"VISTA/lexer"
	"fmt"
	"os"
	"strings"
)

func run() error {
	filename := os.Args[1]
	file, err := os.ReadFile(filename)
	if err != nil {
		return err
	}
	formattedFile := string(file)

	l := lexer.NewLexer(strings.TrimSpace(formattedFile))
	tokens, err := l.Lex()
	if err != nil {
		return err
	}
	fmt.Println(tokens)
	return nil
}

func main() {
	if err := run(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
