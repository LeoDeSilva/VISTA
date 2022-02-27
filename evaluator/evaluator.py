from unittest import result
from evaluator.objects import *
from lexer.token import *
from parse.nodes import *

# Either return expression from eval(PROGRAM_NODE) or parse_program()

def eval(node : Node, environment : Environment) -> Object and Exception:
    if node.type == PROGRAM:
        return eval_program(node, environment)

    elif node.type == BIN_OP:
        return eval_binop(node, environment)
    elif node.type == UNARY_OP:
        return eval_unary(node, environment)

    elif node.type == INITIALISE:
        return eval_init(node, environment)
    elif node.type == ASSIGN:
        return eval_assign(node, environment)

    elif node.type == IDENTIFIER:
        return eval_identifier(node, environment)

    elif node.type == IF:
        return eval_if(node, environment)
    elif node.type == WHILE:
        return eval_while(node, environment)
    elif node.type == FOR:
        return eval_for(node, environment)
    elif node.type == INVOKE:
        return eval_invoke(node, environment)
    elif node.type == RETURN:
        return eval_return(node, environment)
        
    elif node.type == INT:
        return Int(node.value), None
    elif node.type == FLOAT:
        return Float(node.value), None
    elif node.type == STRING:
        return String(node.value), None
    elif node.type == ARRAY:
        return eval_array(node, environment)
    elif node.type == BOOL:
        return Boolean(node.value), None
    
    else:
        return None, EvaluatorException("UnexpectedNode: " + node.__str__())

def eval_return(returnnode : ReturnNode, environment : Environment) -> Object and Exception:
    expression, err = eval(returnnode.expression, environment)
    if err != None: return None, err
    return Return(expression), None

def eval_invoke(invoke : InvokeNode, environment : Environment) -> Object and Exception:
    parameters = []
    for param in invoke.parameters:
        param_expr, err = eval(param, environment)
        if err != None: return None, err
        parameters.append(param_expr)

    local_environment = new_environment()
    local_environment.globals = environment.locals

    if invoke.identifier in environment.functions:
        return environment.functions[invoke.identifier](InvokeNode(invoke.identifier, parameters),local_environment)

    if invoke.identifier in environment.locals:
        function = environment.locals[invoke.identifier]
    elif invoke.identifier in environment.globals:
        function = environment.globals[invoke.identifier]
    else:
        return None, EvaluatorException("InvokeFunctionError: Undefined Function: " + invoke.identifier)

    if function.type != FUNCTION:
        return None, EvaluatorException("InvokeFunctionError: Identifier: " + invoke.identifier + " Not type FUNCTION")
    for i,param_node in enumerate(function.parameters):
        if param_node.var_type != parameters[i].__type__():
            return None, EvaluatorException("InvokeFunctionError: Expected parameter " + str(i) + " type " + str(param_node.var_type) + " got: " + parameters[i].__type__())
        local_environment.locals[param_node.identifier] = parameters[i]
    result, err = eval(function.consequence, local_environment)
    if err != None: return None, err

    if result.type == RETURN:
        return result.expression, None
    elif result.__type__() != function.func_type:
        return None, EvaluatorException("InvokeFunctionError: Expected Return Type : " + function.func_type + " got: " + result.__type__())

    
    return result, None
        

def eval_for(fornode : ForNode, environment : Environment) -> Object and Exception:
    array, err = eval(fornode.expression, environment)
    if err != None: return None, err
    if array.type not in (ARRAY, STRING):
        return None, EvaluatorException("ForNodeError: Expected Expression Type ARRAY or STRING, got: " + array.__str__())
     
    i = 0
    while i < len(array.value):
        expr = array.value[i] if not isinstance(array.value[i],str) else assign_type(array.value[i])
        if expr.__type__() != fornode.var_type and expr.__type__() != "[]":
            return None, EvaluatorException("ForNodeError: Expected Node Type: " + fornode.var_type + " got: " + expr.__type__()) 
        
        environment.locals[fornode.identifier] = expr
        result, err = eval(fornode.consequence, environment)
        if err != None: return None, err
        if result.type == RETURN: return result, None
        i+=1
    
    return Null(), None


# e.g. and 10==10, evaluates to determine consequence
def eval_conditions(conditionals : ConditionNode, environment : Environment) -> bool and Exception:
    result = True
    for condition in conditionals:
        satisfied, err = eval(condition.condition, environment)
        if err != None: return None, err

        if condition.seperator == OR:
            result = result or satisfied.value == 1
        elif condition.seperator == AND:
            result = result and satisfied.value == 1

    return result, None

# e.g. elif (10 == 10 && 2 != 3) { print("Hello World"); }, indidual clauses of if statement
def eval_conditional(node : IfNode, environment : Environment) -> Object and Exception and bool:
    satisfied, err = eval_conditions(node.conditions, environment)
    if err != None: return None, err, False

    if satisfied:
        result, err = eval(node.consequence, environment)
        if err != None: return None, err, True
        if result.type == RETURN: return result, None, True
        return Null(), None, True

    return Null(), None, False

def eval_if(ifnode : IfNode, environment : Environment) -> Object and Exception:
    satisfied = False
    i = 0
    #Loop through all elif's untill one is satisfied
    while not satisfied and i < len(ifnode.conditions):
        result, err, satisfied= eval_conditional(ifnode.conditions[i], environment)
        if err != None: return None, err
        if result.type == RETURN: return result, None
        i += 1
    return Null(), None

def eval_while(whilenode : WhileNode, environment : Environment) -> Object and Exception:
    satisfied = True
    i = 0
    while satisfied:
        result, err, satisfied = eval_conditional(whilenode.conditional, environment)
        if err != None: return None, err
        if result.type == RETURN: return result, None
        i += 1
    return Null(), None

def eval_array(array : ArrayNode, environment : Environment) -> Object and Exception:
    if len(array.nodes) == 0: return Array([]), None
    exprs = []
    array_type = array.nodes[0].type
    for node in array.nodes:
        if node.type != array_type:
            return None, EvaluatorException("TypeError: " + node.__str__() + " Of Type : " + node.type + ", Expected : " + array_type)
        node_expr, err = eval(node, environment)
        if err != None: return None, err
        exprs.append(node_expr)
    return Array(exprs), None

def eval_assign(assign : AssignNode, environment : Environment) -> Object and Exception:
    expr, err = eval(assign.expression, environment)
    if err != None: return None, err

    if assign.identifier in environment.locals: 
        node = environment.locals[assign.identifier]
        if node.__type__() != expr.__type__() and node.__type__() != "[]": 
            return None, EvaluatorException("TypeError: " +expr.__str__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + node.__type__())
        environment.locals[assign.identifier] = expr

    elif assign.identifier in environment.globals:
        node = environment.globals[assign.identifier]
        if node.__type__() != expr.__type__() and node.__type__() != "[]": 
            return None, EvaluatorException("TypeError: " +expr.__str__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + node.__type__())
        environment.globals[assign.identifier] = expr

    else:
        return None, EvaluatorException("UndefinedVariable: " + assign.identifier)
    
    return Null(), None
    

def eval_init(init : InitialiseNode, environment : Environment) -> Object and Exception:
    if init.parameters != None:
        function = FunctionDeclaration(init.var_type, init.parameters, init.expression)
        if init.scope == GLOBAL:
            environment.globals[init.identifier] = function
        else:
            environment.locals[init.identifier] = function 
            
        return Null(), None


    expr, err = eval(init.expression, environment)
    if err != None: return None, err

    if expr.__type__() != init.var_type and expr.__type__() != "[]":
        return None, EvaluatorException("TypeError: " +expr.__str__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + init.var_type)
    
    if init.scope == GLOBAL:
        environment.globals[init.identifier] = expr
    else:
        environment.locals[init.identifier] = expr

    return Null(), None

def eval_identifier(identifier : IdentifierNode, environment : Environment) -> Object and Exception:
    if identifier.identifier in environment.locals:
        return environment.locals[identifier.identifier], None

    elif identifier.identifier in environment.globals:
        return environment.globals[identifier.identifier], None

    return None, EvaluatorException("UndefinedVariable: " + identifier.identifier)

def eval_unary(unary : UnaryOperationNode, environment : Environment) -> Object and Exception:
    right, err = eval(unary.right, environment)
    if err != None: return None, err

    if unary.op == SUB and right.type in (INT, FLOAT):
        return assign_type(-right.value), None
    if unary.op == NOT:
        if right.type == BOOL:
            return Boolean(0 if right.value == 1 else 1), None
        if right.type == INT:
            return Int(0 if right.value == 1 else 1), None

def eval_binop(binop : BinaryOperationNode, environment : Environment) -> Object and Exception:
    left, err = eval(binop.left, environment)
    if err != None: return None, err

    right, err = eval(binop.right, environment)
    if err != None: return None, err

    result,err = left.binary_operation(right, binop.op)
    if err != None: return None, err

    return result, None

def eval_program(program : ProgramNode, environment : Environment) -> Object and Exception:
    for node in program.nodes:
        result, err = eval(node, environment)
        if err != None: return None, err

        if result.type == RETURN: 
            return result, None
        if result.type != NULL: print(result)

    return Null(), None
