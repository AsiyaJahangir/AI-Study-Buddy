from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_helper import summarize_notes, generate_quiz, extract_chart_data
from database import init_db
from auth import register_user, login_user, get_user_id_from_token, logout_user
from chats import (
    create_chat, get_user_chats, chat_belongs_to_user,
    add_message, get_chat_messages, update_chat_title, delete_chat, delete_all_chats
)
import json as json_lib

app = Flask(__name__)
CORS(app)

init_db()

def get_token_from_request():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    return None

def require_login():
    token = get_token_from_request()
    return get_user_id_from_token(token) if token else None


# ---------- AUTH ----------

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    result = register_user(data.get("username", "").strip(), data.get("password", ""))
    return jsonify(result)


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    result = login_user(data.get("username", "").strip(), data.get("password", ""))
    return jsonify(result)


@app.route("/logout", methods=["POST"])
def logout():
    token = get_token_from_request()
    if token:
        logout_user(token)
    return jsonify({"success": True})


# ---------- CHATS ----------

@app.route("/chats", methods=["GET"])
def list_chats():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"chats": get_user_chats(user_id)})


@app.route("/chats", methods=["POST"])
def new_chat():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    chat_id = create_chat(user_id)
    return jsonify({"chat_id": chat_id})


@app.route("/chats/<int:chat_id>/messages", methods=["GET"])
def chat_messages(chat_id):
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    if not chat_belongs_to_user(chat_id, user_id):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"messages": get_chat_messages(chat_id)})


@app.route("/chats/<int:chat_id>", methods=["DELETE"])
def remove_chat(chat_id):
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    if not chat_belongs_to_user(chat_id, user_id):
        return jsonify({"error": "Not found"}), 404
    delete_chat(chat_id)
    return jsonify({"success": True})


@app.route("/chats/clear", methods=["DELETE"])
def clear_all_chats():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    delete_all_chats(user_id)
    return jsonify({"success": True})


# ---------- AI ACTIONS ----------

@app.route("/summarize", methods=["POST"])
def summarize():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    notes = data.get("notes", "")
    chat_id = data.get("chat_id")

    if not notes.strip():
        return jsonify({"result": "Please paste some notes first."})

    if not chat_belongs_to_user(chat_id, user_id):
        return jsonify({"error": "Invalid chat"}), 404

    result = summarize_notes(notes)

    add_message(chat_id, "user", f"[Summarize] {notes[:200]}")
    add_message(chat_id, "assistant", result)
    update_chat_title(chat_id, notes[:40] + "...")

    return jsonify({"result": result})


@app.route("/quiz", methods=["POST"])
def quiz():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    notes = data.get("notes", "")
    chat_id = data.get("chat_id")

    if not notes.strip():
        return jsonify({"result": "Please paste some notes first."})

    if not chat_belongs_to_user(chat_id, user_id):
        return jsonify({"error": "Invalid chat"}), 404

    result = generate_quiz(notes)

    add_message(chat_id, "user", f"[Quiz] {notes[:200]}")
    add_message(chat_id, "assistant", result)
    update_chat_title(chat_id, notes[:40] + "...")

    return jsonify({"result": result})


@app.route("/visualize", methods=["POST"])
def visualize():
    user_id = require_login()
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    notes = data.get("notes", "")
    chat_id = data.get("chat_id")

    if not notes.strip():
        return jsonify({"chart": None, "message": "Please paste some notes first."})

    if not chat_belongs_to_user(chat_id, user_id):
        return jsonify({"error": "Invalid chat"}), 404

    chart_data = extract_chart_data(notes)

    if chart_data:
        add_message(chat_id, "user", f"[Visualize] {notes[:200]}")
        add_message(chat_id, "assistant", "[CHART]" + json_lib.dumps(chart_data))
        return jsonify({"chart": chart_data})
    else:
        return jsonify({"chart": None, "message": "I couldn't find clear numeric data in these notes to chart. Try notes with numbers, stats, or comparisons."})


# ---------- RUN SERVER (must be last) ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)