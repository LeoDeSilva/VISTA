from lexer.token import *
from parse.nodes import *
from typing import List, Dict, Callable
from evaluator.objects import *

from parse.nodes import ProgramNode

#TODO: Construct types from expressions
#Structs will return their name for __type__()

class EvaluatorException(Exception):
    pass

class Object:
    def __init__(self, type : str) -> None:
        self.type = type

    def __str__(self) -> str:
        return self.type

class Null(Object):
    def __init__(self) -> None:
        super().__init__(NULL)

    def __type__(self) -> str:
        return "null"


class BinaryOperation(Object):
    def __init__(self, left : Object, operation : str, right : Object) -> None:
        super().__init__(BIN_OP)
        self.left = left
        self.operation = operation
        self.right = right

class FunctionDeclaration(Object):
    def __init__(self, type : str, parameters : List[Node], consequence : ProgramNode) -> None:
        super().__init__(FUNCTION)

    def __type__(self) -> str:
        return self.type

class Factor(Object):
    def __init__(self, type: str, value) -> None:
        super().__init__(type)
        self.value = value

    def __str__(self) -> str: 
        return str(self.value)

class Boolean(Factor):
    def __init__(self, value : int) -> None:
        super().__init__(BOOL, value)

    def __type__(self) -> str:
        return "bool"

    def __str__(self) -> str:
        return "true" if self.value == 1 else "false"

class String(Factor):
    def __init__(self, value : str) -> None:
        super().__init__(STRING, value)

    def __type__(self) -> str:
        return "string"

    def binary_operation(self, right : Object, operation : str) -> Object and Exception:
        if right.type != STRING: 
            return None, EvaluatorException("TypeError: Expected Type STRING Binary Operation, Got  : " + right.__str__())
        elif operation not in (ADD,EE,NE,LT,GT,LTE,GTE):
            return None, EvaluatorException("TypeError: Expected Operation ADD, Got : " + operation)

        value, err = binary_operation_wrapper(self.value, operation, right.value)
        if err != None: return Null(), err

        return assign_type(value), None

class Int(Factor):
    def __init__(self, value: int) -> None:
        super().__init__(INT, value)

    def __type__(self) -> str:
        return "int"

    def binary_operation(self, right : Object, operation : str) -> Object and Exception:
        if right.type not in (INT, FLOAT): 
            return None, EvaluatorException("TypeError: Expected Type INT or FLOAT Binary Operation, Got  : " + right.__str__())

        value, err = binary_operation_wrapper(self.value, operation, right.value)
        if err != None: return Null(), err

        return assign_type(value), None


class Float(Factor):
    def __init__(self, value: float) -> None:
        super().__init__(FLOAT, value)

    def __type__(self) -> str:
        return "float"

    def binary_operation(self, right : Object, operation : str) -> Object and Exception:
        if right.type not in (INT, FLOAT): 
            return None, EvaluatorException("TypeError: Expected Type INT or FLOAT Binary Operation, Got  : " + right.__str__())

        value, err = binary_operation_wrapper(self.value, operation, right.value)
        if err != None: return Null(), err

        return assign_type(value), None

class Array(Factor):
    def __init__(self, expressions) -> None:
        super().__init__(ARRAY, expressions)
    
    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.value]) + "]"

    def __type__(self) -> str:
        if len(self.value) == 0: return "[]"
        return "[]" + self.value[0].__type__()


# Environment

class Environment:
    def __init__(self, flags : Dict[str,bool], global_vars : Dict[str,Object], local_vars : Dict[str,Object], functions) -> None:
        self.flags = flags
        self.globals = global_vars
        self.locals = local_vars
        self.functions = functions

def new_environment() -> Environment: 
    return Environment(
        flags={},
        global_vars={
            "true":Boolean(1),
            "false":Boolean(0),
        },
        local_vars={},
        functions={
            "range":handle_range,
            "print":handle_print,
        },
    )

# Helpers 

def binary_operation_wrapper(left, operation : str, right) -> int or float or str and Exception:
    if operation == ADD:
        return left + right, None
    elif operation == SUB:
        return left - right, None
    elif operation == DIV:
        return left / right, None
    elif operation == MUL:
        return left * right, None
    elif operation == POW:
        return left ^ right, None
    elif operation == MOD:
        return left % right, None

    elif operation == EE:
        return left == right, None
    elif operation == NE:
        return left != right, None
    elif operation == LT:
        return left < right, None
    elif operation == LTE:
        return left <= right, None
    elif operation == GT:
        return left > right, None
    elif operation == GTE:
        return left >= right, None

    return None, EvaluatorException("UnexpectedOperationError: " + operation)

def assign_type(value) -> Object:
    if isinstance(value, int):
        return Int(value)
    elif isinstance(value, float):
        return Float(value)
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, bool):
        return Boolean(1 if value == True else 0)
    elif isinstance(value, list):
        return Array([assign_type(node) for node in value])

# FUNCTIONS

def handle_range(node , environment : Environment) -> Object and Exception:
    if len(node.parameters) == 0 or len(node.parameters) > 3:
        return None, EvaluatorException("InvokeFunctionError: range, expected between 1 and 3 parameters")
        
    start = 0
    stop = 0
    step = 1

    if len(node.parameters) == 1:
        if node.parameters[0].__type__() != "int":
            return None, EvaluatorException("InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[0].value
    elif len(node.parameters) > 1:
        if node.parameters[0].__type__() != "int":
            return None, EvaluatorException("InvokeFunctionError: range, expected parameter 2 to be type INT, got: " + node.parameters[0].__type__())
        start = node.parameters[0].value

        if node.parameters[1].__type__() != "int":
            return None, EvaluatorException("InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[1].value

    if len(node.parameters) >= 3:
        if node.parameters[2].__type__() != "int":
            return None, EvaluatorException("InvokeFunctionError: range, expected parameter 3 to be type INT, got: " + node.parameters[0].__type__())
        step = node.parameters[2].value

    return assign_type(list(range(start, stop, step))), None

def params_to_string(params : List[Object]) -> str:
    return " ".join([param.__str__() for param in params])
    


def handle_print(node : InvokeNode, environment : Environment) -> Object and Exception:
    print(params_to_string(node.parameters))
    return Null(), None
