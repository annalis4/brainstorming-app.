from flask import Flask, render_template, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

# --- Integrazione Supabase ---
url = os.getenv("SUPABASE_URL", "https://TUO-PROGETTO.supabase.co")
key = os.getenv("SUPABASE_KEY", "LA-TUA-ANON-KEY")
supabase = create_client(url, key)

# --- Rotte ---
@app.route("/")
def home():
    """Mostra la pagina principale con la lavagna"""
    return render_template("index.html")

@app.route("/idea", methods=["POST"])
def add_idea():
    """Aggiunge una nuova idea"""
    data = request.get_json()
    content = data.get("content")
    if not content:
        return jsonify({"status": "error", "message": "contenuto mancante"}), 400
    
    res = supabase.table("ideas").insert({"content": content}).execute()
    return jsonify({"status": "ok", "idea": res.data})

@app.route("/ideas", methods=["GET"])
def list_ideas():
    """Ritorna tutte le idee"""
    res = supabase.table("ideas").select("*").order("created_at", desc=True).execute()
    return jsonify({"ideas": res.data})

# --- Avvio locale ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
git add .
git commit -m "Aggiunta struttura base Flask"
git push origin main
