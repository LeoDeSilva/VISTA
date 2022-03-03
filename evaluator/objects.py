import random
import time

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

    def index(self,index : int) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException("IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        return String(self.value[index]), None
    
    def replace(self, index : int, value : Object) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException("IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        if value.type != STRING:
            return None, EvaluatorException("IndexError: Cannot assign type " + value.__type__() + " to string")
        # self.value[index] = value
        return String(self.value[:index] + value.value + self.value[index+1:]), None

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

    def index(self,index : int) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException("IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        return self.value[index], None
    
    def replace(self, index : int, value : Object) -> Object and Exception:
        if index >= len(self.value):
            return None, EvaluatorException("IndexError: Index Out Of Range: " + str(index) + " Length: " + str(len(self.value) - 1))

        # self.value[index] = value
        return Array(self.value[:index] + [value] + self.value[index+1:]), None

    def __str__(self) -> str:
        return "[" + ",".join([node.__str__() for node in self.value]) + "]"

    def __type__(self) -> str:
        if len(self.value) == 0: return "[]"
        return "[]" + self.value[0].__type__()


# Environment

class Environment:
    def __init__(self, constants : Dict[str,Object], flags : Dict[str,bool], global_vars : Dict[str,Object], local_vars : Dict[str,Object], functions, externals) -> None:
        self.flags = flags
        self.constants = constants
        self.globals = global_vars
        self.locals = local_vars
        self.functions = functions
        self.externals = externals

def new_environment() -> Environment: 
    return Environment(
        flags={},
        constants = {
            "true":Boolean(1),
            "false":Boolean(0),
            "null":Null(),
        },
        global_vars={ },
        local_vars={},
        functions={
            "range":handle_range,
            "print":handle_print,
            "input":handle_input,
            "intInput":handle_int_input,
            "rnd":handle_rnd,
            "length":handle_length,

            "float":handle_float,
            "int":handle_int,
            "string":handle_string,

            "round":handle_round,
            "append":handle_append,
            "remove":handle_remove,
            "insert":handle_insert,

            "sleep": handle_sleep,
        },
        externals={}
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

# FUNCTIONS

def handle_range(node , environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) == 0 or len(node.parameters) > 3:
        return None, None, EvaluatorException("InvokeFunctionError: range, expected between 1 and 3 parameters")
        
    start = 0
    stop = 0
    step = 1

    if len(node.parameters) == 1:
        if node.parameters[0].__type__() != "int":
            return None, None, EvaluatorException("InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[0].value
    elif len(node.parameters) > 1:
        if node.parameters[0].__type__() != "int":
            return None,None,  EvaluatorException("InvokeFunctionError: range, expected parameter 2 to be type INT, got: " + node.parameters[0].__type__())
        start = node.parameters[0].value

        if node.parameters[1].__type__() != "int":
            return None, None, EvaluatorException("InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[1].value

    if len(node.parameters) >= 3:
        if node.parameters[2].__type__() != "int":
            return None, None, EvaluatorException("InvokeFunctionError: range, expected parameter 3 to be type INT, got: " + node.parameters[0].__type__())
        step = node.parameters[2].value

    return assign_type(list(range(start, stop, step))), environment, None

def params_to_string(params : List[Object]) -> str:
    return " ".join([param.__str__() for param in params])
    
def handle_print(node : InvokeNode, environment : Environment) -> Object and Exception:
    print(params_to_string(node.parameters))
    return Null(), environment, None

def handle_int_input(node : InvokeNode, environment : Environment) -> Object and Exception:
    string = params_to_string(node.parameters)
    user_input = input(string)
    try:
        return assign_type(int(user_input)), environment, None
    except ValueError:
        return None, None, EvaluatorException("IntInputError: Input Type Not Type INT, got: " + user_input)

def handle_input(node : InvokeNode, environment : Environment) -> Object and Exception:
    string = params_to_string(node.parameters)
    user_input = input(string)
    return assign_type(user_input), environment, None

def handle_rnd(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) == 0 or len(node.parameters) > 2:
        return None, None, EvaluatorException("InvokeRndError: Expected parameter length between 1 and 2, got: " + str(len(node.parameters)))

    min = 0
    max = 0
    if len(node.parameters) == 1:
        if node.parameters[0].__type__() != "int":
            return None, None, EvaluatorException("InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        max = node.parameters[0].value
    else:
        if node.parameters[0].__type__() != "int":
            return None, None,EvaluatorException("InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        min = node.parameters[0].value

        if node.parameters[1].__type__() != "int":
            return None, None, EvaluatorException("InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        max = node.parameters[1].value

    return assign_type(random.randint(min,max)), environment, None

def handle_sleep(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("SleepError: Expected parameter length 1, got: " + str(len(node.parameters)))

    if node.parameters[0].__type__() not in ("int", "float"):
        return None, None, EvaluatorException("SleepError: Parameter 0 expected type INT or FLOAT, got: " + node.parameters[0].__str__())
    sleep_value = node.parameters[0].value

    time.sleep(sleep_value)
    
    return Null(), environment, None


def handle_round(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException("InvokeRoundError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].__type__() not in ("float", "int"):
        return None, None, EvaluatorException("InvokeRoundError: Expected parameter 1 type INT or FLOAT, got: " + node.parameters[0].__type__())

    if node.parameters[1].__type__() != "int":
        return None, None, EvaluatorException("InvokeRoundError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())
    
    return assign_type(round(node.parameters[0].value, node.parameters[1].value)), environment, None


def handle_length(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("InvokeLengthError: Expected parameter length 1, got: " + str(len(node.parameters)))

    value = node.parameters[0]

    if value.type not in (STRING, ARRAY):
        return None, None, EvaluatorException("InvokeLengthError: Expected parameter 1 type ARRAY or STRING, got:" + value.__str__())
    
    return assign_type(len(value.value)), environment, None


# List methods

def handle_append(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    return Array(node.parameters[0].value + [node.parameters[1]]), environment, None

def handle_remove(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    if node.parameters[1].type != INT:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())  

    index = node.parameters[1].value 
    array = node.parameters[0].value

    return Array(array[:index] + array[index + 1:]), environment, None

def handle_insert(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 3:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter length 3, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    if node.parameters[1].type != INT:
        return None, None, EvaluatorException("InvokeAppendError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())  

    index = node.parameters[1].value 
    array = node.parameters[0].value

    return Array(array[:index] + [node.parameters[2]] +  array[index:]), environment, None

# Type checks

def handle_float(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("InvokeFloatError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(float(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException("InvokeFloatError: Cannot Convert Type: " + node.parameters[0].__type__() + " to float")

def handle_int(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("InvokeIntError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(int(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException("InvokeIntError: Cannot Convert Type: " + node.parameters[0].__type__() + " to int")

def handle_string(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("InvokeStringError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(str(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException("InvokeStringError: Cannot Convert Type: " + node.parameters[0].__type__() + " to string")

