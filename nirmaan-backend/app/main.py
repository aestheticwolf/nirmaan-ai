from fastapi import FastAPI
from app.routes import rules, cad, auth
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import plot, building  

Base.metadata.create_all(bind=engine)

app = FastAPI(title="NIRMAAN.AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules.router)
app.include_router(cad.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "NIRMAAN.AI backend running"}