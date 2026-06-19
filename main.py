from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.routes import router

load_dotenv()

app = FastAPI(title="AI Agent", version="0.1.0")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}