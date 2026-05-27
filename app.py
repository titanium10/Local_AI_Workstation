from flask import Flask, render_template, request, jsonify, session, Response, send_from_directory
import sqlite3
import uuid
import datetime
import requests
import json
import os
import base64

os.environ['PYTHONUNBUFFERED'] = '1'

import chromadb
from pypdf import PdfReader

app = Flask(__name__)
app.secret_key = "samrat-ai-secret-key-2025"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DB_FILE = "chats.db"
CHROMA_PATH = r"C:\Users\samra\OneDrive\Desktop\Chroma DB Real"

# NEW: UPLOADS_FOLDER is where we save image files on disk.
# Instead of storing huge base64 strings in SQLite, we save the actual
# image file here and only store the filename in the database.
# os.path.join builds a path correctly on any OS:
# os.path.join("Local AI", "uploads") → "Local AI\uploads" on Windows
UPLOADS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
# os.path.abspath(__file__) = the full path to app.py
# os.path.dirname(...) = the folder that contains app.py
# So UPLOADS_FOLDER = "C:\Users\samra\OneDrive\Desktop\Local AI\uploads"

# Create the uploads folder if it doesn't exist yet
os.makedirs(UPLOADS_FOLDER, exist_ok=True)
# exist_ok=True means: if the folder already exists, don't crash — just continue

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="rag_docs")

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
    try:
        c.execute("ALTER TABLE chats ADD COLUMN doc_name TEXT")
    except:
        pass
    # NEW: Add image_file column to chats table.
    # This stores the saved filename of the uploaded image, e.g. "abc123.png"
    # We store the filename, not the full path, because paths can change.
    try:
        c.execute("ALTER TABLE chats ADD COLUMN image_file TEXT")
    except:
        pass
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

# NEW: This route serves image files from the uploads folder.
# When the browser requests /uploads/abc123.png, Flask finds that file
# in the UPLOADS_FOLDER and sends it back.
# send_from_directory is Flask's safe way to serve files — it prevents
# attackers from requesting files outside the uploads folder (like ../../passwords.txt)
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOADS_FOLDER, filename)

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
    # CHANGED: Now inserting 6 values — added None for image_file column
    conn.execute("INSERT INTO chats VALUES (?,?,?,?,?,?)", (chat_id, uid, name, now, None, None))
    conn.commit()
    conn.close()
    return jsonify({"id": chat_id, "name": name})

@app.route("/api/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    uid = get_user_id()
    conn = get_db()

    # NEW: Before deleting the chat, get the image_file so we can delete it from disk too
    chat_row = conn.execute("SELECT image_file FROM chats WHERE id=?", (chat_id,)).fetchone()
    if chat_row and chat_row["image_file"]:
        # Build the full path to the image file and delete it
        img_path = os.path.join(UPLOADS_FOLDER, chat_row["image_file"])
        if os.path.exists(img_path):
            os.remove(img_path)
            # os.remove() deletes a file. We check exists() first so we don't crash
            # if the file is already gone.

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

@app.route("/api/chats/<chat_id>/messages", methods=["GET"])
def get_messages(chat_id):
    conn = get_db()
    msgs = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(m) for m in msgs])

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
        # CHANGED: Instead of storing base64 in SQLite, we now save the image
        # as a real file on disk and store just the filename.

        # Generate a unique filename so two users uploading "photo.png" don't
        # overwrite each other. uuid4() creates a random unique ID.
        saved_filename = f"{uuid.uuid4()}.{ext}"
        # Example result: "a3f8c2d1-4b5e-6789-abcd-ef0123456789.png"

        save_path = os.path.join(UPLOADS_FOLDER, saved_filename)
        # Full path: "C:\...\Local AI\uploads\a3f8c2d1-....png"

        with open(save_path, "wb") as f:
            f.write(file_bytes)
        # "wb" = write binary mode. Images are binary data (not text),
        # so we must open the file in binary mode, not regular text mode.

        # If this chat already had an image, delete the old one from disk
        # before storing the new one. We don't want orphaned files piling up.
        if chat_row["image_file"]:
            old_path = os.path.join(UPLOADS_FOLDER, chat_row["image_file"])
            if os.path.exists(old_path):
                os.remove(old_path)

        # Store the saved filename AND the original display name in the database
        conn.execute(
            "UPDATE chats SET doc_name=?, image_file=? WHERE id=?",
            (filename, saved_filename, chat_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "ok": True,
            "type": "image",
            "filename": filename,
            # NEW: return the URL path so the browser can display the image
            # The browser will request /uploads/saved_filename to see it
            "url": f"/uploads/{saved_filename}"
        })

    else:
        conn.close()
        return jsonify({"error": f"Unsupported file type: .{ext}. Use PDF or image files."}), 400

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

    # CHANGED: Read image_file from the chats table directly.
    # This is much cleaner than scanning through all messages for role="image".
    image_file = chat_row["image_file"] if chat_row else None
    conn.close()

    # If there's an image file saved, read it from disk and convert to base64
    # RIGHT NOW, just before sending to llava. This is more reliable than
    # storing base64 in the database because:
    # 1. The file on disk is always the original, clean image data
    # 2. We're not dealing with huge strings being stored/retrieved from SQLite
    image_b64 = None
    if image_file:
        img_path = os.path.join(UPLOADS_FOLDER, image_file)
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")
            # "rb" = read binary mode
            # base64.b64encode converts the raw bytes to base64
            # .decode("utf-8") converts the base64 bytes object to a string

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

    system_msg = {
        "role": "system",
        "content": f"You are a smart AI assistant. Time: {current_time}. Be concise. Use **bold** for key terms. {search_context}{rag_instruction}"
    }

    # Filter out any old "image" role messages — we don't use that system anymore
    text_msgs = [m for m in msgs if m["role"] != "image"]

    if image_b64:
        # CHANGED: Now we build the payload correctly.
        # We send ALL previous text messages normally,
        # then attach the image ONLY to the current (latest) user message.
        # This is the correct way — the image stays attached to the conversation
        # but doesn't get duplicated on every single message.
        messages_payload = [system_msg]

        # Add all messages except the very last one (which is the current user message)
        for m in text_msgs[:-1]:
            messages_payload.append({"role": m["role"], "content": m["content"]})

        # Add the current user message WITH the image
        messages_payload.append({
            "role": "user",
            "content": prompt,
            "images": [image_b64]
            # llava reads this "images" list and processes the image alongside the text
        })

        model = "llava"

    else:
        messages_payload = [system_msg] + [
            {"role": m["role"], "content": m["content"]}
            for m in text_msgs
        ][-6:]
        model = "llama3"

    def generate():
        full_response = ""
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
