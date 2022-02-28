from lexer.token import *
from typing import List

class ParserException(Exception):
    pass

class Node:
    def __init__(self, type) -> None:
        self.type = type


class ErrorNode(Node):
    def __init__(self) -> None:
        super().__init__(ERROR)

    def __str__(self) -> str:
        return "{ERROR}"

class ProgramNode(Node):
    def __init__(self, nodes : List[Node]) -> None:
        super().__init__(PROGRAM)
        self.nodes = nodes

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.nodes]) + "]"

class AssignNode(Node):
    def __init__(self, scope : str , identifier : str, expression : Node) -> None:
        super().__init__(ASSIGN)
        self.scope = scope
        self.identifier = identifier
        self.expression = expression

    def __str__(self) -> str:
        return "(" + self.scope + " " + self.identifier.__str__() + " = " + self.expression.__str__() + ")"

class InitialiseNode(Node):
    def __init__(self, scope : str, type : str, identifier : str, expression : Node, parameters : List[Node] = None) -> None:
        super().__init__(INITIALISE)
        self.scope = scope
        self.var_type = type
        self.identifier = identifier
        self.expression = expression
        self.parameters = parameters

    def __str__(self) -> str:
        return "(" + self.scope + " " + self.type + " " +  self.identifier + (("(" + ",".join([p.__str__() for p in self.parameters]) + ")") if self.parameters != None else "") + " = " + self.expression.__str__() + ")"

class ConditionNode(Node):
    def __init__(self, seperator : str, condition : Node) -> None:
        super().__init__(ConditionNode)
        self.seperator = seperator
        self.condition = condition

    def __str__(self) -> str:
        return "(" + self.seperator + " " + self.condition.__str__()  + ")"

class ConditionalNode(Node):
    def __init__(self, conditions : List[ConditionNode], consequence : ProgramNode) -> None:
        super().__init__(CONDITIONAL)
        self.conditions = conditions
        self.consequence = consequence

    def __str__(self) -> str:
        return  "(" + ",".join([condition.__str__() for condition in self.conditions]) + ")" + "\n\t => " + self.consequence.__str__() 

class IfNode(Node):
    def __init__(self, conditions : List[ConditionalNode]) -> None:
        super().__init__(IF)
        self.conditions = conditions

    def __str__(self) -> str:
        return "IF: \n =>" + "\n =>".join([condition.__str__() for condition in self.conditions]) + ")"

class WhileNode(Node):
    def __init__(self, conditional : ConditionalNode) -> None:
        super().__init__(WHILE)
        self.conditional = conditional

    def __str__(self) -> str:
        return "WHILE (" + self.conditional.__str__() + ")"

class ForNode(Node):
    def __init__(self, type : str, identifier : str, expression : Node ,consequence : ProgramNode) -> None:
        super().__init__(FOR)
        self.var_type = type
        self.identifier = identifier
        self.expression = expression
        self.consequence = consequence

    def __str__(self) -> str:
        return "FOR (" + self.var_type + " " + self.identifier + " => " + self.expression.__str__() + " { " + self.consequence.__str__() + " })"

class ReturnNode(Node):
    def __init__(self, expression) -> None:
        super().__init__(RETURN)
        self.expression = expression
    
    def __str__(self) -> str:
        return "RETURN " + self.expression.__str__()

class BreakNode(Node):
    def __init__(self) -> None:
        super().__init__(BREAK)
    
    def __str__(self) -> str:
        return "BREAK"


class BinaryOperationNode(Node):
    def __init__(self, left : Node, op : str, right : Node) -> None:
        super().__init__(BIN_OP)
        self.left = left
        self.op = op
        self.right = right

    def __str__(self) -> str:
        return "(" + self.left.__str__() + " " + self.op + " " + self.right.__str__() + ")"


class UnaryOperationNode(Node):
    def __init__(self, op : str, right : Node) -> None:
        super().__init__(UNARY_OP)
        self.op = op
        self.right = right

    def __str__(self) -> str:
        return self.op + self.right.__str__()


class AtomNode(Node):
    def __init__(self, type : str) -> None:
        super().__init__(type)

class InvokeNode(AtomNode):
    def __init__(self, identifier : str, parameters : List[Node]) -> None:
        super().__init__(INVOKE)
        self.identifier = identifier
        self.parameters = parameters

    def __str__(self) -> str:
        return self.identifier + "(" + ",".join([param.__str__() for param in self.parameters]) + ")"

class ArrayNode(AtomNode):
    def __init__(self, nodes : List[Node]) -> None:
        super().__init__(ARRAY)
        self.nodes = nodes

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.nodes]) + "]"

class IndexNode(AtomNode):
    def __init__(self, array : Node, index : Node) -> None:
        super().__init__(INDEX)
        self.array = array
        self.index = index

    def __str__(self) -> str:
        return self.array.__str__() + "[" + str(self.index) + "]"


class IdentifierNode(AtomNode):
    def __init__(self, identifier : str) -> None:
        super().__init__(IDENTIFIER)
        self.identifier = identifier

    def __str__(self) -> str:
        return self.identifier

class StringNode(AtomNode):
    def __init__(self, value : str) -> None:
        super().__init__(STRING) 
        self.value = value

    def __str__(self) -> str:
        return self.value

class NumberNode(AtomNode):
    def __init__(self, type : str , value : int or float) -> None:
        super().__init__(type)
        self.value = value

    def __str__(self) -> str: 
        return str(self.value)

class IntNode(NumberNode):
    def __init__(self, value : int) -> None:
        super().__init__(INT, value)

class FloatNode(NumberNode):
    def __init__(self, value : float) -> None:
        super().__init__(FLOAT, value)

class BoolNode(AtomNode):
    def __init__(self, value : int) -> None:
        super().__init__(BOOL)
        self.value = value

    def __str__(self) -> str:
        if self.value == 1:
            return "true"
        return "false" 

class ParameterNode(AtomNode):
    def __init__(self, var_type : str, identifier : str) -> None:
        super().__init__(PARAMETER)
        self.var_type = var_type
        self.identifier = identifier

    def __str__(self) -> str:
        return self.type + " : " + self.identifier

class FlagNode(Node):
    def __init__(self, option : str) -> None:
        super().__init__(FLAG)
        self.option = option

    def __str__(self) -> str:
        return "FLAG : " + self.option

class LoadNode(Node):
    def __init__(self, option : str) -> None:
        super().__init__(LOAD)
        self.option = option

    def __str__(self) -> str:
        return "LOAD : " + self.option