from lexer.token import *
from parse.nodes import *
from typing import List

class Parser:
    def __init__(self, tokens : List[Token]) -> None:
        self.tokens = tokens
        self.position = 0
        self.token = self.tokens[self.position]

    def advance(self, inc : int = 1) -> Token:
        self.position += inc
        self.token = self.tokens[self.position]
        return self.token

    def peek(self) -> Token:
        if self.position + 1 >= len(self.tokens):
            return Token(EOF, "")
        return self.tokens[self.position + 1]

    def parse(self) -> List[Node] and Exception:
        ast = []
        while self.token.type != EOF:
            node, err = self.parse_expression() 
            if err != None: return [], err

            if self.token.type != SEMICOLON and self.token.type != RBRACE: 
                return [], ParserException("ParserError: Expected Semicolon : " + self.token.literal)
            else: self.advance()

            ast.append(node)
        return ast, None

    def parse_expression(self) -> Node and Exception:
        if self.token.type == IDENTIFIER and self.peek().type == EQ:
            return self.parse_assign()

        elif self.token.type == GLOBAL:
            self.advance()
            return self.parse_init(GLOBAL)

        elif self.token.type == TYPE:
            return self.parse_init(LOCAL)

        elif self.token.type == IF:
            return self.parse_if()

        expr, err = self.parse_expr(0)
        if err != None: return ErrorNode(), err
        return expr, None

    def parse_consequence(self) -> List[Node] and Exception:
        consequence = []
        while self.token.type != RBRACE:
            node, err = self.parse_expression() 
            if err != None: return [], err

            print(self.token.type)
            if self.token.type != SEMICOLON and self.token.type != RBRACE: 
                return [], ParserException("ParserError: Expected Semicolon : " + self.token.__str__())
            else: self.advance()
            consequence.append(node)
        return consequence, None
        
    def parse_conditional(self) -> Node and Exception:
        if self.advance().type != LPAREN: return ErrorNode(), ParserException("Parse_Conditional: Expected LPAREN after IF")
        self.advance()

        conditions = []

        expr, err = self.parse_expr(0)
        if err != None: return ErrorNode, err
        conditions.append(Condition(AND, expr))

        while self.token.type in (AND, OR): 
            seperator = self.token.type
            self.advance()
            expr, err = self.parse_expr(0)
            if err != None: return ErrorNode, err
            conditions.append(Condition(seperator, expr))

        if self.token.type != RPAREN: return ErrorNode(), ParserException("Parse_Conditional: Expected RPAREN after Condition")

        if self.advance().type != LBRACE: return ErrorNode(), ParserException("Parse_Conditional: Expected LBRACE After Condition")
        self.advance()

        consequence, err = self.parse_consequence()
        if err != None: return ErrorNode(), err
        return Conditional(conditions, ProgramNode(consequence)), None

    def parse_if(self) -> Node and Exception:
        conditions = []
        while self.token.type in (IF,ELIF,ELSE):
            if self.token.type in (IF, ELIF):
                condition, err = self.parse_conditional()
                if err != None: return ErrorNode(), err
                conditions.append(condition)
            else:
                if self.advance().type != LBRACE: return ErrorNode(), ParserException("Parse_Else: Expected LBRACE")
                self.advance()
                consequence, err = self.parse_consequence()
                if err != None: return ErrorNode, err
                conditions.append(Conditional([BoolNode(1)], ProgramNode(consequence)))

            if self.peek().type in (ELSE, IF, ELIF): self.advance()

        print(self.token.type)
        return IfNode(conditions), None


    def parse_assign(self) -> Node and Exception:
        identifier = self.token.literal
        self.advance(2)
        expr, err = self.parse_expr(0)
        return AssignNode(identifier, expr), err

    def parse_init(self, scope : str) -> Node and Exception:
        node_type = self.token
        if self.advance().type != IDENTIFIER: 
            return ErrorNode(), ParserException("Parse_Init(): Expected Identifier In Initialisation")

        identifier = self.token.literal
        if self.advance().type != EQ:
            return ErrorNode(), ParserException("Parse_Init(): Expected EQ After Identifier")

        self.advance()
        expr, err = self.parse_expr(0)
        return InitialiseNode(scope, node_type, identifier, expr), err

    # Arithmatic Expressions

    def parse_expr(self, rbp : int) -> Node and Exception:
        left, err = self.parse_prefix()
        if err != None: return ErrorNode(), err
        peek_rbp = self.preference(self.token.type)
        while self.peek().type != EOF and peek_rbp >= rbp:
            left, err = self.parse_infix(left, self.token.type)
            if err != None: return ErrorNode(), err
            peek_rbp = self.preference(self.token.type)
        return left, None

    def parse_prefix(self) -> Node and Exception:
        if self.token.type in (NOT, SUB):
            return self.parse_unary()

        elif self.token.type == STRING:
            value = self.token.literal
            self.advance()
            return StringNode(value), None

        elif self.token.type == INT:
            value = int(self.token.literal)
            self.advance()
            return IntNode(value), None

        elif self.token.type == FLOAT:
            value = float(self.token.literal)
            self.advance()
            return FloatNode(value), None

        elif self.token.type == TRUE:
            self.advance()
            return BoolNode(1), None

        elif self.token.type == FALSE:
            self.advance()
            return BoolNode(0), None

        elif self.token.type == LPAREN:
            self.advance()
            expression, err = self.parse_expr(self.preference(LPAREN))
            if err != None: return ErrorNode(),err
            self.advance()
            return expression, None

        elif self.token.type == LSQUARE:
            nodes, err = self.parse_list(RSQUARE)
            if err != None: return ErrorNode(), err
            self.advance()
            return self.parse_postfix(ArrayNode(nodes))

        elif self.token.type == IDENTIFIER:
            identifier = self.token.literal
            node = IdentifierNode(identifier)
            self.advance()
            if self.token.type == LPAREN:
                params, err = self.parse_list(RPAREN)
                if err != None: return ErrorNode(), err
                self.advance()
                return self.parse_postfix(InvokeNode(identifier, params))
            return self.parse_postfix(node)

        return ErrorNode(), ParserException("SyntaxError: parse_prefix() unsupported prefix: " + self.token.literal)

    def parse_unary(self) -> Node and Exception:
        operation = self.token.type
        self.advance()
        expression, err = self.parse_prefix()
        if err != None: return ErrorNode(),err
        return UnaryOp(operation, expression), None

    def parse_postfix(self, node : Node) -> Node and Exception:
        return node, None

    def parse_infix(self, left : Node, operation : str) -> Node and Exception:
        if operation not in [EE,NE,LT,LTE,GT,GTE,ADD,SUB,MUL,DIV,MOD,POW]:
            return ErrorNode(), ParserException("SyntaxError: parse_infix() unsupported operator: " + operation)
        self.advance()
        right, err = self.parse_expr(self.preference(operation) + 1)
        if err != None: return ErrorNode(), err
        return BinaryOp(left,operation,right), None

    def parse_list(self, terminate : str) -> List[Node] and Exception:
        parameters = []
        self.advance()
        if self.token.type == RPAREN: return parameters, None
        while self.token.type != terminate:
            if self.token.type == EOF: return ErrorNode(), ParserException("SyntaxError: Unclosed parenthasis: " + terminate)

            elif self.token.type != COMMA:
                param, err = self.parse_expr(0)
                if err != None: return ErrorNode(), err
                parameters.append(param)
            else:
                self.advance()
        return parameters, None

    def parse_parameters(self, terminate) -> List[Node] and Exception:
        parameters = []
        return parameters, None

    def preference(self,type : str) -> int:
        preferences = {
            EE:10,
            NE:10,
            GT:10,
            LT:10,
            GTE:10,
            LTE:10,
            MOD:15,
            ADD:20,
            SUB:20,
            MUL:30,
            DIV:30,
            POW:40,
            LPAREN:0,
        }
        
        if type in preferences:
            return preferences[type]
        return -1

