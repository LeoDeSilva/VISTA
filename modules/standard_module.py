from evaluator.objects import *
from evaluator.evaluator import eval
from parse.nodes import *
from lexer.token import *

def handle_range(node , environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) == 0 or len(node.parameters) > 3:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: range, expected between 1 and 3 parameters")
        
    start = 0
    stop = 0
    step = 1

    if len(node.parameters) == 1:
        if node.parameters[0].__type__() != "int":
            return None, None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[0].value
    elif len(node.parameters) > 1:
        if node.parameters[0].__type__() != "int":
            return None,None,  EvaluatorException(environment.lineNumber,"InvokeFunctionError: range, expected parameter 2 to be type INT, got: " + node.parameters[0].__type__())
        start = node.parameters[0].value

        if node.parameters[1].__type__() != "int":
            return None, None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: range, expected parameter 1 to be type INT, got: " + node.parameters[0].__type__())
        stop = node.parameters[1].value

    if len(node.parameters) >= 3:
        if node.parameters[2].__type__() != "int":
            return None, None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: range, expected parameter 3 to be type INT, got: " + node.parameters[0].__type__())
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
        return None, None, EvaluatorException(environment.lineNumber,"IntInputError: Input Type Not Type INT, got: " + user_input)

def handle_input(node : InvokeNode, environment : Environment) -> Object and Exception:
    string = params_to_string(node.parameters)
    user_input = input(string)
    return assign_type(user_input), environment, None

def handle_rnd(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) == 0 or len(node.parameters) > 2:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeRndError: Expected parameter length between 1 and 2, got: " + str(len(node.parameters)))

    min = 0
    max = 0
    if len(node.parameters) == 1:
        if node.parameters[0].__type__() != "int":
            return None, None, EvaluatorException(environment.lineNumber,"InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        max = node.parameters[0].value
    else:
        if node.parameters[0].__type__() != "int":
            return None, None,EvaluatorException(environment.lineNumber,"InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        min = node.parameters[0].value

        if node.parameters[1].__type__() != "int":
            return None, None, EvaluatorException(environment.lineNumber,"InvokeRndError: Parameter 0 expected type INT, got: " + node.parameters[0].__str__())
        max = node.parameters[1].value

    return assign_type(random.randint(min,max)), environment, None

def handle_sleep(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException(environment.lineNumber,"SleepError: Expected parameter length 1, got: " + str(len(node.parameters)))

    if node.parameters[0].__type__() not in ("int", "float"):
        return None, None, EvaluatorException(environment.lineNumber,"SleepError: Parameter 0 expected type INT or FLOAT, got: " + node.parameters[0].__str__())
    sleep_value = node.parameters[0].value

    time.sleep(sleep_value)
    
    return Null(), environment, None


def handle_round(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeRoundError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].__type__() not in ("float", "int"):
        return None, None, EvaluatorException(environment.lineNumber,"InvokeRoundError: Expected parameter 1 type INT or FLOAT, got: " + node.parameters[0].__type__())

    if node.parameters[1].__type__() != "int":
        return None, None, EvaluatorException(environment.lineNumber,"InvokeRoundError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())
    
    return assign_type(round(node.parameters[0].value, node.parameters[1].value)), environment, None


def handle_length(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeLengthError: Expected parameter length 1, got: " + str(len(node.parameters)))

    value = node.parameters[0]

    if value.type not in (STRING, ARRAY):
        return None, None, EvaluatorException(environment.lineNumber,"InvokeLengthError: Expected parameter 1 type ARRAY or STRING, got:" + value.__str__())
    
    return assign_type(len(value.value)), environment, None


# List methods

def handle_append(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    return Array(node.parameters[0].value + [node.parameters[1]]), environment, None

def handle_remove(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 2:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter length 2, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    if node.parameters[1].type != INT:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())  

    index = node.parameters[1].value 
    array = node.parameters[0].value

    return Array(array[:index] + array[index + 1:]), environment, None

def handle_insert(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 3:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter length 3, got: " + str(len(node.parameters)))

    if node.parameters[0].type != ARRAY:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter 1 type ARRAY, got: " + node.parameters[0].__type__())  

    if node.parameters[1].type != INT:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeAppendError: Expected parameter 1 type INT, got: " + node.parameters[0].__type__())  

    index = node.parameters[1].value 
    array = node.parameters[0].value

    return Array(array[:index] + [node.parameters[2]] +  array[index:]), environment, None

# Type checks

def handle_float(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeFloatError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(float(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeFloatError: Cannot Convert Type: " + node.parameters[0].__type__() + " to float")

def handle_int(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeIntError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(int(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeIntError: Cannot Convert Type: " + node.parameters[0].__type__() + " to int")

def handle_string(node : InvokeNode, environment : Environment) -> Object and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeStringError: Expected parameter length 1, got: " + str(len(node.parameters)))

    try:
        return assign_type(str(node.parameters[0].value)), environment, None
    except:
        return None, None, EvaluatorException(environment.lineNumber,"InvokeStringError: Cannot Convert Type: " + node.parameters[0].__type__() + " to string")

def extract_methods():
    return {
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
    }