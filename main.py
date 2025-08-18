from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import os

# Inizializza Flask
app = Flask(__name__)

# Configura Supabase con variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Devi impostare SUPABASE_URL e SUPABASE_KEY come variabili d'ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rotta principale: mostra la pagina con il form
@app.route("/")
def index():
    return render_template("index.html")

# Rotta per inserire una nuova idea
@app.route("/idea", methods=["POST"])
def add_idea():
    data = request.get_json()
    content = data.get("content", "").strip()
    if content:
        res = supabase.table("ideas").insert({"content": content}).execute()
        return jsonify({"status": "ok", "idea": res.data})
    return jsonify({"status": "error", "message": "Nessun contenuto ricevuto"}), 400

# Rotta per mostrare tutte le idee
@app.route("/ideas", methods=["GET"])
def list_ideas():
    res = supabase.table("ideas").select("*").order("id", desc=True).execute()
    return jsonify({"ideas": res.data})

if __name__ == "__main__":
    # Avvio in locale (su Render useremo gunicorn)
    app.run(host="0.0.0.0", port=5000, debug=True)
