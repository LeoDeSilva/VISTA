import random
import time

from lexer.token import *
from parse.nodes import *
from typing import List, Dict, Callable
from evaluator.objects import *

from parse.nodes import ProgramNode

class EvaluatorException(Exception):
    def __init__(self, lineNumber : int, message : str) -> None:
        super().__init__(f"Line: {lineNumber}: {message}")

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

class Return(Object):
    def __init__(self, expression) -> None:
        super().__init__(RETURN)
        self.expression = expression

    def __type__(self) -> str:
        return "return"

class BinaryOperation(Object):
    def __init__(self, left : Object, operation : str, right : Object) -> None:
        super().__init__(BIN_OP)
        self.left = left
        self.operation = operation
        self.right = right

class FunctionDeclaration(Object):
    def __init__(self, func_type : str, parameters : List[Node], consequence : ProgramNode) -> None:
        super().__init__(FUNCTION)
        self.func_type = func_type 
        self.parameters = parameters
        self.consequence = consequence

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

    def index(self,index : int, environment) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException(environment.lineNumber,"IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        return String(self.value[index]), None
    
    def replace(self, index : int, value : Object, environment) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException(environment.lineNumber,"IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        if value.type != STRING:
            return None, EvaluatorException(environment.lineNumber,"IndexError: Cannot assign type " + value.__type__() + " to string")
        # self.value[index] = value
        return String(self.value[:index] + value.value + self.value[index+1:]), None

    def binary_operation(self, right : Object, operation : str, environment) -> Object and Exception:
        if right.type != STRING: 
            return None, EvaluatorException(environment.lineNumber,"TypeError: Expected Type STRING Binary Operation, Got  : " + right.__str__())
        elif operation not in (ADD,EE,NE,LT,GT,LTE,GTE):
            return None, EvaluatorException(environment.lineNumber,"TypeError: Expected Operation ADD, Got : " + operation)

        value, err = binary_operation_wrapper(self.value, operation, right.value, environment)
        if err != None: return Null(), err

        return assign_type(value), None

class Int(Factor):
    def __init__(self, value: int) -> None:
        super().__init__(INT, value)

    def __type__(self) -> str:
        return "int"

    def binary_operation(self, right : Object, operation : str, environment) -> Object and Exception:
        if right.type not in (INT, FLOAT): 
            return None, EvaluatorException(environment.lineNumber,"TypeError: Expected Type INT or FLOAT Binary Operation, Got  : " + right.__str__())

        value, err = binary_operation_wrapper(self.value, operation, right.value, environment)
        if err != None: return Null(), err

        return assign_type(value), None


class Float(Factor):
    def __init__(self, value: float) -> None:
        super().__init__(FLOAT, value)

    def __type__(self) -> str:
        return "float"

    def binary_operation(self, right : Object, operation : str, environment) -> Object and Exception:
        if right.type not in (INT, FLOAT): 
            return None, EvaluatorException(environment.lineNumber,"TypeError: Expected Type INT or FLOAT Binary Operation, Got  : " + right.__str__())

        value, err = binary_operation_wrapper(self.value, operation, right.value, environment)
        if err != None: return Null(), err

        return assign_type(value), None

class Array(Factor):
    def __init__(self, expressions) -> None:
        super().__init__(ARRAY, expressions)

    def index(self,index : int, environment) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException(environment.lineNumber,"IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        return self.value[index], None
    
    def replace(self, index : int, value : Object, environment) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException(environment.lineNumber,"IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        # self.value[index] = value
        return Array(self.value[:index] + [value] + self.value[index+1:]), None

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.value]) + "]"

    def __type__(self) -> str:
        if len(self.value) == 0: return "[]"
        return "[]" + self.value[0].__type__()


# Environment

class Environment:
    def __init__(self, lineNumber, constants : Dict[str,Object], flags : Dict[str,bool], global_vars : Dict[str,Object], local_vars : Dict[str,Object], functions, externals) -> None:
        self.lineNumber = lineNumber
        self.flags = flags
        self.constants = constants
        self.globals = global_vars
        self.locals = local_vars
        self.functions = functions
        self.externals = externals

def new_environment(line_number) -> Environment: 
    import modules.standard_module as standard_module
    return Environment(
        lineNumber=line_number,
        flags={},
        constants = {
            "true":Boolean(1),
            "false":Boolean(0),
            "null":Null(),
        },
        global_vars={ },
        local_vars={},
        functions=standard_module.extract_methods(),
        externals={}
    )

# Helpers 

def binary_operation_wrapper(left, operation : str, right, environment) -> int or float or str and Exception:
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

    return None, EvaluatorException(environment.lineNumber,"UnexpectedOperationError: " + operation)

def return_base(obj : Object):
    if obj.type in (INT,STRING,FLOAT):
        return obj.value
    elif obj.type == ARRAY:
        return [return_base(node) for node in obj.value]
    elif obj.type == BOOL:
        return True if obj.value == 1 else False

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
