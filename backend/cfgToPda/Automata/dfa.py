
from typing import Set, Dict, List, FrozenSet, Any

class NFA:
    def __init__(
        self,
        alphabet: Set[str],
        states: Set[str],
        transitions: Dict[str, Dict[str, List[str]]],
        initial_state: str,
        final_states: Set[str]
    ):
        self.alphabet = alphabet
        self.states = states
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def epsilon_closure(self, state_set: Set[str]) -> Set[str]:
        closure = set(state_set)
        stack = list(state_set)
        epsilon_symbols = ["", "ε", "epsilon", "λ"]
        while stack:
            state = stack.pop()
            if state in self.transitions:
                for sym in epsilon_symbols:
                    if sym in self.transitions[state]:
                        for t in self.transitions[state][sym]:
                            if t not in closure:
                                closure.add(t)
                                stack.append(t)
        return closure

    def to_dfa(self):
        initial_closure = self.epsilon_closure({self.initial_state})
        initial_set = frozenset(initial_closure)
        dfa_states_map: Dict[FrozenSet[str], str] = {}
        dfa_states_map[initial_set] = "_".join(sorted(initial_set)) if initial_set else "empty"
        dfa_states: List[str] = [dfa_states_map[initial_set]]
        dfa_transitions: Dict[str, Dict[str, List[str]]] = {}
        dfa_final_states: List[str] = []

        if initial_set & self.final_states:
            dfa_final_states.append(dfa_states_map[initial_set])

        queue: List[FrozenSet[str]] = [initial_set]
        while queue:
            current_set = queue.pop(0)
            current_name = dfa_states_map[current_set]
            dfa_transitions[current_name] = {}

            for sym in self.alphabet:
                reachable = set()
                for st in current_set:
                    if st in self.transitions and sym in self.transitions[st]:
                        for t in self.transitions[st][sym]:
                            reachable |= self.epsilon_closure({t})
                if not reachable:
                    continue

                next_set = frozenset(reachable)
                if next_set not in dfa_states_map:
                    new_name = "_".join(sorted(next_set))
                    dfa_states_map[next_set] = new_name
                    dfa_states.append(new_name)
                    if next_set & self.final_states:
                        dfa_final_states.append(new_name)
                    queue.append(next_set)
                target_name = dfa_states_map[next_set]
                dfa_transitions[current_name].setdefault(sym, [])
                dfa_transitions[current_name][sym] = [target_name]

        dfa_result = {
            "alphabet": list(self.alphabet),
            "states": dfa_states,
            "initial_state": dfa_states_map[initial_set],
            "final_states": dfa_final_states,
            "transitions": dfa_transitions
        }
        return dfa_result

def generate_mermaid_diagram(dfa: Dict) -> str:
    lines = ["stateDiagram-v2"]
    lines.append(f"    [*] --> {dfa['initial_state']}")

    for state, trans in dfa["transitions"].items():
        for sym, dest_list in trans.items():
            for dest in dest_list:
                lines.append(f"    {state} --> {dest} : {sym}")

    for final_state in dfa["final_states"]:
        lines.append(f"    {final_state} --> [*]")

    return "\n".join(lines)
