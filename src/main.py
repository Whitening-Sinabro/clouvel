from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import docs_router, guide_router

app = FastAPI(
    title="Clouvel",
    description="AI 실수를 기억하고 재발을 방지하는 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_router)
app.include_router(guide_router)


@app.get("/")
def root():
    return {
        "name": "Clouvel",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/docs/scan",
            "/docs/analyze", 
            "/guide/prd",
            "/guide/verify"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}
