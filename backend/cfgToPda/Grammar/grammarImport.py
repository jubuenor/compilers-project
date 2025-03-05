
from backend.cfgToPda.Utils.Exceptions import IllegalVariableException
import backend.cfgToPda.Utils.constants as constant
from backend.cfgToPda.Automata.state import State
from backend.cfgToPda.Automata.transition import Transition

def importGrammar(grammar_str):
    data = grammar_str.strip().splitlines()
    if len(data) < 3:
        raise ValueError("La gramática debe tener al menos 3 líneas: "
                         "1) símbolo inicial, 2) terminales, 3) reglas de producción.")

    initStateSym = data[0].rstrip()   
    terminals = data[1].rstrip()     
    states = []
    transitions = []

    initState = State("Q0", True, False, [])
    midState = State("Q1", False, False, [])
    finalState = State("Q2", False, True, [])

    terminals = terminals.split(',')

    for idx in range(2, len(data)):
        rule = data[idx].strip()
        rule = rule.replace(" ", "")
        for character in rule:
            if character in ['-', '>', '|']:
                continue
            elif character not in terminals and (not character.isupper()) and character not in [constant.LAMBDA, "ε"]:
                raise IllegalVariableException(character, rule)

        lhs = rule[:rule.find('-')]  
        rhs = rule[rule.find('>') + 1:]  
        rhs = rhs.split('|')

        for prod in rhs:
            trans = Transition(
                prod[:1],        
                midState,
                midState,
                lhs,             
                list(prod[1:]) if len(list(prod[1:])) > 0 else [constant.LAMBDA]
            )
            transitions.append(trans)

    init = Transition(constant.LAMBDA, initState, midState, constant.EPSILON, [initStateSym, constant.EPSILON])
    transitions.append(init)
    final = Transition(constant.LAMBDA, midState, finalState, constant.EPSILON, [constant.EPSILON])
    transitions.append(final)

    states = [initState, midState, finalState]
    return states, transitions
