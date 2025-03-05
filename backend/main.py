from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.cfgToPda.Automata.dfa import generate_mermaid_diagram
from backend.cfgToPda.cfgToPda import generate_items_nfa, converseCfgToPda, grammar_to_nfa

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BodyRequest(BaseModel):
    grammar: str

@app.get("/ping")
def read_root():
    return "pong"

@app.post("/convert")
def read_item(body: BodyRequest):
    try:
        raw, formatted = converseCfgToPda(body.grammar)
        return {"raw": raw, "formatted": formatted}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert-dfa")
def convert_dfa(body: BodyRequest):
    nfa = grammar_to_nfa(body.grammar)
    dfa = nfa.to_dfa()
    mermaid_dfa = generate_mermaid_diagram(dfa)
    return {"raw": dfa, "formatted": mermaid_dfa}

@app.post("/items")
def generate_items(body: BodyRequest):
    # previous step: generate eNFA with valid items
    dfa_states, dfa_start, dfa_transitions, dfa_final_states = generate_items_nfa(body.grammar)
    #res = generate_items_nfa(body.grammar)

    #print(dfa_transitions)

    states_list = {}

    lines = ["flowchart LR"]

    cont = 0
    for state, trans in dfa_transitions.items():
        for sym, dest_list in trans.items():
            state_str = ';'.join(list(state))
            dest_str = ';'.join(list(dest_list))

            if dest_str != '':
                if not state_str in states_list:
                    cont+=1
                    state_name = f"S{cont}"
                    states_list[state_str] = state_name
                    lines.append(f'    {state_name}["`{state_str}`"]')
                if not dest_str in states_list:
                    cont+=1
                    dest_name = f"S{cont}"
                    states_list[dest_str] = dest_name
                    lines.append(f'    {dest_name}["`{dest_str}`"]')
                state_name = states_list[state_str]
                dest_name = states_list[dest_str]
                lines.append(f"    {state_name}-->|'{sym.replace('(', '⦅').replace(')','⦆')}'|{dest_name}")


    to_return = "\n".join(lines)
    return {"formatted": to_return}
    #return {"formatted": res}
