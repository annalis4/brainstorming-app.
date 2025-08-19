from flask import Flask, request, jsonify, render_template
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cmqiuyqpzcdwgqgkgmdc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcWl1eXFwemNkd2dxZ2tnbWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjAyNDgsImV4cCI6MjA3MTA5NjI0OH0.JyqSexwA9INcc3HjNemLUhveCQzY-AAplD8YHACkZP0")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/idea", methods=["POST"])
def add_idea():
    data = request.get_json()
    content = data.get("content", "").strip().lower()  # normalizza a minuscolo
    if not content:
        return jsonify({"status": "error", "message": "Nessun contenuto ricevuto"}), 400

    # Verifica se già esiste
    existing = supabase.table("ideas").select("*").eq("content", content).execute().data
    if existing:
        idea = existing[0]
        new_count = idea["count"] + 1
        supabase.table("ideas").update({"count": new_count}).eq("id", idea["id"]).execute()
        idea["count"] = new_count
        return jsonify({"status": "ok", "idea": idea})

    # Inserisci nuova idea senza posizione
    res = supabase.table("ideas").insert({"content": content}).execute()
    return jsonify({"status": "ok", "idea": res.data[0]})

@app.route("/ideas", methods=["GET"])
def list_ideas():
    res = supabase.table("ideas").select("*").execute()
    return jsonify({"ideas": res.data})

@app.route("/idea/position", methods=["POST"])
def save_position():
    data = request.get_json()
    idea_id = data.get("id")
    x = data.get("x")
    y = data.get("y")
    if idea_id is None or x is None or y is None:
        return jsonify({"status": "error", "message": "Dati mancanti"}), 400
    supabase.table("ideas").update({"pos_x": x, "pos_y": y}).eq("id", idea_id).execute()
    return jsonify({"status": "ok"})

# Reset lavagna
@app.route("/reset", methods=["POST"])
def reset():
    supabase.table("ideas").delete().neq("id", 0).execute()
    return jsonify({"status": "ok", "message": "Lavagna resettata"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
