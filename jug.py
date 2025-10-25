import feedparser
import requests
import time
import hashlib
from dotenv import load_dotenv
import os
import sys
# initial startup notice will be sent after environment variables are loaded and send_telegram is defined

# --- Load .env variables safely ---
load_dotenv()



print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("CHAT_ID:", os.getenv("CHAT_ID"))
print("FEEDS:", os.getenv("FEEDS"))
print("KEYWORDS:", os.getenv("KEYWORDS"))

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
FEEDS = os.getenv("FEEDS")
KEYWORDS = os.getenv("KEYWORDS")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))
STATE_FILE = os.getenv("STATE_FILE", "seen_hashes.txt")

# --- Safety checks ---
if not BOT_TOKEN or not CHAT_ID or not FEEDS or not KEYWORDS:
    print("ERROR: Please make sure BOT_TOKEN, CHAT_ID, FEEDS, and KEYWORDS are set in .env")
    sys.exit(1)

FEEDS = os.getenv("FEEDS")
if not FEEDS:
    raise ValueError("FEEDS variable not found in .env")
FEEDS = FEEDS.split(",")


# --- Load previously seen posts ---
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        seen = set(line.strip() for line in f.readlines())
else:
    seen = set()

# --- Confirmation print ---
print("✅ Script started — monitoring WhatsApp updates...")



# --- Function to send Telegram message ---
def send_telegram(message):
    print(f"📩 Sending Telegram message: {message}")  # debug/confirmation
    url = f"https://api.telegram.org/bot8200302452:AAFXlzdZiHAZz1Ktuv7Ac3H1o0by1_nAtFs/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    try:
        resp_json = response.json()
        if not resp_json.get("ok"):
            print("⚠️ Telegram API error:", resp_json)
    except Exception as e:
        print("⚠️ Error parsing Telegram response:", e)

# send startup confirmation now that send_telegram and env vars are available
send_telegram("✅ WhatsApp username monitor started — I’ll notify you as soon as a username update appears.")

# --- Continuous monitoring loop ---
while True:
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            content = entry.title + " " + entry.get("summary", "")
            content_lower = content.lower()
            if any(k in content_lower for k in KEYWORDS):
                # Unique hash for duplicate checking
                hash_id = hashlib.md5((entry.link + entry.title).encode()).hexdigest()
                if hash_id not in seen:
                    message = f"📢 New WhatsApp update detected:\n{entry.title}\n{entry.link}"
                    send_telegram(message)
                    seen.add(hash_id)
    # Save seen posts
    with open(STATE_FILE, "w") as f:
        for h in seen:
            f.write(h + "\n")
    time.sleep(CHECK_INTERVAL)

