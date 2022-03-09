from lexer.token import *
from typing import List

class ParserException(Exception):
    def __init__(self, line_number : int, message : str):
        super().__init__(line_number,f"Line {line_number}: {message}")

class Node:
    def __init__(self, line_number, type) -> None:
        self.type = type
        self.line_number = line_number


class ErrorNode(Node):
    def __init__(self, line_number,) -> None:
        super().__init__(line_number, ERROR)

    def __str__(self) -> str:
        return "{ERROR}"

class ProgramNode(Node):
    def __init__(self, line_number, nodes : List[Node]) -> None:
        super().__init__(line_number, PROGRAM)
        self.nodes = nodes

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.nodes]) + "]"

class AssignNode(Node):
    def __init__(self, line_number, scope : str , identifier : str, expression : Node) -> None:
        super().__init__(line_number,ASSIGN)
        self.scope = scope
        self.identifier = identifier
        self.expression = expression

    def __str__(self) -> str:
        return "(" + self.scope + " " + self.identifier.__str__() + " = " + self.expression.__str__() + ")"

class InitialiseNode(Node):
    def __init__(self, line_number, scope : str, type : str, identifier : str, expression : Node, parameters : List[Node] = None) -> None:
        super().__init__(line_number,INITIALISE)
        self.scope = scope
        self.var_type = type
        self.identifier = identifier
        self.expression = expression
        self.parameters = parameters

    def __str__(self) -> str:
        return "(" + self.scope + " " + self.type + " " +  self.identifier + (("(" + ",".join([p.__str__() for p in self.parameters]) + ")") if self.parameters != None else "") + " = " + self.expression.__str__() + ")"

class ConditionNode(Node):
    def __init__(self, line_number, seperator : str, condition : Node) -> None:
        super().__init__(line_number,ConditionNode)
        self.seperator = seperator
        self.condition = condition

    def __str__(self) -> str:
        return "(" + self.seperator + " " + self.condition.__str__()  + ")"

class ConditionalNode(Node):
    def __init__(self, line_number, conditions : List[ConditionNode], consequence : ProgramNode) -> None:
        super().__init__(line_number,CONDITIONAL)
        self.conditions = conditions
        self.consequence = consequence

    def __str__(self) -> str:
        return  "(" + ",".join([condition.__str__() for condition in self.conditions]) + ")" + "\n\t => " + self.consequence.__str__() 

class IfNode(Node):
    def __init__(self, line_number, conditions : List[ConditionalNode]) -> None:
        super().__init__(line_number,IF)
        self.conditions = conditions

    def __str__(self) -> str:
        return "IF: \n =>" + "\n =>".join([condition.__str__() for condition in self.conditions]) + ")"

class WhileNode(Node):
    def __init__(self, line_number, conditional : ConditionalNode) -> None:
        super().__init__(line_number,WHILE)
        self.conditional = conditional

    def __str__(self) -> str:
        return "WHILE (" + self.conditional.__str__() + ")"

class ForNode(Node):
    def __init__(self, line_number, type : str, identifier : str, expression : Node ,consequence : ProgramNode) -> None:
        super().__init__(line_number,FOR)
        self.var_type = type
        self.identifier = identifier
        self.expression = expression
        self.consequence = consequence

    def __str__(self) -> str:
        return "FOR (" + self.var_type + " " + self.identifier + " => " + self.expression.__str__() + " { " + self.consequence.__str__() + " })"

class ReturnNode(Node):
    def __init__(self, line_number, expression) -> None:
        super().__init__(line_number,RETURN)
        self.expression = expression
    
    def __str__(self) -> str:
        return "RETURN " + self.expression.__str__()

class BreakNode(Node):
    def __init__(self, line_number) -> None:
        super().__init__(line_number,BREAK)
    
    def __str__(self) -> str:
        return "BREAK"


class BinaryOperationNode(Node):
    def __init__(self, line_number, left : Node, op : str, right : Node) -> None:
        super().__init__(line_number,BIN_OP)
        self.left = left
        self.op = op
        self.right = right

    def __str__(self) -> str:
        return "(" + self.left.__str__() + " " + self.op + " " + self.right.__str__() + ")"


class UnaryOperationNode(Node):
    def __init__(self, line_number, op : str, right : Node) -> None:
        super().__init__(line_number,UNARY_OP)
        self.op = op
        self.right = right

    def __str__(self) -> str:
        return self.op + self.right.__str__()


class AtomNode(Node):
    def __init__(self, line_number, type : str) -> None:
        super().__init__(line_number,type)

class InvokeNode(AtomNode):
    def __init__(self, line_number, identifier : Node, parameters : List[Node]) -> None:
        super().__init__(line_number,INVOKE)
        self.function_node = identifier
        self.parameters = parameters

    def __str__(self) -> str:
        return self.function_node.__str__() + "(" + ",".join([param.__str__() for param in self.parameters]) + ")"

class ArrayNode(AtomNode):
    def __init__(self, line_number, nodes : List[Node]) -> None:
        super().__init__(line_number,ARRAY)
        self.nodes = nodes

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.nodes]) + "]"

class IndexNode(AtomNode):
    def __init__(self, line_number, array : Node, index : Node) -> None:
        super().__init__(line_number,INDEX)
        self.array = array
        self.index = index

    def __str__(self) -> str:
        return self.array.__str__() + "[" + str(self.index) + "]"


class IdentifierNode(AtomNode):
    def __init__(self, line_number, identifier : str) -> None:
        super().__init__(line_number,IDENTIFIER)
        self.identifier = identifier

    def __str__(self) -> str:
        return self.identifier

class StringNode(AtomNode):
    def __init__(self, line_number, value : str) -> None:
        super().__init__(line_number,STRING) 
        self.value = value

    def __str__(self) -> str:
        return self.value

class NumberNode(AtomNode):
    def __init__(self, line_number, type : str , value : int or float) -> None:
        super().__init__(line_number,type)
        self.value = value

    def __str__(self) -> str: 
        return str(self.value)

class IntNode(NumberNode):
    def __init__(self, line_number, value : int) -> None:
        super().__init__(line_number,INT, value)

class FloatNode(NumberNode):
    def __init__(self, line_number, value : float) -> None:
        super().__init__(line_number,FLOAT, value)

class BoolNode(AtomNode):
    def __init__(self, line_number, value : int) -> None:
        super().__init__(line_number,BOOL)
        self.value = value

    def __str__(self) -> str:
        if self.value == 1:
            return "true"
        return "false" 

class ParameterNode(AtomNode):
    def __init__(self, line_number, var_type : str, identifier : str) -> None:
        super().__init__(line_number,PARAMETER)
        self.var_type = var_type
        self.identifier = identifier

    def __str__(self) -> str:
        return self.type + " : " + self.identifier

class FlagNode(Node):
    def __init__(self, line_number, option : str) -> None:
        super().__init__(line_number,FLAG)
        self.option = option

    def __str__(self) -> str:
        return "FLAG : " + self.option

class LoadNode(Node):
    def __init__(self, line_number, option : str) -> None:
        super().__init__(line_number,LOAD)
        self.option = option

    def __str__(self) -> str:
        return "LOAD : " + self.option

class AnonymousFunctionNode(Node):
    def __init__(self, line_number,  var_type : str, consequence : Node, parameters : List[Node] = None) -> None:
        super().__init__(line_number, ANONYMOUS)
        self.var_type = var_type
        self.consequence = consequence
        self.parameters = parameters

    def __str__(self) -> str:
        return "(" + self.var_type + (("(" + ",".join([p.__str__() for p in self.parameters]) + ")") if self.parameters != None else "") + " = " + self.consequence.__str__() + ")"