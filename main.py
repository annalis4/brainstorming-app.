import logging
from fastapi import FastAPI

app = FastAPI()

@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error(f"Unhandled error: {e}", exc_info=True)
        raise

import os
from supabase import create_client 

url = os.getenv("SUPABASE_URL", "https://cmqiuyqpzcdwgqgkgmdc.supabase.co")
key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcWl1eXFwemNkd2dxZ2tnbWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjAyNDgsImV4cCI6MjA3MTA5NjI0OH0.JyqSexwA9INcc3HjNemLUhveCQzY-AAplD8YHACkZP0")
supabase = create_client(url, key)

# Template (HTML)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/idea")
async def add_idea(request: Request):
    data = await request.json()
    content = data.get("content")
    res = supabase.table("ideas").insert({"content": content}).execute()
    return {"status": "ok", "idea": res.data}

@app.get("/ideas")
def list_ideas():
    res = supabase.table("ideas").select("*").execute()
    return {"ideas": res.data}
