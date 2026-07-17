# AI Study Buddy

A full-stack AI-powered study assistant that summarizes notes, generates quiz questions, and automatically visualizes information as charts or flowcharts — with user accounts and a ChatGPT-style chat history.

## About

Studying from long, dense notes is hard. AI Study Buddy lets you paste any notes and instantly get a clean summary, a set of quiz questions to test yourself, or a visual representation (bar/line/pie chart for numeric data, or a flowchart for step-by-step processes) — all powered by a real LLM. Every conversation is saved to your account, so you can pick up where you left off, just like ChatGPT.

## Features

- **User accounts** — secure registration and login with hashed passwords (no plain-text passwords ever stored)
- **AI-powered summarization** — condenses long notes into clear bullet points
- **AI-generated quizzes** — creates mixed multiple-choice and short-answer questions from your notes
- **Smart auto-visualization** — the AI decides whether your notes are better shown as a bar/line/pie chart or a flowchart, then renders it live
- **ChatGPT-style sidebar** — every chat is saved per-user; switch between past chats, start new ones, or delete them (individually or all at once)
- **Persistent chat history** — stored in a real database (SQLite), not just the browser

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript (vanilla), [Chart.js](https://www.chartjs.org/) for charts, [Mermaid.js](https://mermaid.js.org/) for flowcharts
- **Backend:** Python, Flask
- **Database:** SQLite (users, chats, messages)
- **Auth:** Werkzeug password hashing + token-based sessions
- **AI:** [Pollinations.ai](https://pollinations.ai) free text-generation API (no signup required)

## Project Structure

```
AI-Study-Buddy/
│
├── frontend/
│   ├── index.html        # Main app (requires login)
│   ├── login.html        # Login / Sign up page
│   ├── style.css
│   ├── auth-style.css
│   ├── script.js
│   └── auth.js
│
├── backend/
│   ├── app.py             # Flask routes
│   ├── auth.py            # Registration, login, token sessions
│   ├── chats.py           # Chat + message database operations
│   ├── database.py        # SQLite schema and connection
│   └── ai_helper.py       # AI prompt logic (summarize, quiz, visualize)
│
└── README.md
```

## Running Locally / in GitHub Codespaces

**1. Start the backend** (Terminal 1)
```bash
cd backend
pip install flask flask-cors requests werkzeug --break-system-packages
python3 database.py   # creates the database (only needed once)
python3 app.py
```
Runs the Flask API on port 5000.

**2. Start the frontend** (Terminal 2 — separate terminal tab, keep the backend running)
```bash
cd frontend
python3 -m http.server 8080
```

**3. Update the backend URL**
In `frontend/script.js` and `frontend/auth.js`, set `BACKEND_URL` to your backend's forwarded address (in Codespaces: the **Ports** tab → port 5000 → Forwarded Address). Make both ports **Public**.

**4. Open the app**
Visit the forwarded URL for port 8080. You'll be redirected to the login/sign-up page automatically if not logged in.

## Security Notes

This is a learning project, so a few things are simplified compared to a production app:
- Session tokens are stored in memory (they reset if the server restarts) rather than in the database
- No rate limiting or HTTPS enforcement beyond what Codespaces provides by default

Passwords themselves **are** properly hashed with Werkzeug's `generate_password_hash`, so real password security fundamentals are in place.

## Future Enhancements

- Persistent server-side sessions (survive backend restarts)
- Flashcard generation mode
- Export summaries/quizzes as PDF
- Dark mode toggle
- Support for uploading PDF/DOCX notes directly

## Author

Created by Asiya Jahangir.