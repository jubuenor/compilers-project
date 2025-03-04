from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.cfgToPda.Automata.dfa import generate_mermaid_diagram
from backend.cfgToPda.cfgToPda import converseCfgToPda, grammar_to_nfa

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
