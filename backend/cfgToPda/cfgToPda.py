import argparse
import backend.cfgToPda.Grammar.grammarImport as Grammar
import backend.cfgToPda.Utils.constants as constant
from backend.cfgToPda.Automata.state import State
from backend.cfgToPda.Automata.transition import Transition

debug = False # debug mode, shows stack contents while parsing

class Automaton:
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

    def toPda(self):
        trFunc = {}
        for t in self.transitions:
            key = (t.currState, t.inputSymbol, t.popSymbol)
            # make a new key in transition function if not found
            if (not key in trFunc.keys()):
                trFunc[key] = []
            trFunc[key].append((t.nextState, t.pushSymbols))
        trFunc = enumerate(trFunc.items())
        rawTransitions = ""
        mermaidFormattedTransitions = ""
        for i, (key, value) in trFunc:
            rawTransitions+=constant.DELTA + '(' + str(key[0]) + ',' + key[1] + ',' + key[2] + ') = {'
            mermaidFormattedTransitions+=str(key[0]) + '-->|' + key[1] + ', ' + key[2] + '; '
            targets = []

            for val in value:
                pushStr = ''.join(val[1])
                targets.append(
                    '(' + str(val[0]) + ',' + pushStr + ')'
                )
                if val==value[-1]:
                    mermaidFormattedTransitions += pushStr + '| ' + str(val[0]) + ';\n'
                else:
                    mermaidFormattedTransitions+=pushStr + ', ' 
            rawTransitions+= str(', ').join(targets) + ' }' + '\n'

        return rawTransitions, mermaidFormattedTransitions
    
    def checkMembership(self, string):
        stack = []
        stack.append(constant.EPSILON)
        # find initial state
        for state in self.states:
            if (state.isInitial):
                currState = state
                break
        finishProcess, state = self.matchStr(string, currState, stack)
        t = (state.isFinal and finishProcess)
        return t

    # has exponential time complexity, but is useful for small strings |w| <= 50
    def matchStr(self, string, currState, stack):
        # print(currState)
        idx = stack.__len__() -1
        top = stack[idx]
        finishProcess = False
        # next character to be processed
        if len(string) > 0:
            inputSym = string[0]
        else: inputSym = constant.LAMBDA
        state = currState
        visited = False # checks if any moves are left to backtrack

        for tr in self.transitions:
            if tr.currState is currState and (tr.inputSymbol == inputSym or tr.inputSymbol == constant.LAMBDA) and (tr.popSymbol == top):
                # remove last element from stack (pop simulation)
                newStack = stack [:-1]
                # add the non-lambda transition push symbols to stack
                pushSymbols = tr.pushSymbols[:]
                pushSymbols.reverse()
                for sym in pushSymbols:
                    if sym == constant.LAMBDA:
                        continue
                    newStack.append(sym)
                if debug:
                    print(newStack)
                # don't truncate if input symbol was lambda
                if (tr.inputSymbol == constant.LAMBDA):
                    finishProcess, state = self.matchStr(string[:], tr.nextState, newStack)
                else:
                    finishProcess, state = self.matchStr(string[1:], tr.nextState, newStack)
                visited = True #mark path traversed
                if state.isFinal and finishProcess: break


        if not visited: 
            # mark string processing finished only if string is reduced to base size 0
            finishProcess = (len(string) == 0) 

        return finishProcess, state


def converseCfgToPda(grammar_str):
#     grammar_str = """
# S
# i,*,(,),+
# S->E
# E->T+E|T
# T->i*T|i|(E)
#     """
#     grammar_str = """
# S
# a,b
# S->aSX|bSY|b
# X->b
# Y->a
# """

    states, transitions = Grammar.importGrammar(grammar_str)
    
    pda = Automaton(states, transitions)
    # print("PDA Transition Function:")
    raw, mermaid = pda.toPda()
    return raw, mermaid
    
    # print(raw)
    # print("Mermaid formatted transitions:")
    # print(mermaid)
    
    # while(True):
    #     print("Parse targets? (Y/N)")
    #     inp = input().strip().capitalize()
    #     if (inp != "Y"): break
    #     string = input("String to parse: ").strip()
    #     isMember = pda.checkMembership(string)
    #     if isMember:
    #         print("String " + string + " is part of the language.")
    #     else:
    #         print("String " + string + " is not in the language.")
