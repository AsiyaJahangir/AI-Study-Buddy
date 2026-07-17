from database import get_connection

def create_chat(user_id, title="New Chat"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, title) VALUES (?, ?)",
        (user_id, title)
    )
    conn.commit()
    chat_id = cursor.lastrowid
    conn.close()
    return chat_id


def get_user_chats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats


def chat_belongs_to_user(chat_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM chats WHERE id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row["user_id"] == user_id


def add_message(chat_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
        (chat_id, role, content)
    )
    conn.commit()
    conn.close()


def get_chat_messages(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
        (chat_id,)
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages


def update_chat_title(chat_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()


def delete_chat(chat_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


def delete_all_chats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM chats WHERE user_id = ?", (user_id,))
    chat_ids = [row["id"] for row in cursor.fetchall()]
    for chat_id in chat_ids:
        cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()