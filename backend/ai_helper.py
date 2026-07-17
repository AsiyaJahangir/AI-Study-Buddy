import requests
import urllib.parse
import re

def call_ai(prompt):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            text = response.text
            text = re.split(r"---\s*\n\s*🌸", text)[0].strip()
            text = re.split(r"\*\*Support Pollinations", text)[0].strip()
            return text
        elif response.status_code == 429:
            return "The AI service is rate-limited right now (free tier allows about 1 request per 15 seconds). Please wait a moment and try again."
        else:
            return f"Error: the AI service returned status {response.status_code}. Try again in a moment."
    except Exception as e:
        return f"Error reaching AI service: {str(e)}"


def summarize_notes(notes_text):
    prompt = (
        "Summarize the following study notes into clear, concise bullet points. "
        "Keep the key concepts and important details, but make it shorter and easier to review. "
        "Do not add a title, just give the bullet points:\n\n"
        f"{notes_text}"
    )
    return call_ai(prompt)


def generate_quiz(notes_text):
    prompt = (
        "Based on the following study notes, create exactly 5 quiz questions to test understanding. "
        "Number them 1 to 5. Mix multiple choice and short answer questions. "
        "Provide the correct answer right after each question, labeled 'Answer:'. "
        "Do not add extra commentary before or after:\n\n"
        f"{notes_text}"
    )
    return call_ai(prompt)
import json

import json

def extract_chart_data(notes_text):
    prompt = (
        "Analyze the following notes and decide the BEST way to visualize them. Choose exactly one type:\n\n"
        "1. If the notes contain numeric data, statistics, or comparisons between a few categories, "
        "respond with ONLY this JSON format (chart_type can be 'bar', 'line', or 'pie' — pick whichever "
        "best fits the data):\n"
        '{"type": "chart", "chart_type": "bar", "title": "short title", "labels": ["a", "b"], "values": [10, 20]}\n\n'
        "2. If the notes describe a process, sequence of steps, a cycle, or a decision flow (e.g. 'first X happens, "
        "then Y, then Z' or cause-and-effect steps), respond with ONLY this JSON format using valid Mermaid "
        "flowchart syntax in the 'mermaid' field (use short node labels, 'TD' direction, plain arrows -->):\n"
        '{"type": "flowchart", "title": "short title", "mermaid": "flowchart TD\\nA[Start] --> B[Step]\\nB --> C[End]"}\n\n'
        "3. If there is genuinely nothing visual to represent (pure abstract text with no data or process), "
        "respond with ONLY this:\n"
        '{"type": "none"}\n\n'
        "Respond with ONLY the JSON object, no explanation, no markdown formatting, no code fences.\n\n"
        f"Notes:\n{notes_text}"
    )
    raw = call_ai(prompt)

    try:
        json_start = raw.find("{")
        json_end = raw.rfind("}") + 1
        json_str = raw[json_start:json_end]
        data = json.loads(json_str)
        if data.get("type") == "none":
            return None
        return data
    except Exception:
        return None