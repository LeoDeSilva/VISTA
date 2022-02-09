import sys
from lexer.lexer import Lexer

def main():
    if len(sys.argv) < 2:
        print("Useage: main.py <filename>")
    else:
        with open(sys.argv[1]) as f:
            l = Lexer(f.read().strip())  
            tokens, err = l.lex()
            if err != None:
                raise(err)

            [print(tok) for tok in tokens]
if __name__ == "__main__":
    main()