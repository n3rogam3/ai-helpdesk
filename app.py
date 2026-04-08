from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

AUTHOR = "David Pantucek"

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

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

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")

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

        response.raise_for_status()
        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        return jsonify({
            "prompt": prompt,
            "answer": answer,
            "model": "gemma3:27b"
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))
    app.run(host="0.0.0.0", port=port)