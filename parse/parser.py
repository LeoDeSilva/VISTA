from lexer.token import *
from parse.nodes import *
from typing import List

class Parser:
    def __init__(self, program_tokens : List[Token]) -> None:
        self.program_tokens = program_tokens
        self.token_position = 0
        self.current_token = self.program_tokens[self.token_position]
        self.line_number = 0

    def advance(self) -> Token:
        self.token_position += 1
        self.current_token = self.program_tokens[self.token_position]
        self.line_number = self.current_token.line_number

        return self.current_token

    def peek(self) -> Token:
        if self.token_position + 1 >= len(self.program_tokens):
            return Token(EOF, "", self.line_number)

        return self.program_tokens[self.token_position + 1]

    def parse_tokens(self) -> List[Node] and Exception:
        ast = []
        while self.current_token.type != EOF:
            parsed_node, err = self.parse_expression() 
            if err != None: return [], err

            if self.current_token.type not in (SEMICOLON, RBRACE): 
                return [], ParserException(self.current_token.line_number,"ParserError: Expected Semicolon : " + self.current_token.__str__())
            else: self.advance()

            ast.append(parsed_node)
        return ProgramNode(self.line_number,ast), None

    def parse_expression(self) -> Node and Exception:
        if self.current_token.type == IDENTIFIER and self.peek().type == EQ:
            return self.parse_assign_node(LOCAL, self.current_token)

        elif self.current_token.type == IDENTIFIER and self.peek().type == IDENTIFIER: # <TYPE> <ID>
            return self.parse_initialise_node(LOCAL)

        elif self.current_token.type == GLOBAL:
            self.advance()
            if self.current_token.type == IDENTIFIER and self.peek().type == IDENTIFIER: # <TYPE> <ID>
                return self.parse_initialise_node(GLOBAL)

            return self.parse_assign_node(GLOBAL, self.current_token)

        elif self.current_token.type == IF:
            return self.parse_if_node()

        elif self.current_token.type == FOR:
            return self.parse_for_node()

        elif self.current_token.type == RETURN:
            return self.parse_return_node()

        elif self.current_token.type == BREAK:
            return self.parse_break_node()

        elif self.current_token.type == WHILE:
            return self.parse_while_node()

        elif self.current_token.type == LOAD:
            return self.parse_load_node()

        return self.parse_pratt_expression(0) # 10, 10+10

    # Keyword Operations

    def parse_load_node(self) -> Node and Exception:
        if self.advance().type != IDENTIFIER:
            return None, ParserException(self.current_token.line_number, "SyntaxError: load statement, expected IDENTIFIER after load")

        identifier_literal = self.current_token.literal
        self.advance()
        return LoadNode(self.line_number,identifier_literal), None


    def parse_break_node(self) -> Node and Exception:
        self.advance()
        if self.current_token.type != SEMICOLON:
            return None, ParserException(self.current_token.line_number,"SyntaxError: break statement, expected SEMICOLON after keyword")

        return BreakNode(self.line_number), None

    def parse_return_node(self) -> Node and Exception:
        self.advance()

        if self.current_token.type == SEMICOLON:
            return ReturnNode(self.line_number,IdentifierNode("null")), None

        return_expr, err = self.parse_pratt_expression(0)
        return ReturnNode(self.line_number,return_expr), err

    def parse_while_node(self) -> Node and Exception:
        conditional, err = self.parse_conditional()
        return WhileNode(self.line_number,conditional), err

    # for ( type ID => expr ) { }
    def parse_for_node(self) -> Node and Exception:
        if self.advance().type != LPAREN: 
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected LPAREN after Condition")
        
        if self.advance().type != IDENTIFIER:
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected Type After LPAREN")

        identifier_type = self.current_token.literal

        if self.advance().type != IDENTIFIER:
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected Identifier After Type")

        identifier_literal = self.current_token.literal

        if self.advance().type != ARROW:
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected => After Identifier")

        self.advance()

        interable_expr, err = self.parse_pratt_expression(0)
        if err != None: return None, err

        if self.current_token.type != RPAREN:
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected RPAREN After Expression")

        if self.advance().type != LBRACE:
            return None, ParserException(self.current_token.line_number,"Parse_For: Expected LBRACE After Expression")

        self.advance()
        consequence, err = self.parse_consequence()

        return ForNode(self.line_number,identifier_type, identifier_literal, interable_expr, ProgramNode(self.line_number,consequence)), err

    def parse_if_node(self) -> Node and Exception:
        conditions = []
        while self.current_token.type in (IF,ELIF,ELSE):
            if self.current_token.type in (IF, ELIF):
                # Parse (10==10) { } => the conditoin part that remains across if or elif
                condition, err = self.parse_conditional()
                if err != None: return None, err
                conditions.append(condition)
            else:
                # since else has no conditon : always true
                if self.advance().type != LBRACE: return None, ParserException(self.current_token.line_number,"Parse_Else: Expected LBRACE")
                self.advance()
                consequence, err = self.parse_consequence()
                if err != None: return ErrorNode, err
                conditions.append(ConditionalNode(self.line_number,[ConditionNode(self.line_number,AND, BoolNode(self.line_number,1))], ProgramNode(self.line_number,consequence)))

            if self.peek().type in (ELSE, IF, ELIF): self.advance()

        return IfNode(self.line_number,conditions), None

    def parse_assign_node(self, scope : str, identifier : Node) -> Node and Exception:
        if self.advance().type != EQ: return None, ParserException(self.current_token.line_number,"SyntaxError: Expected = After Assign Indentifier : " + identifier)
        self.advance()
        assign_expr, err = self.parse_pratt_expression(0)
        return AssignNode(self.line_number,scope, identifier, assign_expr), err

    def parse_initialise_node(self, scope : str) -> Node and Exception:
        initialise_type = self.current_token.literal
        if self.advance().type != IDENTIFIER: 
            return None, ParserException(self.current_token.line_number,"Parse_Init(): Expected Identifier In Initialisation")

        initialise_literal = self.current_token.literal
        if self.advance().type != EQ:
            # If LPAREN, parse a function defenition
            if self.current_token.type == LPAREN:
                return self.parse_declaration(initialise_type, initialise_literal)
            return None, ParserException(self.current_token.line_number,"Parse_Init(): Expected EQ After Identifier")

        self.advance()
        initialise_expr, err = self.parse_pratt_expression(0)
        return InitialiseNode(self.line_number,scope, initialise_type, initialise_literal, initialise_expr), err

    # Function defenition : TYPE ID (TYPE ID, TYPE ID) { ... }
    def parse_declaration(self, node_type : str, identifier : str) -> Node and Exception:
        self.advance()
        params, err = self.parse_params()
        if err != None: return None, err

        if self.advance().type != LBRACE: return None, ParserException(self.current_token.line_number,"SyntaxError: Expected { After Function Declaration")
        self.advance()

        consequence, err = self.parse_consequence()
        if err != None: return ErrorNode, err

        return InitialiseNode(self.line_number,LOCAL, node_type, identifier, ProgramNode(self.line_number,consequence), params), None

    # ( type ID , type ID )
    def parse_params(self) -> List[Node] and Exception:
        parameters = []

        while self.current_token.type != RPAREN:
            if self.current_token.type != IDENTIFIER: return None, ParserException(self.current_token.line_number,"SyntaxError: Expected Type Before Identifier : " + self.current_token.literal)
            param_type = self.current_token.literal

            if self.advance().type != IDENTIFIER: return None, ParserException(self.current_token.line_number,"SyntaxError: Expected Identifier After Type : " + self.current_token.literal)
            param_identifier = self.current_token.literal

            param = ParameterNode(self.line_number,param_type, param_identifier)
            parameters.append(param)

            if self.advance().type != COMMA: 
                if self.current_token.type == RPAREN:
                    return parameters, None
                return None, ParserException(self.current_token.line_number,"SyntaxError: Expected Comma After Parameter : " + param.__str__())

            self.advance()

        return parameters, None

    def parse_consequence(self) -> List[Node] and Exception:
        consequence = []
        while self.current_token.type != RBRACE:
            node, err = self.parse_expression() 
            if err != None: return [], err

            if self.current_token.type not in (SEMICOLON, RBRACE): 
                return [], ParserException(self.current_token.line_number,"ParserError: Expected Semicolon : " + self.current_token.__str__())
            else: self.advance()
            consequence.append(node)
        return consequence, None

    def parse_conditional(self) -> Node and Exception:
        if self.advance().type != LPAREN: return None, ParserException(self.current_token.line_number,"Parse_Conditional: Expected LPAREN after IF")
        self.advance()

        conditions = []

        # Initial expression will always be AND
        expr, err = self.parse_pratt_expression(0)
        if err != None: return ErrorNode, err
        conditions.append(ConditionNode(self.line_number,AND, expr))

        while self.current_token.type in (AND, OR): 
            seperator = self.current_token.type
            self.advance()
            expr, err = self.parse_pratt_expression(0)
            if err != None: return ErrorNode, err
            conditions.append(ConditionNode(self.line_number, seperator, expr))

        if self.current_token.type != RPAREN: return None, ParserException(self.current_token.line_number,"Parse_Conditional: Expected RPAREN after Condition")

        if self.advance().type != LBRACE: return None, ParserException(self.current_token.line_number,"Parse_Conditional: Expected LBRACE After Condition")
        self.advance()

        consequence, err = self.parse_consequence()
        if err != None: return None, err
        return ConditionalNode(self.line_number,conditions, ProgramNode(self.line_number,consequence)), None


    # Arithmatic Expressions

    def parse_pratt_expression(self, rbp : int) -> Node and Exception:
        left, err = self.parse_prefix()
        if err != None: return None, err
        peek_rbp = self.preference(self.current_token.type)

        # While the operation power is larger, parse this experssion
        while self.peek().type != EOF and peek_rbp >= rbp:
            left, err = self.parse_infix(left, self.current_token.type)
            if err != None: return None, err
            peek_rbp = self.preference(self.current_token.type)

        return left, None

    def parse_prefix(self) -> Node and Exception:
        if self.current_token.type in (NOT, SUB):
            return self.parse_unary()

        elif self.current_token.type == STRING:
            value = self.current_token.literal
            self.advance()
            return StringNode(self.line_number,value), None

        elif self.current_token.type == INT:
            value = int(self.current_token.literal)
            self.advance()
            return IntNode(self.line_number,value), None

        elif self.current_token.type == FLOAT:
            value = float(self.current_token.literal)
            self.advance()
            return FloatNode(self.line_number,value), None

        elif self.current_token.type == LPAREN:
            self.advance()
            expression, err = self.parse_pratt_expression(self.preference(LPAREN))
            if err != None: return None,err
            self.advance()
            return expression, None

        elif self.current_token.type == LSQUARE:
            nodes, err = self.parse_list(RSQUARE)
            if err != None: return None, err
            self.advance()
            return self.parse_postfix(ArrayNode(self.line_number, nodes))

        elif self.current_token.type == IDENTIFIER:
            if self.peek().type == ARROW:
                return_type = self.current_token.literal
                self.advance()
                if self.advance().type != LPAREN:
                    return None, ParserException(self.current_token.line_number, "SyntaxError: Anonymous Function, Expected ( After =>")

                self.advance()
                params, err = self.parse_params()
                if err != None: return None, err

                if self.advance().type != LBRACE: 
                    return None, ParserException(self.current_token.line_number,"SyntaxError: Expected { After Function Declaration")
                self.advance()

                consequence, err = self.parse_consequence()
                if err != None: return ErrorNode, err

                self.advance()
                return self.parse_postfix(AnonymousFunctionNode(self.line_number, return_type, ProgramNode(self.line_number,consequence), params))


            identifier = self.current_token.literal
            identifier_node = IdentifierNode(self.line_number,identifier)
            self.advance()
            return self.parse_postfix(identifier_node)

        return None, ParserException(self.current_token.line_number,"SyntaxError: parse_prefix() unsupported prefix: " + self.current_token.literal)

    def parse_unary(self) -> Node and Exception:
        operation = self.current_token.type
        self.advance()
        expression, err = self.parse_prefix()
        if err != None: return None,err
        return UnaryOperationNode(self.line_number,operation, expression), None

    def parse_postfix(self, node : Node) -> Node and Exception:
        if self.current_token.type == LSQUARE:
            self.advance()
            expr, err = self.parse_pratt_expression(0)
            if err != None: return None, err
            if self.current_token.type != RSQUARE:
                return None,ParserException(self.current_token.line_number,"SyntaxError: Expected closing RPAREN after indexing array, " + node.__str__() + "[" + expr.__str__())
            self.advance()

            if self.current_token.type == EQ:
                self.advance()
                expression, err = self.parse_pratt_expression(0)
                if err != None: return None, err
                return AssignNode(self.line_number,NULL, IndexNode(self.line_number,node,expr), expression), None

            return self.parse_postfix(IndexNode(self.line_number,node, expr))

        if self.current_token.type == LPAREN:
            params, err = self.parse_list(RPAREN)
            if err != None: return None, err
            self.advance()
            return self.parse_postfix(InvokeNode(self.line_number,node, params))

        return node, None

    def parse_infix(self, left : Node, operation : str) -> Node and Exception:
        if operation not in [EE,NE,LT,LTE,GT,GTE,ADD,SUB,MUL,DIV,MOD,POW]:
            return None, ParserException(self.current_token.line_number,"SyntaxError: parse_infix() unsupported operator: " + operation)

        self.advance()
        right, err = self.parse_pratt_expression(self.preference(operation) + 1)
        if err != None: return None, err
        return BinaryOperationNode(self.line_number,left,operation,right), None

    def parse_list(self, terminate : str) -> List[Node] and Exception:
        parameters = []
        self.advance()
        if self.current_token.type == terminate: return parameters, None
        while self.current_token.type != terminate:
            # Parse Expression and make sure COMMA after expression
            if self.current_token.type == EOF: 
                return None, ParserException(self.current_token.line_number,"SyntaxError: Unclosed parenthasis: " + terminate)

            param, err = self.parse_pratt_expression(0)
            if err != None: return None, err
            parameters.append(param)

            if self.current_token.type != COMMA: 
                if self.current_token.type == terminate: 
                    # Return if end of list
                    return parameters, None
                return None, ParserException(self.current_token.line_number,"SyntaxError: Expected Comma After Parameter : " + param.__str__())
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

