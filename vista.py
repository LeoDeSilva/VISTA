import sys
from lexer.lexer import Lexer
from parse.parser import Parser
from evaluator.evaluator import eval, eval_program
from evaluator.objects import Environment, new_environment

def main():
    if len(sys.argv) < 2:
        print("Useage: main.py <filename>")
    else:
        with open(sys.argv[1]) as f:
            environment = new_environment(1)
            l = Lexer(f.read().strip())  
            tokens, err = l.lex_program()
            if err != None: raise(err)
            # [print(token) for token in tokens]

            p = Parser(tokens)
            ast, err = p.parse_tokens()
            if err != None: raise(err)
            # [print(node) for node in ast.nodes]

            result, _, err = eval_program(ast, environment)
            if err != None: raise(err)

if __name__ == "__main__":
    main()