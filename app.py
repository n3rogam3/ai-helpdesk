from flask import Flask, request, jsonify, render_template
import os
import requests
from datetime import datetime
import psycopg2

app = Flask(__name__)

AUTHOR = "David Pantucek"

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(database_url)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ai_logs (
                id SERIAL PRIMARY KEY,
                prompt TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("DB init error:", e)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "author": AUTHOR,
        "time": datetime.now().isoformat()
    }), 200

@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify({"error": "Chybi prompt"}), 400

    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    base_url = (os.getenv("OPENAI_BASE_URL") or "https://kurim.ithope.eu/v1").strip()

    if not api_key:
        return jsonify({"error": "Neni nastavena OPENAI_API_KEY"}), 500

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma3:27b",
                "messages": [
                    {
                        "role": "system",
                        "content": "Odpovidej kratce, jasne a cesky."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 120
            },
            timeout=30
        )

        if not response.ok:
            return jsonify({
                "error": "AI sluzba vratila chybu",
                "status_code": response.status_code,
                "response_text": response.text
            }), 500

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO ai_logs (prompt, answer) VALUES (%s, %s)",
                (prompt, answer)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("DB insert error:", e)

        return jsonify({
            "answer": answer
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Nepodarilo se spojit s AI sluzbou",
            "detail": str(e)
        }), 500
    except (KeyError, IndexError, TypeError, ValueError) as e:
        return jsonify({
            "error": "Neplatna odpoved od AI sluzby",
            "detail": str(e)
        }), 500

init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))
    app.run(host="0.0.0.0", port=port)
