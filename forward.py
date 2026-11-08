import os, json, time, requests
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ["BOT_TOKEN"]
SOURCE = os.environ["SOURCE_CHANNEL"].strip().lstrip("@").lower()
API = f"https://tapi.bale.ai/bot{TOKEN}"
WORKERS = 5      # تعداد ارسال هم‌زمان
PAUSE = 0.2      # مکث کوتاه (ثانیه) برای رعایت محدودیت

channels = [x.strip() for x in open("channels.txt").read().split() if x.strip()]
offset = json.load(open("state.json"))["offset"] if os.path.exists("state.json") else 0

def send(args):
    ch, from_id, mid = args
    for attempt in range(3):
        try:
            res = requests.post(f"{API}/forwardMessage", json={
                "chat_id": ch,
                "from_chat_id": from_id,
                "message_id": mid}, timeout=30)
            if res.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            print(ch, res.status_code, res.text[:100])
            break
        except Exception as e:
            print(ch, "error:", e)
            time.sleep(1)
    time.sleep(PAUSE)

r = requests.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 0}).json()
for u in r.get("result", []):
    offset = u["update_id"] + 1
    post = u.get("channel_post") or u.get("message")
    if not post:
        continue
    chat = post["chat"]
    if chat.get("type") != "channel":
        continue
    if chat.get("username", "").lower() != SOURCE:
        continue
    if "new_chat_members" in post or post.get("message_id", 0) == 0:
        continue
    print("FORWARD:", post["message_id"])
    jobs = [(ch, chat["id"], post["message_id"]) for ch in channels]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(send, jobs))

json.dump({"offset": offset}, open("state.json", "w"))
