import argparse
import re
from collections import deque, defaultdict
import backend.cfgToPda.Grammar.grammarImport as Grammar
import backend.cfgToPda.Utils.constants as constant
from backend.cfgToPda.Automata.state import State
from backend.cfgToPda.Automata.transition import Transition

debug = False  # debug mode, shows stack contents while parsing

class Automaton:
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

    def toPda(self):
        trFunc = {}
        for t in self.transitions:
            key = (t.currState.name, t.inputSymbol, t.popSymbol)
            trFunc.setdefault(key, []).append((t.nextState.name, t.pushSymbols))

        rawTransitions = ""
        mermaidFormattedTransitions = "stateDiagram-v2\n"

        for key, transitions in trFunc.items():
            for (nextState, pushSymbols) in transitions:
                pushStr = ''.join(pushSymbols)
                label = f"{key[1]}, {key[2]} → {pushStr}"
                mermaidFormattedTransitions += f"{key[0]} --> {nextState} : {label}\n"

                rawTransitions += f"{constant.DELTA}({key[0]},{key[1]},{key[2]}) = ( {nextState},{pushStr} )\n"

        return rawTransitions, mermaidFormattedTransitions

    def checkMembership(self, string):
        stack = [constant.EPSILON]
        currState = None
        for state in self.states:
            if state.isInitial:
                currState = state
                break
        finishProcess, finalState = self.matchStr(string, currState, stack)
        return finalState.isFinal and finishProcess

    def matchStr(self, string, currState, stack):
        idx = len(stack) - 1
        top = stack[idx]
        finishProcess = False
        inputSym = string[0] if len(string) > 0 else constant.LAMBDA
        state = currState
        visited = False

        for tr in self.transitions:
            if (
                tr.currState is currState
                and (tr.inputSymbol == inputSym or tr.inputSymbol == constant.LAMBDA)
                and (tr.popSymbol == top)
            ):
                newStack = stack[:-1]
                pushSymbols = tr.pushSymbols[:]
                pushSymbols.reverse()
                for sym in pushSymbols:
                    if sym != constant.LAMBDA:
                        newStack.append(sym)
                if debug:
                    print("newStack:", newStack)

                if tr.inputSymbol == constant.LAMBDA:
                    finishProcess, state = self.matchStr(string[:], tr.nextState, newStack)
                else:
                    finishProcess, state = self.matchStr(string[1:], tr.nextState, newStack)
                visited = True
                if state.isFinal and finishProcess:
                    break

        if not visited:
            finishProcess = (len(string) == 0)

        return finishProcess, state

def converseCfgToPda(grammar_str):
    states, transitions = Grammar.importGrammar(grammar_str)
    pda = Automaton(states, transitions)
    raw, mermaid = pda.toPda()
    return raw, mermaid


def epsilon_closure(state, epsilon_transitions):
    """Computes the epsilon closure of a state."""
    closure = set()
    stack = [state]
    while stack:
        current = stack.pop()
        if current not in closure:
            closure.add(current)
            if current in epsilon_transitions:
                stack.extend(epsilon_transitions[current])
    return closure


def nfa_to_dfa(states, alphabet, transitions, start_state, final_states, epsilon_transitions):
    """Converts an NFA (with or without epsilon transitions) to a DFA."""
    dfa_states = {}
    dfa_start = frozenset(epsilon_closure(start_state, epsilon_transitions)) if epsilon_transitions else frozenset([start_state])
    dfa_queue = deque([dfa_start])
    dfa_transitions = {}
    dfa_final_states = set()
    
    while dfa_queue:
        current_dfa_state = dfa_queue.popleft()
        if current_dfa_state in dfa_states:
            continue
        
        dfa_states[current_dfa_state] = len(dfa_states)
        dfa_transitions[current_dfa_state] = {}
        
        if any(state in final_states for state in current_dfa_state):
            dfa_final_states.add(current_dfa_state)
        
        for symbol in alphabet:
            if symbol == 'ε':
                continue
            
            new_state = set()
            for nfa_state in current_dfa_state:
                if symbol in transitions.get(nfa_state, {}):
                    for next_state in transitions[nfa_state][symbol]:
                        if epsilon_transitions:
                            new_state.update(epsilon_closure(next_state, epsilon_transitions))
                        else:
                            new_state.add(next_state)
            
            new_state = frozenset(new_state)
            if new_state and new_state not in dfa_states:
                dfa_queue.append(new_state)
            
            dfa_transitions[current_dfa_state][symbol] = new_state
    
    return dfa_states, dfa_start, dfa_transitions, dfa_final_states



def gen_auto(item, rules, table=None, already_expanded=None):
    if table is None:
        table = []
    if already_expanded is None:
        already_expanded = []

    already_expanded.append(item)
    
    if item.endswith('.'):
        return table
    
    point_index = item.index('.')
    next_symbol = [s for s in all_symbols if item[point_index + 1:].startswith(s)][0]
    
    s_len = len(next_symbol)
    next_item = item.replace('.', '')
    next_item = next_item[:point_index + s_len] + '.' + next_item[point_index + s_len:]
    
    table.append([[item, next_symbol], next_item])
    gen_auto(next_item, rules, table, already_expanded)
    
    if next_symbol in non_term_array:
        symbol_rules = [r for r in rules if r[0] == next_symbol]
        for rule in symbol_rules:
            new_item = rule[0] + '->.' + rule[1]
            table.append([[item, 0], new_item])
            
            if new_item not in already_expanded:
                gen_auto(new_item, rules, table, already_expanded)
    
    return table


def create_items(grammar, start_sym, terminals):
    #example_grammar = "S'->S ; S->(T) ; T->T+int|int"
    #ex_non_terminals = "S',S,T"
    #ex_terminals = "(,),+,int"
    global all_symbols, non_term_array
    
    mod_grammar = grammar.replace(' ', '')
    pre_rules = [r for r in mod_grammar.split(';') if r]
    #non_term_array = [t for t in non_terminals.split(',') if t]
    term_array = [t for t in terminals.split(',') if t]
    
    non_term_array = [start_sym + "'"]
    rules = [[start_sym + "'", start_sym]]
    for rule in pre_rules:
        match = re.match(r'^(.*)->(.*)$', rule)
        if match:
            lhs, rhs = match.groups()

            non_term_array.append(lhs)

            rhs_rules = rhs.split('|')
            for r in rhs_rules:
                rules.append([lhs, r])

    all_symbols = non_term_array + term_array
    
    start_rule = rules[0]
    initial_state = start_rule[0] + '->.' + start_rule[1]
    return gen_auto(initial_state, rules)


def generate_items_nfa (grammar_str):
    pre_grammar = grammar_str.splitlines()
    start_symbol = pre_grammar[0].strip()
    terminals = pre_grammar[1].strip()
    rules = pre_grammar[2:]
    rules = ';'.join([r.strip() for r in rules])
    items_table = create_items(rules, start_symbol, terminals)

    ### creating ε-nfa data
    eps_transitions = {}
    transitions = {}
    initial_state = None
    states = set()
    final_states = set()
    sigma_boy_alph = set(all_symbols)
    for rules_tp in items_table:
        state_symb_pair, to_state = rules_tp
        from_state, symbol = state_symb_pair

        states.add(from_state)
        states.add(to_state)

        if (from_state.find("'")
                and not from_state.endswith('.')):
            initial_state = from_state
        if to_state.endswith('.'):
            final_states.add(to_state)

        if symbol == 0:
            if from_state in eps_transitions:
                eps_transitions[from_state].add(to_state)
            else:
                eps_transitions[from_state] = {to_state}
        else:
            if from_state in transitions:
                transitions[from_state][symbol].add(to_state)
            else:
                transitions[from_state] = {symbol: {to_state}}

    #items_table
    '''dfa_states, dfa_start, dfa_transitions, dfa_final_states =
    print(dfa_states)
    [states,
            sigma_boy_alph,
            transitions,
            initial_state,
            final_states,
            eps_transitions]'''
    return nfa_to_dfa(
            states,
            sigma_boy_alph,
            transitions,
            initial_state,
            final_states,
            eps_transitions)

def grammar_to_nfa(grammar_str: str):
    from backend.cfgToPda.Grammar import grammarImport
    states, transitions = grammarImport.importGrammar(grammar_str)
    data = grammar_str.strip().splitlines()
    terminals = set(data[1].rstrip().split(','))
    state_names = {s.name for s in states}
    initial_state = next(s.name for s in states if s.isInitial)
    final_states = {s.name for s in states if s.isFinal}
    trans_dict = {}
    for s in state_names:
        trans_dict[s] = {}
    for t in transitions:
        src = t.currState.name
        sym = t.inputSymbol
        dest = t.nextState.name
        if sym not in trans_dict[src]:
            trans_dict[src][sym] = []
        trans_dict[src][sym].append(dest)

    from backend.cfgToPda.Automata.dfa import NFA
    return NFA(
        alphabet=terminals,
        states=state_names,
        transitions=transitions,#trans_dict,
        initial_state=initial_state,
        final_states=final_states
    )
