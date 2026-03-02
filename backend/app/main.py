import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LogSleuth API",
    description="AI-powered log anomaly detector",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["Logs"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    # 2. Tell Uvicorn to treat the parent folder (backend) as the root directory
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, app_dir=parent_dir)