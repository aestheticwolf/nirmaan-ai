from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Import models so SQLAlchemy registers them
from app.models import (
    plot,
    building,
    design,
    compliance_result,
    rule,
    project_version,
    state,
    authority,
    regulation
)
# Import routers
from app.routes import rules, cad, auth, dashboard

from app.models import rule, compliance_result, design

from app.routes.layout_edit import router as layout_edit_router


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NIRMAAN.AI Backend")



# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth.router)
app.include_router(cad.router)
app.include_router(rules.router)
app.include_router(dashboard.router)
app.include_router(layout_edit_router)

@app.get("/")
def root():
    return {"message": "NIRMAAN.AI backend running"}