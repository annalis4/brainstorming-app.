from flask import Flask, request, jsonify, render_template, session
from supabase import create_client, Client
import os

# Inizializza Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")  # per gestire le sessioni

# Configura Supabase con variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://cmqiuyqpzcdwgqgkgmdc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcWl1eXFwemNkd2dxZ2tnbWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU1MjAyNDgsImV4cCI6MjA3MTA5NjI0OH0.JyqSexwA9INcc3HjNemLUhveCQzY-AAplD8YHACkZP0")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rotta principale
@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

# Registrazione nuovo utente
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"status": "error", "message": "Username obbligatorio"}), 400

    try:
        res = supabase.table("profiles").insert({"username": username}).execute()
        if res.data:
            user = res.data[0]
            session["user"] = user
            return jsonify({"status": "ok", "user": user})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Login utente esistente
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    res = supabase.table("profiles").select("*").eq("username", username).execute()
    if res.data:
        session["user"] = res.data[0]
        return jsonify({"status": "ok", "user": res.data[0]})
    return jsonify({"status": "error", "message": "Utente non trovato"}), 404

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"status": "ok", "message": "Logout effettuato"})

# Inserimento idea legata a utente
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

# Lista di tutte le idee (con autore)
@app.route("/ideas", methods=["GET"])
def list_ideas():
    res = supabase.rpc(
        "exec",
        {
            "sql": """
                select i.id, i.content, i.count, i.pos_x, i.pos_y, i.created_at,
                       p.username
                from ideas i
                left join profiles p on i.user_id = p.id
                order by i.created_at desc;
            """
        }
    ).execute()

    return jsonify({"ideas": res.data})

# Reset lavagna
@app.route("/reset", methods=["POST"])
def reset():
    try:
        res = supabase.table("ideas").delete().neq("id", -1).execute()
        return jsonify({"status": "ok", "deleted": len(res.data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
