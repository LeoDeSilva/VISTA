import sys
from lexer.lexer import Lexer

def main():
    if len(sys.argv) < 2:
        print("Useage: main.py <filename>")
    else:
        with open(sys.argv[1]) as f:
            l = Lexer(f.read())  
            l.lex()

if __name__ == "__main__":
    main()