import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection

# Simple in-memory token store: { token: user_id }
# Note: this resets if the server restarts — fine for learning, but a real
# production app would store sessions in the database too.
ACTIVE_SESSIONS = {}

def register_user(username, password):
    if not username or not password:
        return {"success": False, "error": "Username and password are required."}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "error": "That username is already taken."}

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    conn.commit()
    conn.close()
    return {"success": True}


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return {"success": False, "error": "Invalid username or password."}

    token = secrets.token_hex(24)
    ACTIVE_SESSIONS[token] = user["id"]
    return {"success": True, "token": token, "username": user["username"]}


def get_user_id_from_token(token):
    return ACTIVE_SESSIONS.get(token)


def logout_user(token):
    ACTIVE_SESSIONS.pop(token, None)