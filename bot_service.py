import os
import asyncio
import threading
from flask import Flask, request, jsonify
import discord

# =========================
# ENV VARS (Render)
# =========================
DISCORD_TOKEN = os.getenv("MTQ3Mjk2MDM5NDk0MjM0OTMxMg.GzcNRL.tKpPv9aKu8DNBfE4_j12QZdDerbMOxEg8CWFyQ")
API_SECRET = os.getenv("Modmail")
PORT = int(os.getenv("PORT", "8080"))

if not DISCORD_TOKEN or not API_SECRET:
    raise RuntimeError("DISCORD_TOKEN oder API_SECRET fehlt")

# =========================
# DISCORD CLIENT
# =========================
intents = discord.Intents.none()
client = discord.Client(intents=intents)

# =========================
# FLASK APP
# =========================
app = Flask(__name__)

@app.route("/send", methods=["POST"])
def send_dm():
    if request.headers.get("X-Secret") != API_SECRET:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    try:
        user_id = int(data.get("user_id", 0))
        content = str(data.get("content", ""))[:1900]
    except Exception:
        return jsonify({"ok": False, "error": "bad_request"}), 400

    if user_id <= 0 or not content:
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    async def _send():
        user = await client.fetch_user(user_id)
        await user.send(content)

    try:
        fut = asyncio.run_coroutine_threadsafe(_send(), client.loop)
        fut.result(timeout=10)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@client.event
async def on_ready():
    print(f"Bot online als {client.user}")

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    client.run(DISCORD_TOKEN)
