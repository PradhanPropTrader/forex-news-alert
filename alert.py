import json, os, urllib.request
from datetime import datetime, timezone, timedelta

FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
STATE = "sent.json"
LEAD = 15  # minutes before the event
IST = timezone(timedelta(hours=5, minutes=30))

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def post(url, payload):
    req = urllib.request.Request(url, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json",
                                  "User-Agent": "Mozilla/5.0"})
    urllib.request.urlopen(req, timeout=30)

sent = set(json.load(open(STATE))) if os.path.exists(STATE) else set()
now = datetime.now(timezone.utc)
new = False

for e in get(FEED):
    if e.get("impact") != "High" or "Election" in e["title"]:
        continue
    t = datetime.fromisoformat(e["date"]).astimezone(timezone.utc)
    mins = (t - now).total_seconds() / 60
    key = f'{e["date"]}|{e["country"]}|{e["title"]}'
    if 0 < mins <= LEAD and key not in sent:
        when = t.astimezone(IST)
        msg = (f"🚨 FX NEWS ALERT\n\n"
               f"💵 Currency - {e['country']}\n\n"
               f"📊 {e['title']}\n\n"
               f"📅 Release Date: {when.strftime('%d %B %Y')}\n"
               f"⏰ Time: {when.strftime('%I:%M %p')} IST 🇮🇳\n\n"
               f"⚠️ Increased market volatility expected. Trade with caution.")
        tg = os.environ["TG_TOKEN"]
        post(f"https://api.telegram.org/bot{tg}/sendMessage",
             {"chat_id": os.environ["TG_CHAT"], "text": msg})
        post(os.environ["DISCORD_WEBHOOK"], {"content": msg})
        sent.add(key)
        new = True

if new:
    json.dump(sorted(sent), open(STATE, "w"))
