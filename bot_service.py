import os
import asyncio
import threading
from flask import Flask, request, jsonify
import discord

# =========================
# ENV (Render)
# =========================
DISCORD_TOKEN = os.getenv("MTQ3Mjk2MDM5NDk0MjM0OTMxMg.GMDLus.aAqvQI9YvWFGdHTcmyOkWrXVLEeAlBCHax7f70", "").strip()
API_SECRET = os.getenv("Modmail", "").strip()
PORT = int(os.getenv("PORT", "8080"))

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN fehlt (Render Environment)")
if not API_SECRET:
    raise RuntimeError("API_SECRET fehlt (Render Environment)")

# =========================
# Discord Client
# =========================
intents = discord.Intents.none()
client = discord.Client(intents=intents)

# =========================
# Flask App
# =========================
app = Flask(__name__)

@app.get("/")
def health():
    return "OK", 200

@app.post("/send")
def send_dm():
    # Auth (muss exakt matchen)
    if request.headers.get("X-Secret") != API_SECRET:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    try:
        user_id = int(data.get("user_id", 0))
        content = str(data.get("content", "")).strip()
    except Exception:
        return jsonify({"ok": False, "error": "bad_request"}), 400

    if user_id <= 0 or not content:
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    # Discord limit safety
    content = content[:1900]

    async def _send():
        user = await client.fetch_user(user_id)
        await user.send(content)

    try:
        fut = asyncio.run_coroutine_threadsafe(_send(), client.loop)
        fut.result(timeout=12)
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@client.event
async def on_ready():
    print(f"✅ Bot online als {client.user}")

def run_flask():
    # Wichtig: host=0.0.0.0 und PORT von Render verwenden
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    # Flask im Hintergrund, Discord im Hauptthread
    threading.Thread(target=run_flask, daemon=True).start()
    client.run(DISCORD_TOKEN)
