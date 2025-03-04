import argparse
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
        transitions=trans_dict,
        initial_state=initial_state,
        final_states=final_states
    )
