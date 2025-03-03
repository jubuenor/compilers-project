from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.cfgToPda.cfgToPda import converseCfgToPda

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
    raw, formatted = converseCfgToPda(body.grammar)
    return {"raw": raw, "formatted": formatted}
