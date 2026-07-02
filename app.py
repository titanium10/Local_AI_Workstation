from flask import Flask, render_template, request, jsonify, session, Response, send_from_directory
import sqlite3
import uuid
import datetime
import requests
import json
import os
import base64
import time
import tempfile
import asyncio
import queue
import threading

os.environ['PYTHONUNBUFFERED'] = '1'

import chromadb
from pypdf import PdfReader

import whisper
import edge_tts

whisper_model = whisper.load_model("base")

app = Flask(__name__)
app.secret_key = "samrat-ai-secret-key-2025"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DB_FILE = "chats.db"
CHROMA_PATH = r"C:\Users\samra\OneDrive\Desktop\Chroma DB Real"
UPLOADS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="rag_docs")

live_stats = {
    "is_generating": False,
    "tokens_this_response": 0,
    "last_tps": 0.0,
    "last_model": "",
    "generation_start": None,
}

# ── Dynamic Concurrency Queue (FIFO request queue) ────────────────────────
# Your RTX 5070 8GB can really only run ONE Ollama generation at a time.
# If two people hit /api/chat in the same second (two friends through
# ngrok), without a queue Ollama would either crash, hang, or silently
# serialize requests with zero feedback to either person.
#
# queue_status tracks every in-flight ticket: {ticket_id: {state, created_at}}
# state is one of: "waiting" -> "processing" -> "done"
queue_status = {}
queue_lock = threading.Lock()

# This is the ACTUAL resource being protected. Only one thread at a time
# may hold this lock, and holding it is what "gives permission" to talk
# to Ollama. Everything else (queue_status, position numbers) is just
# bookkeeping so the frontend can show "you're #2" — this lock is what
# guarantees correctness even if that bookkeeping had a bug somewhere.
ollama_generation_lock = threading.Lock()

def enqueue_ticket():
    """
    Called at the start of every /api/chat request. Creates a new ticket,
    registers it as 'waiting', and returns its id — like pulling a
    numbered ticket at a deli counter.
    """
    ticket_id = str(uuid.uuid4())
    with queue_lock:
        queue_status[ticket_id] = {
            "state": "waiting",
            "created_at": time.time(),
        }
    return ticket_id

def get_queue_position(ticket_id):
    """Returns this ticket's 1-indexed position in line, or None if unknown."""
    with queue_lock:
        if ticket_id not in queue_status:
            return None
        active = [
            (tid, info) for tid, info in queue_status.items()
            if info["state"] in ("waiting", "processing")
        ]
        active.sort(key=lambda x: x[1]["created_at"])
        for i, (tid, info) in enumerate(active):
            if tid == ticket_id:
                return i + 1
        return None

def wait_for_turn(ticket_id, timeout=300):
    """
    Blocks the current request thread until it's this ticket's turn to
    use Ollama. Returns True once granted, False if we timed out (300s
    default — protects against a wedged request hanging everyone forever).

    Only the ticket at the front of the sorted line ever attempts to
    acquire the lock, so there's no risk of two tickets racing for it.
    We poll every 0.3s rather than a more "clever" wake-up mechanism —
    simple to reason about, hard to get subtly wrong.
    """
    start = time.time()
    while time.time() - start < timeout:
        with queue_lock:
            active = [
                (tid, info) for tid, info in queue_status.items()
                if info["state"] in ("waiting", "processing")
            ]
            active.sort(key=lambda x: x[1]["created_at"])
            is_my_turn = bool(active) and active[0][0] == ticket_id

        if is_my_turn:
            acquired = ollama_generation_lock.acquire(timeout=0.5)
            if acquired:
                with queue_lock:
                    queue_status[ticket_id]["state"] = "processing"
                return True

        time.sleep(0.3)

    return False

def release_ticket(ticket_id):
    """
    Called once generation is fully finished (success, error, or the user
    hit stop). Releases the lock so the next person in line gets their
    turn, and marks this ticket 'done'.

    Wrapped in try/finally at every call site — if we ever failed to
    release the lock, every future request would wait forever, taking
    down the app for everyone. That's exactly the failure mode a queue
    is supposed to prevent, not cause.
    """
    with queue_lock:
        if ticket_id in queue_status:
            queue_status[ticket_id]["state"] = "done"
    if ollama_generation_lock.locked():
        try:
            ollama_generation_lock.release()
        except RuntimeError:
            pass

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
    # Existing migrations
    try: c.execute("ALTER TABLE chats ADD COLUMN doc_name TEXT")
    except: pass
    try: c.execute("ALTER TABLE chats ADD COLUMN image_file TEXT")
    except: pass
    # NEW: pinned chats. 0=not pinned, 1=pinned. pinned_at tracks when pinned for sort order.
    try: c.execute("ALTER TABLE chats ADD COLUMN pinned INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE chats ADD COLUMN pinned_at TEXT")
    except: pass
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

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def extract_pdf_text(file_bytes):
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def store_chunks_in_chroma(chat_id, chunks, filename):
    try:
        existing = collection.get(where={"chat_id": chat_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except:
        pass
    if not chunks:
        return 0
    ids = [f"{chat_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"chat_id": chat_id, "filename": filename} for _ in chunks]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)

def search_chroma(chat_id, query, n_results=3):
    try:
        existing = collection.get(where={"chat_id": chat_id})
        if not existing["ids"]:
            return ""
        actual_n = min(n_results, len(existing["ids"]))
        results = collection.query(
            query_texts=[query],
            n_results=actual_n,
            where={"chat_id": chat_id}
        )
        chunks = results["documents"][0]
        return "\n---\n".join(chunks)
    except Exception as e:
        print(f"Chroma search error: {e}")
        return ""

@app.route("/")
def index():
    get_user_id()
    return render_template("index2.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_FOLDER, filename)

# ── NEW FEATURE 20: Ollama connection status check ──────────────────────
# Frontend polls this every 10 seconds to show a green/red dot.
# We just hit Ollama's /api/tags endpoint with a short timeout.
# If it responds → online. If timeout/error → offline.
@app.route("/api/ollama-status")
def ollama_status():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            # Also return the model list so we know what's available
            data = r.json()
            return jsonify({"online": True, "models": [m["name"] for m in data.get("models", [])]})
        return jsonify({"online": False})
    except:
        return jsonify({"online": False})

# ── Concurrency queue status endpoint ─────────────────────────────────────
# The frontend polls this (lightweight, no GPU work involved) to display
# "you are position #2 in queue" while its main /api/chat request is
# blocked waiting for its turn. This is a plain read of the queue_status
# dict — it never touches Ollama, so it stays fast even while a
# generation is in progress.
@app.route("/api/queue/status/<ticket_id>")
def queue_status_endpoint(ticket_id):
    with queue_lock:
        info = queue_status.get(ticket_id)
    if not info:
        # Ticket doesn't exist (already cleaned up, or never existed) —
        # treat this as "not waiting", frontend just won't show a queue banner.
        return jsonify({"state": "unknown", "position": None})
    position = get_queue_position(ticket_id)
    return jsonify({"state": info["state"], "position": position})

# Stats dashboard (unchanged from original)
@app.route("/stats")
def stats():
    conn = get_db()
    total_messages = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE role IN ('user', 'assistant')"
    ).fetchone()[0]
    total_chats = conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM chats").fetchone()[0]
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    messages_today = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE role='user' AND created_at LIKE ?",
        (today + "%",)
    ).fetchone()[0]
    busiest = conn.execute(
        """SELECT strftime('%Y-%m-%d', created_at) as day, COUNT(*) as cnt
           FROM messages WHERE role='user'
           GROUP BY day ORDER BY cnt DESC LIMIT 1"""
    ).fetchone()
    busiest_day = f"{busiest['day']} ({busiest['cnt']} messages)" if busiest else "No data yet"
    last7 = conn.execute(
        """SELECT strftime('%Y-%m-%d', created_at) as day, COUNT(*) as cnt
           FROM messages WHERE role='user'
           AND created_at >= date('now', '-7 days')
           GROUP BY day ORDER BY day ASC"""
    ).fetchall()
    conn.close()

    current_tps = 0.0
    if live_stats["is_generating"] and live_stats["generation_start"]:
        elapsed = time.time() - live_stats["generation_start"]
        if elapsed > 0 and live_stats["tokens_this_response"] > 0:
            current_tps = live_stats["tokens_this_response"] / elapsed

    html = f"""<!DOCTYPE html>
<html><head><title>Samrat's AI — Stats</title>
<meta http-equiv="refresh" content="3">
<style>
body {{ font-family: 'Courier New', monospace; background: #0a0a0f; color: #e0e0e0; padding: 40px; }}
h1 {{ color: #7f77dd; margin-bottom: 30px; }}
h2 {{ color: #7f77dd; margin-top: 30px; font-size: 16px; text-transform: uppercase; letter-spacing: 2px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
.card {{ background: #13131a; border: 1px solid #2a2a3a; border-radius: 12px; padding: 20px; }}
.card .label {{ color: #888; font-size: 12px; margin-bottom: 8px; }}
.card .value {{ color: #fff; font-size: 28px; font-weight: bold; }}
.live {{ border-color: {'#7f77dd' if live_stats['is_generating'] else '#2a2a3a'}; }}
.status-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%;
               background: {'#7f77dd' if live_stats['is_generating'] else '#333'};
               margin-right: 8px;
               {'animation: pulse 1s infinite;' if live_stats['is_generating'] else ''} }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
.bar-wrap {{ margin: 6px 0; }}
.bar-label {{ font-size: 12px; color: #888; margin-bottom: 3px; }}
.bar {{ height: 20px; background: #7f77dd; border-radius: 4px; min-width: 4px; }}
.footer {{ color: #444; font-size: 12px; margin-top: 40px; }}
</style></head><body>
<h1>⚡ Samrat's AI — Dashboard</h1>
<p style="color:#555; margin-top:-20px; margin-bottom:30px;">Auto-refreshes every 3 seconds</p>
<h2>📊 Usage Stats</h2>
<div class="grid">
<div class="card"><div class="label">Total Messages</div><div class="value">{total_messages:,}</div></div>
<div class="card"><div class="label">Total Chats</div><div class="value">{total_chats:,}</div></div>
<div class="card"><div class="label">Unique Users</div><div class="value">{total_users:,}</div></div>
<div class="card"><div class="label">Messages Today</div><div class="value">{messages_today:,}</div></div>
<div class="card"><div class="label">Busiest Day</div><div class="value" style="font-size:16px;">{busiest_day}</div></div>
</div>
<h2>🔴 Live Generation</h2>
<div class="grid">
<div class="card live"><div class="label"><span class="status-dot"></span>Status</div><div class="value" style="font-size:20px;">{'🟣 Generating...' if live_stats['is_generating'] else '⚫ Idle'}</div></div>
<div class="card live"><div class="label">Tokens This Response</div><div class="value">{live_stats['tokens_this_response']:,}</div></div>
<div class="card live"><div class="label">Current TPS</div><div class="value">{current_tps:.1f} <span style="font-size:14px;color:#888;">t/s</span></div></div>
<div class="card live"><div class="label">Last Completed TPS</div><div class="value">{live_stats['last_tps']:.1f} <span style="font-size:14px;color:#888;">t/s</span></div></div>
<div class="card live"><div class="label">Model</div><div class="value" style="font-size:18px;">{live_stats['last_model'] or '—'}</div></div>
</div>
<h2>📅 Last 7 Days</h2>
<div style="background:#13131a; border:1px solid #2a2a3a; border-radius:12px; padding:20px;">"""
    max_count = max([r['cnt'] for r in last7], default=1)
    for row in last7:
        bar_width = int((row['cnt'] / max_count) * 300)
        html += f'<div class="bar-wrap"><div class="bar-label">{row["day"]} — {row["cnt"]} messages</div><div class="bar" style="width:{bar_width}px;"></div></div>'
    if not last7:
        html += "<p style='color:#555;'>No messages in the last 7 days yet.</p>"
    html += f'</div><div class="footer">Last updated: {datetime.datetime.now().strftime("%H:%M:%S")}</div></body></html>'
    return html

# ── MODIFIED: GET /api/chats — now returns pinned status + message count ─
# Pinned chats sorted first, then by created_at DESC for the rest.
# Each chat now also includes msg_count for the badge in sidebar.
@app.route("/api/chats", methods=["GET"])
def get_chats():
    uid = get_user_id()
    conn = get_db()
    chats = conn.execute(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM messages m WHERE m.chat_id = c.id AND m.role IN ('user','assistant')) AS msg_count
           FROM chats c
           WHERE c.user_id=?
           ORDER BY COALESCE(c.pinned, 0) DESC, c.created_at DESC""",
        (uid,)
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
    # Note: explicit column names so it survives schema migrations
    conn.execute(
        "INSERT INTO chats (id, user_id, name, created_at, doc_name, image_file, pinned, pinned_at) VALUES (?,?,?,?,?,?,?,?)",
        (chat_id, uid, name, now, None, None, 0, None)
    )
    conn.commit()
    conn.close()
    return jsonify({"id": chat_id, "name": name})

# ── NEW FEATURE 3: PATCH /api/chats/<chat_id> — rename or pin/unpin ──────
# Frontend calls this when user clicks Rename or Pin in the "..." menu.
# Body can have {"name": "new name"} or {"pinned": true/false}
@app.route("/api/chats/<chat_id>", methods=["PATCH"])
def update_chat(chat_id):
    uid = get_user_id()
    data = request.json or {}
    conn = get_db()

    # Verify this chat belongs to the current user (security)
    chat_row = conn.execute(
        "SELECT id FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404

    if "name" in data:
        new_name = data["name"].strip()[:100]  # cap at 100 chars
        if new_name:
            conn.execute("UPDATE chats SET name=? WHERE id=?", (new_name, chat_id))

    if "pinned" in data:
        pinned_val = 1 if data["pinned"] else 0
        pinned_at = datetime.datetime.now().isoformat() if pinned_val else None
        conn.execute("UPDATE chats SET pinned=?, pinned_at=? WHERE id=?",
                     (pinned_val, pinned_at, chat_id))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    uid = get_user_id()
    conn = get_db()
    chat_row = conn.execute("SELECT image_file FROM chats WHERE id=?", (chat_id,)).fetchone()
    if chat_row and chat_row["image_file"]:
        img_path = os.path.join(UPLOADS_FOLDER, chat_row["image_file"])
        if os.path.exists(img_path):
            os.remove(img_path)
    conn.execute("DELETE FROM messages WHERE chat_id=?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id=? AND user_id=?", (chat_id, uid))
    conn.commit()
    conn.close()
    try:
        existing = collection.get(where={"chat_id": chat_id})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except:
        pass
    return jsonify({"ok": True})

# ── MODIFIED: GET messages — now returns id + created_at for timestamps + edit ──
@app.route("/api/chats/<chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    conn = get_db()
    msgs = conn.execute(
        "SELECT id, role, content, created_at FROM messages WHERE chat_id=? ORDER BY id",
        (chat_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(m) for m in msgs])

# ── NEW FEATURE 5: Export chat as markdown ──────────────────────────────
# Returns a .md file the browser downloads. Format is clean readable markdown
# with timestamps so it's actually useful as a record.
@app.route("/api/chats/<chat_id>/export")
def export_chat(chat_id):
    uid = get_user_id()
    conn = get_db()
    chat_row = conn.execute(
        "SELECT * FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404
    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE chat_id=? ORDER BY id",
        (chat_id,)
    ).fetchall()
    conn.close()

    # Build the markdown string
    md = f"# {chat_row['name']}\n\n"
    md += f"_Exported from Samrat's AI on {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}_\n\n---\n\n"
    for m in msgs:
        # Format the timestamp nicely
        try:
            ts = datetime.datetime.fromisoformat(m['created_at']).strftime('%H:%M')
        except:
            ts = ""
        role = "👤 You" if m['role'] == 'user' else "🤖 AI"
        md += f"### {role} `{ts}`\n\n{m['content']}\n\n---\n\n"

    # Make a safe filename from the chat name
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in chat_row['name'])[:50]
    filename = f"{safe_name}.md"

    return Response(
        md,
        mimetype="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# ── NEW FEATURE 9 helper: Delete a single message ───────────────────────
# Used by the edit feature — when user edits their last message, we delete
# the old user message + the AI response, then send the new prompt fresh.
@app.route("/api/chats/<chat_id>/messages/<int:msg_id>", methods=["DELETE"])
def delete_message(chat_id, msg_id):
    uid = get_user_id()
    conn = get_db()
    # Security: verify the chat belongs to the user
    chat_row = conn.execute(
        "SELECT id FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404
    conn.execute("DELETE FROM messages WHERE id=? AND chat_id=?", (msg_id, chat_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── NEW FEATURE 16: Regenerate the last AI response ─────────────────────
# Deletes the last assistant message so the user can hit send again
# (frontend then re-triggers /api/chat with the last user message).
@app.route("/api/chats/<chat_id>/regenerate", methods=["POST"])
def regenerate(chat_id):
    uid = get_user_id()
    conn = get_db()
    chat_row = conn.execute(
        "SELECT id FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404

    # Find the last assistant message
    last_ai = conn.execute(
        "SELECT id FROM messages WHERE chat_id=? AND role='assistant' ORDER BY id DESC LIMIT 1",
        (chat_id,)
    ).fetchone()

    # Find the last user message (we'll return its content so frontend can re-send)
    last_user = conn.execute(
        "SELECT content FROM messages WHERE chat_id=? AND role='user' ORDER BY id DESC LIMIT 1",
        (chat_id,)
    ).fetchone()

    if last_ai:
        conn.execute("DELETE FROM messages WHERE id=?", (last_ai["id"],))
    # Also delete the last user message — frontend will re-add it via /api/chat
    if last_user:
        last_user_row = conn.execute(
            "SELECT id FROM messages WHERE chat_id=? AND role='user' ORDER BY id DESC LIMIT 1",
            (chat_id,)
        ).fetchone()
        if last_user_row:
            conn.execute("DELETE FROM messages WHERE id=?", (last_user_row["id"],))

    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "last_user_message": last_user["content"] if last_user else ""
    })

# ── NEW FEATURE 10: Auto-generate a smart chat title using Ollama ───────
# Called after the first AI response. Asks llama3 to summarize the chat
# in 3-5 words for a clean title. Falls back to first 30 chars on error.
@app.route("/api/chats/<chat_id>/title", methods=["POST"])
def generate_title(chat_id):
    uid = get_user_id()
    conn = get_db()
    chat_row = conn.execute(
        "SELECT * FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404

    # Get the first user message
    first_user = conn.execute(
        "SELECT content FROM messages WHERE chat_id=? AND role='user' ORDER BY id ASC LIMIT 1",
        (chat_id,)
    ).fetchone()
    conn.close()

    if not first_user:
        return jsonify({"name": chat_row["name"]})

    # Ask Ollama for a short title — non-streaming, fast call
    try:
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{
                    "role": "user",
                    "content": f"Generate a 3-5 word title for this conversation. Respond with ONLY the title, no quotes or punctuation:\n\n{first_user['content'][:500]}"
                }],
                "stream": False
            },
            timeout=15
        )
        result = r.json()
        title = result["message"]["content"].strip().strip('"\'.')[:60]
        # Filter out common AI babbling
        if not title or len(title) < 3:
            raise Exception("bad title")
    except:
        # Fallback to first 30 chars of the user message
        title = first_user["content"][:30] + ("..." if len(first_user["content"]) > 30 else "")

    conn = get_db()
    conn.execute("UPDATE chats SET name=? WHERE id=?", (title, chat_id))
    conn.commit()
    conn.close()
    return jsonify({"name": title})

@app.route("/api/chats/<chat_id>/upload", methods=["POST"])
def upload_file(chat_id):
    uid = get_user_id()
    conn = get_db()
    chat_row = conn.execute(
        "SELECT * FROM chats WHERE id=? AND user_id=?", (chat_id, uid)
    ).fetchone()
    if not chat_row:
        conn.close()
        return jsonify({"error": "Chat not found"}), 404
    file = request.files.get("file")
    if not file:
        conn.close()
        return jsonify({"error": "No file provided"}), 400
    filename = file.filename
    file_bytes = file.read()
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        text = extract_pdf_text(file_bytes)
        if not text.strip():
            conn.close()
            return jsonify({"error": "Could not extract text from PDF. It may be a scanned image PDF."}), 400
        chunks = chunk_text(text)
        num_chunks = store_chunks_in_chroma(chat_id, chunks, filename)
        conn.execute("UPDATE chats SET doc_name=? WHERE id=?", (filename, chat_id))
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "type": "pdf", "filename": filename, "chunks": num_chunks})
    elif ext in ["png", "jpg", "jpeg", "gif", "webp"]:
        saved_filename = f"{uuid.uuid4()}.{ext}"
        save_path = os.path.join(UPLOADS_FOLDER, saved_filename)
        with open(save_path, "wb") as f:
            f.write(file_bytes)
        if chat_row["image_file"]:
            old_path = os.path.join(UPLOADS_FOLDER, chat_row["image_file"])
            if os.path.exists(old_path):
                os.remove(old_path)
        conn.execute(
            "UPDATE chats SET doc_name=?, image_file=? WHERE id=?",
            (filename, saved_filename, chat_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "type": "image", "filename": filename, "url": f"/uploads/{saved_filename}"})
    else:
        conn.close()
        return jsonify({"error": f"Unsupported file type: .{ext}. Use PDF or image files."}), 400

# ── MODIFIED: /api/chat — now accepts user persona from request body ────
# Frontend sends `persona` string from settings panel — it gets injected
# into the system prompt so the AI knows who it's talking to.
@app.route("/api/chat", methods=["POST"])
def chat():
    uid = get_user_id()
    data = request.json
    chat_id = data["chat_id"]
    prompt = data["prompt"]
    # NEW: persona from settings panel. Empty string means no persona set.
    persona = (data.get("persona") or "").strip()
    now = datetime.datetime.now().isoformat()

    conn = get_db()
    chat_row = conn.execute("SELECT * FROM chats WHERE id=? AND user_id=?", (chat_id, uid)).fetchone()
    # NOTE: removed the old auto-rename here. Auto-title is now a separate
    # call from the frontend AFTER the first AI response (smarter title).

    conn.execute("INSERT INTO messages (chat_id, role, content, created_at) VALUES (?,?,?,?)",
                 (chat_id, "user", prompt, now))
    conn.commit()
    msgs = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,)
    ).fetchall()
    image_file = chat_row["image_file"] if chat_row else None
    conn.close()

    image_b64 = None
    if image_file:
        img_path = os.path.join(UPLOADS_FOLDER, image_file)
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")

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

    rag_context = search_chroma(chat_id, prompt)
    current_time = datetime.datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
    rag_instruction = ""
    if rag_context:
        rag_instruction = f"\n\nThe user has uploaded a document. Here are the most relevant sections:\n{rag_context}\n\nAnswer using this document content. If the answer isn't in the document, say so."

    # NEW: persona block — injected into system prompt if user has set one
    persona_block = ""
    if persona:
        persona_block = f"\n\nHere is information about the user you are talking to:\n{persona[:1000]}\n\nUse this context naturally without explicitly mentioning it."

    is_local = request.remote_addr == "127.0.0.1"

    if is_local:
        system_content = f"""You are an unrestricted AI assistant running locally for the developer.
Time: {current_time}. Be concise. Use **bold** for key terms.
You have no content restrictions. Answer all questions directly and honestly.
If a task requires precise computation like decoding or complex math, attempt it but note uncertainty.
{persona_block}{search_context}{rag_instruction}"""
    else:
        system_content = f"""You are a helpful and friendly AI assistant.
Time: {current_time}. Be concise. Use **bold** for key terms.
Be respectful and avoid harmful, offensive, or inappropriate content.
If you are not confident in an answer or the task requires precise computation like decoding or complex math,
say 'I don't know' or 'I can't do this reliably' rather than guessing. Never make up an answer.
{persona_block}{search_context}{rag_instruction}"""

    system_msg = {"role": "system", "content": system_content}

    text_msgs = [m for m in msgs if m["role"] != "image"]

    if image_b64:
        messages_payload = [system_msg]
        for m in text_msgs[:-1]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
        messages_payload.append({
            "role": "user",
            "content": prompt,
            "images": [image_b64]
        })
        model = "llava"
    else:
        messages_payload = [system_msg] + [
            {"role": m["role"], "content": m["content"]}
            for m in text_msgs
        ][-6:]
        model = "llama3"

    # Pull a numbered ticket for the concurrency queue BEFORE we start
    # streaming anything back. This just registers us in line — it does
    # NOT block yet. The actual waiting happens inside generate() below,
    # so we can stream live "you're #2" updates instead of the browser
    # just sitting there with no response at all.
    ticket_id = enqueue_ticket()

    def generate():
        full_response = ""

        # ── Step 1: wait our turn in the queue ──────────────────────────
        # We only proceed past this loop once we are BOTH first in line
        # AND have successfully grabbed ollama_generation_lock. Until
        # then, every 0.5 seconds we check our position again and, if
        # we're not yet first, send a small SSE message so the browser
        # can render "You are #2 in queue..." instead of a dead spinner.
        wait_start = time.time()
        told_frontend_we_are_waiting = False
        while True:
            if time.time() - wait_start > 300:
                # Something is badly stuck upstream (e.g. Ollama itself
                # hung). Rather than wait forever, fail loudly so the
                # user isn't left staring at a frozen screen.
                yield f"data: {json.dumps({'error': 'Timed out waiting in queue. Try again.'})}\n\n"
                release_ticket(ticket_id)
                return

            position = get_queue_position(ticket_id)
            if position == 1:
                # We're at the front — try to grab the actual GPU lock.
                if ollama_generation_lock.acquire(timeout=0.5):
                    with queue_lock:
                        queue_status[ticket_id]["state"] = "processing"
                    break  # got it — fall through to real generation below
            else:
                told_frontend_we_are_waiting = True
                yield f"data: {json.dumps({'queued': True, 'position': position})}\n\n"

            time.sleep(0.5)

        # Let the frontend know it's no longer waiting, now that we've
        # actually started (only needed if we ever told it we were queued).
        if told_frontend_we_are_waiting:
            yield f"data: {json.dumps({'queued': False})}\n\n"

        # ── Step 2: the real generation, exactly as before ──────────────
        live_stats["is_generating"] = True
        live_stats["tokens_this_response"] = 0
        live_stats["generation_start"] = time.time()
        live_stats["last_model"] = model

        try:
            r = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": model, "messages": messages_payload, "stream": True},
                stream=True,
                timeout=(10, 120)
            )
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        word = chunk["message"]["content"]
                        full_response += word
                        live_stats["tokens_this_response"] += 1
                        yield f"data: {json.dumps({'token': word})}\n\n"
                    if chunk.get("done") and "eval_count" in chunk and "eval_duration" in chunk:
                        eval_count = chunk["eval_count"]
                        eval_duration = chunk["eval_duration"]
                        if eval_duration > 0:
                            live_stats["last_tps"] = eval_count / (eval_duration / 1_000_000_000)

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

        finally:
            # This ALWAYS runs — success, error, or the user hitting stop
            # (which aborts the HTTP connection and triggers GeneratorExit,
            # which Python routes through this same finally block). That
            # guarantee is exactly why we release the lock here instead of
            # only after the try block's happy path: a stuck lock would
            # freeze the queue for every single person after this request.
            live_stats["is_generating"] = False
            release_ticket(ticket_id)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff"
        }
    )

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio provided"}), 400
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name
    try:
        result = whisper_model.transcribe(tmp_path, fp16=False)
        text = result["text"].strip()
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.route("/api/speak", methods=["POST"])
def speak():
    data = request.json
    text = data.get("text", "")
    voice = data.get("voice", "en-US-GuyNeural")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    async def generate_speech():
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    try:
        audio_data = asyncio.run(generate_speech())
        from flask import send_file
        import io
        return send_file(
            io.BytesIO(audio_data),
            mimetype="audio/mpeg",
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=False, port=5000, threaded=True)
