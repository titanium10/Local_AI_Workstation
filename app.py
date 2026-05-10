from flask import Flask, render_template, request, jsonify, session, Response
import sqlite3
import uuid
import datetime
import requests
import json
import os

os.environ['PYTHONUNBUFFERED'] = '1'

app = Flask(__name__)
app.secret_key = "samrat-ai-secret-key-2025"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
DB_FILE = "chats.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def get_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        session.permanent = True
    return session["user_id"]

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    get_user_id()
    return render_template("index2.html")

@app.route("/api/chats", methods=["GET"])
def get_chats():
    uid = get_user_id()
    conn = get_db()
    chats = conn.execute(
        "SELECT * FROM chats WHERE user_id=? ORDER BY created_at DESC", (uid,)
    ).fetchall()
    conn.close()
    return jsonify([dict(c) for c in chats])

@app.route("/api/chats", methods=["POST"])
def create_chat():
    uid = get_user_id()
    chat_id = str(uuid.uuid4())
    name = request.json.get("name", "New Conversation")
    now = datetime.datetime.now().isoformat()
    conn = get_db()
    conn.execute("INSERT INTO chats VALUES (?,?,?,?)", (chat_id, uid, name, now))
    conn.commit()
    conn.close()
    return jsonify({"id": chat_id, "name": name})

@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    uid = get_user_id()
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id=? AND user_id=?", (chat_id, uid))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/chats/<chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    conn = get_db()
    msgs = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(m) for m in msgs])

@app.route("/api/chat", methods=["POST"])
def chat():
    uid = get_user_id()
    data = request.json
    chat_id = data["chat_id"]
    prompt = data["prompt"]
    now = datetime.datetime.now().isoformat()

    conn = get_db()
    chat_row = conn.execute("SELECT * FROM chats WHERE id=? AND user_id=?", (chat_id, uid)).fetchone()
    if chat_row and chat_row["name"] == "New Conversation":
        name = prompt[:30] + ("..." if len(prompt) > 30 else "")
        conn.execute("UPDATE chats SET name=? WHERE id=?", (name, chat_id))

    conn.execute("INSERT INTO messages (chat_id, role, content, created_at) VALUES (?,?,?,?)",
                 (chat_id, "user", prompt, now))
    conn.commit()

    msgs = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,)
    ).fetchall()
    conn.close()

    search_context = ""
    search_triggers = ["what", "who", "where", "when", "why", "how", "?", "search", "latest"]
    if any(t in prompt.lower() for t in search_triggers):
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(prompt, max_results=2))
                search_context = "\n".join([r['body'] for r in results])
        except:
            pass

    current_time = datetime.datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
    system_msg = {
        "role": "system",
        "content": f"You are a smart AI assistant. Time: {current_time}. Be concise. Use **bold** for key terms. {search_context}"
    }

    messages_payload = [system_msg] + [{"role": m["role"], "content": m["content"]} for m in msgs][-6:]

    def generate():
        full_response = ""
        try:
            r = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": "llama3", "messages": messages_payload, "stream": True},
                stream=True,
                timeout=(10, 120)
            )
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        word = chunk["message"]["content"]
                        full_response += word
                        yield f"data: {json.dumps({'token': word})}\n\n"

            conn2 = get_db()
            conn2.execute(
                "INSERT INTO messages (chat_id, role, content, created_at) VALUES (?,?,?,?)",
                (chat_id, "assistant", full_response, datetime.datetime.now().isoformat())
            )
            conn2.commit()
            conn2.close()
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff"
        }
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=False, port=5000, threaded=True)
