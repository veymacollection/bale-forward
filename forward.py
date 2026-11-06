import os, json, time, requests

TOKEN = os.environ["BOT_TOKEN"]
SOURCE = os.environ["SOURCE_CHANNEL"].strip()
API = f"https://tapi.bale.ai/bot{TOKEN}"

channels = [x.strip() for x in open("channels.txt").read().split() if x.strip()]
offset = json.load(open("state.json"))["offset"] if os.path.exists("state.json") else 0

r = requests.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 0}).json()
for u in r.get("result", []):
    offset = u["update_id"] + 1
    post = u.get("channel_post")
    if not post:
        continue
    chat = post["chat"]
    uname = "@" + chat.get("username", "")
    if uname.lower() != SOURCE.lower() and str(chat["id"]) != SOURCE:
        continue
    for ch in channels:
        res = requests.post(f"{API}/copyMessage", json={
            "chat_id": ch,
            "from_chat_id": chat["id"],
            "message_id": post["message_id"]})
        print(ch, res.status_code, res.text[:100])
        time.sleep(1.5)

json.dump({"offset": offset}, open("state.json", "w"))
