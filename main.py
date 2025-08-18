import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error(f"Unhandled error: {e}", exc_info=True)
        raise

# Supabase client
url = os.getenv("SUPABASE_URL", "https://cmqiuyqpzcdwgqgkgmdc.supabase.co")
key = os.getenv("SUPABASE_KEY", "SUPER_SECRET_KEY")  # Don't hardcode in production!
supabase = create_client(url, key)

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/idea")
async def add_idea(request: Request):
    data = await request.json()
    content = data.get("content")
    try:
        res = supabase.table("ideas").insert({"content": content}).execute()
        return {"status": "ok", "idea": res.data}
    except Exception as e:
        logging.error(f"Failed to add idea: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/ideas")
async def list_ideas():
    try:
        res = supabase.table("ideas").select("*").execute()
        return {"ideas": res.data}
    except Exception as e:
        logging.error(f"Failed to list ideas: {e}")
        return {"status": "error", "detail": str(e)}
