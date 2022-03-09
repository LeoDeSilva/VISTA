from os import environ
from xmlrpc.client import INVALID_ENCODING_CHAR
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
    elif node.type == INDEX:
        return eval_index(node, environment)
    elif node.type == BREAK:
        return node, None
    elif node.type == FLAG:
        environment.flags[node.option] = True
        return Null(), None
    elif node.type == LOAD:
        return eval_load(node, environment)
    elif node.type == ANONYMOUS:
        return eval_anonymous(node, environment)
    
    else:
        return None, EvaluatorException(environment.lineNumber,"UnexpectedNode: " + node.__str__())

def eval_anonymous(anonymous : AnonymousFunctionNode, environment : Environment) -> Object and Exception:
    return FunctionDeclaration(anonymous.var_type, anonymous.parameters, anonymous.consequence), None

def eval_load(load : LoadNode, environment : Environment) -> Object and Exception:
    if load.option == "pygame":
        import modules.pygame_module as pygame_module
        environment.functions.update(pygame_module.extract_methods())
    return Null(), None

def eval_index(index : IndexNode, environment :  Environment) -> Object and Exception:
    array, err = eval(index.array, environment)
    if err != None: return None, err
    if array.type not in (ARRAY, STRING):
        return None,EvaluatorException(environment.lineNumber,"IndexError: Cannot Index: " + array.__str__() + " Expected Type ARRAY")

    index_expr, err = eval(index.index, environment)
    if err != None: return None
    if index_expr.type != INT:
        return None, EvaluatorException(environment.lineNumber,"IndexError: Index must be of type INT, got: " + index_expr.__str__())
    
    return array.index(index_expr.value, environment)

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

    local_environment = new_environment(environment.lineNumber, environment)

    if invoke.function_node.type == ANONYMOUS:
        function, err = eval(invoke.function_node, environment)
        if err != None: return None, err

    elif invoke.function_node.type == IDENTIFIER:
        if invoke.function_node.identifier in environment.locals:
            function = environment.locals[invoke.function_node.identifier]

        elif invoke.function_node.identifier in environment.globals:
            function = environment.globals[invoke.function_node.identifier]

        elif invoke.function_node.identifier in environment.functions:
            result, updated_env, err =  environment.functions[invoke.function_node.identifier](
                InvokeNode(invoke.line_number,invoke.function_node.identifier, parameters),
                local_environment
            )

            if err != None: return None, err
            environment.globals.update(updated_env.globals)
            environment.externals.update(updated_env.externals)
            return result, err

        else:
            return None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: Undefined Function: " + invoke.function_node.identifier)

    if function.type != FUNCTION:
        return None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: Identifier: " + invoke.function_node + " Not type FUNCTION")

    for i,param_node in enumerate(function.parameters):
        if not types_equal(param_node.var_type, parameters[i].__type__()):
            return None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: Expected parameter " + str(i) + " type " + str(param_node.var_type) + " got: " + parameters[i].__type__())

        local_environment.locals[param_node.identifier] = parameters[i]

    result, updated_env, err = eval_program(function.consequence, local_environment)
    if err != None: return None, err
    environment.globals.update(updated_env.globals)
    environment.externals.update(updated_env.externals)

    if result.type == RETURN:
        return result.expression, None
    elif not types_equal(function.func_type, result.__type__()):
        return None, EvaluatorException(environment.lineNumber,"InvokeFunctionError: Expected Return Type : " + function.func_type + " got: " + result.__type__())

    return result, None
        

def eval_for(fornode : ForNode, environment : Environment) -> Object and Exception:
    array, err = eval(fornode.expression, environment)
    if err != None: return None, err
    if array.type not in (ARRAY, STRING):
        return None, EvaluatorException(environment.lineNumber,"ForNodeError: Expected Expression Type ARRAY or STRING, got: " + array.__str__())
     
    i = 0
    while i < len(array.value):
        expr = array.value[i] if not isinstance(array.value[i],str) else assign_type(array.value[i])
        if not types_equal(fornode.var_type, expr.__type__()):
            return None, EvaluatorException(environment.lineNumber,"ForNodeError: Expected Node Type: " + fornode.var_type + " got: " + expr.__type__()) 
        
        environment.locals[fornode.identifier] = expr
        result, _, err = eval_program(fornode.consequence, environment)
        if err != None: return None, err
        if result.type == RETURN: return result, None
        elif result.type == BREAK: break

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
    result = Null()
    satisfied, err = eval_conditions(node.conditions, environment)
    if err != None: return None, err, False

    if satisfied:
        result, _, err = eval_program(node.consequence, environment)
        if err != None: return None, err, True
        # if result.type == RETURN: return result, None, True
        # return Null(), None, True

    return result, None, satisfied

def eval_if(ifnode : IfNode, environment : Environment) -> Object and Exception:
    satisfied = False
    i = 0
    #Loop through all elif's untill one is satisfied
    while not satisfied and i < len(ifnode.conditions):
        result, err, satisfied= eval_conditional(ifnode.conditions[i], environment)
        if err != None: return None, err
        if result.type in (RETURN,BREAK): 
            return result, None
        i += 1
    return Null(), None

def eval_while(whilenode : WhileNode, environment : Environment) -> Object and Exception:
    satisfied = True
    i = 0
    while satisfied:
        result, err, satisfied = eval_conditional(whilenode.conditional, environment)
        if err != None: return None, err
        if result.type == RETURN: return result, None
        if result.type == BREAK: break
        i += 1
    return Null(), None

def eval_array(array : ArrayNode, environment : Environment) -> Object and Exception:
    if len(array.nodes) == 0: return Array([]), None
    exprs = []
    array_type = ""
    for node in array.nodes:
        node_expr, err = eval(node, environment)
        if array_type == "": array_type = node_expr.__type__()
        if not types_equal(array_type, node_expr.__type__()):
            return None, EvaluatorException(environment.lineNumber,"TypeError: " + node_expr.__str__() + " Of Type : " + node_expr.__type__() + ", Expected : " + array_type)
        if err != None: return None, err
        exprs.append(node_expr)
    return Array(exprs), None


def base_array(node : Node, environment : Environment) -> Object and Object and str and Exception:
    # Return base array
    array = node
    while array.type == INDEX: 
        array = array.array

    # Index, each prev index is wrapped in next index, reversing order
    prev_index = array
    cur_node = node
    while cur_node.type == INDEX:
        prev_index = IndexNode(environment.lineNumber, prev_index, cur_node.index)
        cur_node = cur_node.array
    
    identifier = array.identifier if array.type == IDENTIFIER else ""

    base, err = eval(array, environment)
    if err != None: return None, None, None, err

    if base.type not in (ARRAY, STRING):
        return None, None, None, EvaluatorException(environment.lineNumber,"IndexError: cannot index: " + base.__str__() + " expected type ARRAY, got: " + base.type)

    return base, prev_index, identifier, None


def replace(base : Object, node : Object, index : int, value : Object, environment : Environment) -> Object and Exception:
    # If not bottom level index (has acess to base array), replace this index with the replaced version of sub array
    if node.type == INDEX and node.array.type == INDEX:
        # because replacing the next array needs next index
        next_index, err = eval(node.array.index, environment)
        if err != None: return None, err

        # The array to be replaced is the index of this array e.g. [[1,2]][0] = [1,2]
        next_array, err = base.index(index, environment)
        if err != None: return None, err

        # the replaced version of the next_array e.g. [10,2][0] = -1  => [0,2]
        replaced, err = replace(next_array, node.array, next_index.value, value, environment)
        if err != None: return None, err

        # Replace the index to be changed with modified sub array
        return base.replace(index, replaced, environment)

    elif node.type == INDEX:
        # If lowest level index, just replace base array
        return  base.replace(index,value, environment)


def eval_assign(assign : AssignNode, environment : Environment) -> Object and Exception:
    # assign.identifier = Token(IDENTIFIER, assign.identifier) if isinstance(assign.identifier, str) else assign.identifier
    expr, err = eval(assign.expression, environment)
    if err != None: return None, err

    if assign.identifier.type == INDEX:
        # Reverse order of indexes (otherwise wrong order), see if identifier and return base array
        array, indices, identifier, err = base_array(assign.identifier, environment)
        if err != None: return None, err

        index, err = eval(indices.index, environment)
        if err != None: return None, err

        array, err = replace(array, indices, index.value, expr, environment)
        if err != None: return None, err

        expr = array

        # If no identifier, return the replaced array, this lets [x,x,x][0] = 10 be used as an atom in expressions
        if identifier == "":
            return array, None
        
        assign_identifier = identifier
    elif assign.identifier.type == IDENTIFIER:
        assign_identifier = assign.identifier.literal
        

    if assign_identifier in environment.locals: 
        node = environment.locals[assign_identifier]
        if not types_equal(node.__type__(), expr.__type__()): 
            return None, EvaluatorException(environment.lineNumber,"TypeError: " +expr.__type__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + node.__type__())
        environment.locals[assign_identifier] = expr

    elif assign_identifier in environment.globals:
        node = environment.globals[assign_identifier]
        if not types_equal(node.__type__(), expr.__type__()): 
            return None, EvaluatorException(environment.lineNumber,"TypeError: " +expr.__type__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + node.__type__())
        environment.globals[assign_identifier] = expr

    else:
        return None, EvaluatorException(environment.lineNumber,"UndefinedVariable: " + assign_identifier)
    
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

    if not types_equal(init.var_type, expr.__type__()):
        return None, EvaluatorException(environment.lineNumber,"TypeError: " +expr.__str__() + " Of Type : " + expr.__type__() + " Does Not Equal Type : " + init.var_type)
    
    if init.scope == GLOBAL:
        environment.globals[init.identifier] = expr
    else:
        environment.locals[init.identifier] = expr

    return Null(), None

def eval_identifier(identifier : IdentifierNode, environment : Environment) -> Object and Exception:
    if identifier.identifier in environment.constants:
        return environment.constants[identifier.identifier], None

    if identifier.identifier in environment.locals:
        return environment.locals[identifier.identifier], None

    elif identifier.identifier in environment.globals:
        return environment.globals[identifier.identifier], None

    return None, EvaluatorException(environment.lineNumber,"UndefinedVariable: " + identifier.identifier)

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

    result,err = left.binary_operation(right, binop.op, environment)
    if err != None: return None, err

    return result, None

def eval_program(program : ProgramNode, environment : Environment) -> Object and Environment and Exception:
    for node in program.nodes:
        environment.lineNumber = node.line_number
        result, err = eval(node, environment)
        if err != None: return None, None, err

        if result.type in (RETURN, BREAK): 
            return result, environment, None
        # if result.type != NULL: print(result)

    return Null(), environment, None

def types_equal(left : Object, right : Object) -> bool:
    return left == right or (left[:2] == right[:2] and left[:2] == "[]")