from lexer.token import *
from parse.nodes import *
from typing import List

#THINK: instead of global keyword, outside function scope is used as global in functions, they can be modified : like pyyhon

class Parser:
    def __init__(self, tokens : List[Token]) -> None:
        self.tokens = tokens
        self.position = 0
        self.token = self.tokens[self.position]

    def advance(self, inc : int = 1, terminate : str = None) -> Token:
        if terminate != None:
            while self.token.type != terminate:
                self.advance()

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
                return [], ParserException("ParserError: Expected Semicolon : " + self.token.__str__())
            else: self.advance()

            ast.append(node)
        return ProgramNode(ast), None

    def parse_expression(self) -> Node and Exception:
        if self.token.type == IDENTIFIER and self.peek().type == EQ:
            return self.parse_assign(LOCAL)

        elif self.token.type == GLOBAL:
            self.advance()
            if self.token.type == IDENTIFIER and self.peek().type == IDENTIFIER:
                return self.parse_init(GLOBAL)
            return self.parse_assign(GLOBAL)

        elif self.token.type == IDENTIFIER and self.peek().type == IDENTIFIER:
            return self.parse_init(LOCAL)

        elif self.token.type == IF:
            return self.parse_if()

        elif self.token.type == FOR:
            return self.parse_for()

        elif self.token.type == RETURN:
            return self.parse_return()

        elif self.token.type == WHILE:
            return self.parse_while()

        elif self.token.type == NOT and self.peek().type == LSQUARE:
            return self.parse_flag()

        expr, err = self.parse_expr(0)
        if err != None: return None, err
        return expr, None

    # Keyword Operations

    def parse_flag(self) -> Node and Exception:
        if self.advance(2).type != IDENTIFIER: return None, ParserException("SyntaxError: FLAG Expected To Be Identifier")
        identifier = self.token.literal
        if self.advance().type != RSQUARE: return None, ParserException("SyntaxError: Expected ] After Flag : " + identifier)
        self.advance()
        return FlagNode(identifier), None

    def parse_return(self) -> Node and Exception:
        self.advance()
        expr, err = self.parse_expr(0)
        if err != None: return None, err
        return ReturnNode(expr), None

    def parse_while(self) -> Node and Exception:
        conditional, err = self.parse_conditional()
        return WhileNode(conditional), err

    # for ( type ID => expr ) { }
    def parse_for(self) -> Node and Exception:
        if self.advance().type != LPAREN: 
            return None, ParserException("Parse_For: Expected LPAREN after Condition")
        
        if self.advance().type != IDENTIFIER:
            return None, ParserException("Parse_For: Expected Type After LPAREN")

        identifier_type = self.token.literal

        if self.advance().type != IDENTIFIER:
            return None, ParserException("Parse_For: Expected Identifier After Type")

        identifier = self.token.literal

        if self.advance().type != ARROW:
            return None, ParserException("Parse_For: Expected => After Identifier")

        self.advance()

        expr, err = self.parse_expr(0)
        if err != None: return None, err

        if self.token.type != RPAREN:
            return None, ParserException("Parse_For: Expected RPAREN After Expression")

        if self.advance().type != LBRACE:
            return None, ParserException("Parse_For: Expected LBRACE After Expression")

        self.advance()
        consequence, err = self.parse_consequence()
        if err != None: return None, err

        return ForNode(identifier_type, identifier, expr, ProgramNode(consequence)), None

    def parse_if(self) -> Node and Exception:
        conditions = []
        while self.token.type in (IF,ELIF,ELSE):
            if self.token.type in (IF, ELIF):
                # Parse (10==10) { } => the conditoin part that remains across if or elif
                condition, err = self.parse_conditional()
                if err != None: return None, err
                conditions.append(condition)
            else:
                # since else has no conditon : always true
                if self.advance().type != LBRACE: return None, ParserException("Parse_Else: Expected LBRACE")
                self.advance()
                consequence, err = self.parse_consequence()
                if err != None: return ErrorNode, err
                conditions.append(ConditionalNode([ConditionNode(AND, BoolNode(1))], ProgramNode(consequence)))

            if self.peek().type in (ELSE, IF, ELIF): self.advance()

        return IfNode(conditions), None

    def parse_assign(self, scope : str) -> Node and Exception:
        identifier = self.token.literal
        if self.advance().type != EQ: return None, ParserException("SyntaxError: Expected = After Assign Indentifier : " + identifier)
        self.advance()
        expr, err = self.parse_expr(0)
        return AssignNode(scope, identifier, expr), err

    def parse_init(self, scope : str) -> Node and Exception:
        node_type = self.token.literal
        if self.advance().type != IDENTIFIER: 
            return None, ParserException("Parse_Init(): Expected Identifier In Initialisation")

        identifier = self.token.literal
        if self.advance().type != EQ:
            # If LPAREN, parse a function defenition
            if self.token.type == LPAREN:
                return self.parse_declaration(node_type, identifier)
            return None, ParserException("Parse_Init(): Expected EQ After Identifier")

        self.advance()
        expr, err = self.parse_expr(0)
        return InitialiseNode(scope, node_type, identifier, expr), err

    # Function defenition : TYPE ID (TYPE ID, TYPE ID) { ... }
    def parse_declaration(self, node_type : str, identifier : str) -> Node and Exception:
        self.advance()
        params, err = self.parse_params()
        if err != None: return None, err
        if self.advance().type != LBRACE: return None, ParserException("SyntaxError: Expected { After Function Declaration")
        self.advance()
        consequence, err = self.parse_consequence()
        if err != None: return ErrorNode, err
        return InitialiseNode(LOCAL, node_type, identifier, ProgramNode(consequence), params), None

    # ( type ID , type ID )
    def parse_params(self) -> List[Node] and Exception:
        parameters = []
        while self.token.type != RPAREN:
            if self.token.type != IDENTIFIER: return None, ParserException("SyntaxError: Expected Type Before Identifier : " + self.token.literal)
            param_type = self.token.literal

            if self.advance().type != IDENTIFIER: return None, ParserException("SyntaxError: Expected Identifier After Type : " + self.token.literal)
            param_identifier = self.token.literal

            param = ParameterNode(param_type, param_identifier)
            parameters.append(param)

            if self.advance().type != COMMA: 
                if self.token.type == RPAREN:
                    return parameters, None
                return None, ParserException("SyntaxError: Expected Comma After Parameter : " + param.__str__())
            self.advance()
        return parameters, None

    def parse_consequence(self) -> List[Node] and Exception:
        consequence = []
        while self.token.type != RBRACE:
            node, err = self.parse_expression() 
            if err != None: return [], err

            if self.token.type != SEMICOLON and self.token.type != RBRACE: 
                return [], ParserException("ParserError: Expected Semicolon : " + self.token.__str__())
            else: self.advance()
            consequence.append(node)
        return consequence, None

    def parse_conditional(self) -> Node and Exception:
        if self.advance().type != LPAREN: return None, ParserException("Parse_Conditional: Expected LPAREN after IF")
        self.advance()

        conditions = []

        # Initial expression will always be AND
        expr, err = self.parse_expr(0)
        if err != None: return ErrorNode, err
        conditions.append(ConditionNode(AND, expr))

        while self.token.type in (AND, OR): 
            seperator = self.token.type
            self.advance()
            expr, err = self.parse_expr(0)
            if err != None: return ErrorNode, err
            conditions.append(ConditionNode(seperator, expr))

        if self.token.type != RPAREN: return None, ParserException("Parse_Conditional: Expected RPAREN after Condition")

        if self.advance().type != LBRACE: return None, ParserException("Parse_Conditional: Expected LBRACE After Condition")
        self.advance()

        consequence, err = self.parse_consequence()
        if err != None: return None, err
        return ConditionalNode(conditions, ProgramNode(consequence)), None


    # Arithmatic Expressions

    def parse_expr(self, rbp : int) -> Node and Exception:
        left, err = self.parse_prefix()
        if err != None: return None, err
        peek_rbp = self.preference(self.token.type)

        # While the operation power is larger, parse this experssion
        while self.peek().type != EOF and peek_rbp >= rbp:
            left, err = self.parse_infix(left, self.token.type)
            if err != None: return None, err
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

        elif self.token.type == LPAREN:
            self.advance()
            expression, err = self.parse_expr(self.preference(LPAREN))
            if err != None: return None,err
            self.advance()
            return expression, None

        elif self.token.type == LSQUARE:
            nodes, err = self.parse_list(RSQUARE)
            if err != None: return None, err
            self.advance()
            return self.parse_postfix(ArrayNode(nodes))

        elif self.token.type == IDENTIFIER:
            identifier = self.token.literal
            node = IdentifierNode(identifier)
            self.advance()
            if self.token.type == LPAREN:
                params, err = self.parse_list(RPAREN)
                if err != None: return None, err
                self.advance()
                return self.parse_postfix(InvokeNode(identifier, params))
            return self.parse_postfix(node)

        return None, ParserException("SyntaxError: parse_prefix() unsupported prefix: " + self.token.literal)

    def parse_unary(self) -> Node and Exception:
        operation = self.token.type
        self.advance()
        expression, err = self.parse_prefix()
        if err != None: return None,err
        return UnaryOperationNode(operation, expression), None

    def parse_postfix(self, node : Node) -> Node and Exception:
        return node, None

    def parse_infix(self, left : Node, operation : str) -> Node and Exception:
        if operation not in [EE,NE,LT,LTE,GT,GTE,ADD,SUB,MUL,DIV,MOD,POW]:
            return None, ParserException("SyntaxError: parse_infix() unsupported operator: " + operation)

        self.advance()
        right, err = self.parse_expr(self.preference(operation) + 1)
        if err != None: return None, err
        return BinaryOperationNode(left,operation,right), None

    def parse_list(self, terminate : str) -> List[Node] and Exception:
        parameters = []
        self.advance()
        if self.token.type == terminate: return parameters, None
        while self.token.type != terminate:
            # Parse Expression and make sure COMMA after expression
            if self.token.type == EOF: 
                return None, ParserException("SyntaxError: Unclosed parenthasis: " + terminate)

            param, err = self.parse_expr(0)
            if err != None: return None, err
            parameters.append(param)

            if self.token.type != COMMA: 
                if self.token.type == terminate: 
                    # Return if end of list
                    return parameters, None
                return None, ParserException("SyntaxError: Expected Comma After Parameter : " + param.__str__())
            self.advance()

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

