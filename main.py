from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from supabase import create_client
import os

app = FastAPI()

# Integrazione Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
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
git push
