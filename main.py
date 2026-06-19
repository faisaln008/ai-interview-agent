from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes import router
from app.database import init_db

load_dotenv()

app = FastAPI(title="AI Agent", version="0.1.0")
app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
