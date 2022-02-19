import sys
from lexer.lexer import Lexer
from parse.parser import Parser

def main():
    if len(sys.argv) < 2:
        print("Useage: main.py <filename>")
    else:
        with open(sys.argv[1]) as f:
            l = Lexer(f.read().strip())  
            tokens, err = l.lex()
            if err != None: raise(err)

            p = Parser(tokens)
            ast, err = p.parse()
            if err != None: raise(err)
            [print(node) for node in ast]

if __name__ == "__main__":
    main()