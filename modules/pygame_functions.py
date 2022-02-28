from os import environ
import pygame
from evaluator.objects import *
from evaluator.evaluator import eval
from parse.nodes import *
from lexer.token import *

def handle_pygameVersion(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    print("Pygame module initialised")
    return Null(), environment, None

def handle_newWindow(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) < 2:
        return None, None, EvaluatorException("newWindowError: Expected parameter length 2, got: " + str(len(node.parameters)))

    x = node.parameters[0]

    if x.type != INT:
        return None, None, EvaluatorException("newWindowError: Expected parameter 0 to be type INT, got: " + node.parameters[0].__type__())

    y = node.parameters[1]

    if y.type != INT:
        return None, None, EvaluatorException("newWindowError: Expected parameter 1 to be type INT, got: " + node.parameters[1].__type__())

    environment.externals["screen"] = pygame.display.set_mode([x.value, y.value])
    environment.externals["clock"] = pygame.time.Clock()
    return Null(), environment, None

def handle_pygameInit(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    running = True 
    while running:
        if "tickrate" in environment.externals:
            if "clock" not in environment.externals:
                return None, None, EvaluatorException("PygameError: pygame window not initialised")
            environment.externals["clock"].tick(environment.externals["tickrate"])
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        result, err = eval(InvokeNode("update", []), environment)
        if err != None:
            return None, None, err

        pygame.display.flip()
    return Null(), environment, None

def handle_clear(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) > 1:
        return None, None, EvaluatorException("clearError: Expected parameter length <= 1, got: " + str(len(node.parameters)))

    colour = node.parameters[0] if len(node.parameters) == 1 else assign_type([255,255,255])
    if colour.__type__() != "[]int":
        return None, None, EvaluatorException("clearError: Expected parameter type []int, got: " + colour.__type__())
    elif len(colour.value) != 3:
        return None, None, EvaluatorException("clearError: Expected parameter 1 type []int, length 3, got: " + str(len(colour.value)))

    if "screen" not in environment.externals:
        return None, None, EvaluatorException("PygameError: Screen not initialised")

    colour_value = return_base(colour)
    screen = environment.externals["screen"]
    screen.fill(colour_value)
    
    return Null(), environment, None

def handle_rect(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) != 3:
        return None, environment, EvaluatorException("rectError: Expected parameter length 3, got: " + str(len(node.parameters)))

    position = node.parameters[0]
    if position.__type__() not in ("[]int", "[]float"): return None, None, EvaluatorException("rectError: Expected position type []int, got: " + position.__type__())
    if len(position.value) != 2: return None, None, EvaluatorException("rectError: Expected position type []int, length 2, got: " + position.__str__())

    size = node.parameters[1]
    if size.__type__() not in ("[]int", "[]float"): return None, None, EvaluatorException("rectError: Expected size type []int, got: " + size.__type__())
    if len(size.value) != 2: return None, None, EvaluatorException("rectError: Expected size type []int, length 2, got: " + size.__str__())

    colour = node.parameters[2]
    if colour.__type__() != "[]int": return None, None, EvaluatorException("rectError: Expected colour type []int, got: " + colour.__type__())
    elif len(colour.value) != 3: return None, None, EvaluatorException("rectError: Expected colour type []int, length 3, got: " + str(len(colour.value)))

    if "screen" in environment.externals:
        position_base = return_base(position)
        size_base = return_base(size)
        colour_base = return_base(colour)

        screen = environment.externals["screen"]

        pygame.draw.rect(screen, colour_base, (position_base[0], position_base[1], size_base[0], size_base[1]))
    else:
        return None, None, EvaluatorException("PygameError: Screen not initialised")

    return Null(), environment, None

def handle_tick(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("tickError: Expected parameter length 1, got: " + str(len(node.parameters)))

    ticks = node.parameters[0]

    if ticks.type not in (FLOAT, INT):
        return None, None, EvaluatorException("tickError: Expected ticks to be type INT, got: " + str(ticks.__type__()))
    
    if "clock" not in environment.externals:
        return None, None, EvaluatorException("tickError: Pygame window not initialised")

    environment.externals["clock"].tick(ticks.value)
    return Null(), environment, None

def handle_tickrate(node : InvokeNode, environment : Environment) -> Object and Environment and Exception:
    if len(node.parameters) != 1:
        return None, None, EvaluatorException("tickrateError: Expected parameter length 1, got: " + str(len(node.parameters)))

    ticks = node.parameters[0]

    if ticks.type not in (INT, FLOAT):
        return None, None, EvaluatorException("tickrateError: Expected ticks to be type INT, got: " + str(ticks.__type__()))
    
    if "clock" not in environment.externals:
        return None, None, EvaluatorException("tickrateError: Pygame window not initialised")

    environment.externals["tickrate"] = ticks.value
    return Null(), environment, None




def extract_functions():
    return  {
        "pygameVersion":handle_pygameVersion,
        "newWindow": handle_newWindow,
        "pygameInit": handle_pygameInit,
        "clear": handle_clear,
        "rect": handle_rect,
        "tick": handle_tick,
        "tickrate": handle_tickrate,
    }