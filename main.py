from flask import Flask, request, jsonify, render_template, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

# Configura Supabase
SUPABASE_URL = os.getenv("https://cmqiuyqpzcdwgqgkgmdc.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcWl1eXFwemNkd2dxZ2tnbWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjAyNDgsImV4cCI6MjA3MTA5NjI0OH0.JyqSexwA9INcc3HjNemLUhveCQzY-AAplD8YHACkZP0")
supabase: Client = create_client(https://cmqiuyqpzcdwgqgkgmdc.supabase.co, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcWl1eXFwemNkd2dxZ2tnbWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjAyNDgsImV4cCI6MjA3MTA5NjI0OH0.JyqSexwA9INcc3HjNemLUhveCQzY-AAplD8YHACkZP0)

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"status": "error", "message": "Username obbligatorio"}), 400

    existing = supabase.table("profiles").select("*").eq("username", username).execute()
    if existing.data:
        return jsonify({"status": "error", "message": "Username già registrato"}), 400

    res = supabase.table("profiles").insert({"username": username}).execute()
    user = res.data[0]
    session["user"] = user
    return jsonify({"status": "ok", "user": user})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    res = supabase.table("profiles").select("*").eq("username", username).execute()
    if res.data:
        session["user"] = res.data[0]
        return jsonify({"status": "ok", "user": res.data[0]})
    return jsonify({"status": "error", "message": "Utente non trovato"}), 404

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"status": "ok", "message": "Logout effettuato"})

@app.route("/idea", methods=["POST"])
def add_idea():
    user = session.get("user")
    if not user:
        return jsonify({"status": "error", "message": "Devi fare login"}), 403

    data = request.get_json()
    content = data.get("content", "").strip()
    if content:
        res = supabase.table("ideas").insert({
            "content": content,
            "user_id": user["id"]
        }).execute()
        return jsonify({"status": "ok", "idea": res.data})
    return jsonify({"status": "error", "message": "Nessun contenuto ricevuto"}), 400

@app.route("/ideas", methods=["GET"])
def list_ideas():
    res = supabase.table("ideas").select("id, content, user_id, created_at").order("created_at", desc=True).execute()
    ideas = res.data
    users = {u["id"]: u["username"] for u in supabase.table("profiles").select("id, username").execute().data}
    for idea in ideas:
        idea["username"] = users.get(idea["user_id"], "Anonimo")
    return jsonify({"ideas": ideas})


# 🔹 Solo un admin può resettare la lavagna
@app.route("/reset", methods=["POST"])
def reset():
    user = session.get("user")
    if not user or not user.get("is_admin"):
        return jsonify({"status": "error", "message": "Non sei autorizzato a resettare la lavagna"}), 403
    try:
        # Chiama la funzione SQL creata nel Supabase SQL Editor
        supabase.rpc("reset_ideas").execute()
        return jsonify({"status": "ok", "message": "Lavagna resettata con successo"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
