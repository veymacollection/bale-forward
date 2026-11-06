import os, json, time, requests

TOKEN = os.environ["BOT_TOKEN"]
SOURCE = int(os.environ["SOURCE_CHANNEL"])
API = f"https://tapi.bale.ai/bot{TOKEN}"

channels = [int(x) for x in open("channels.txt").read().split() if x.strip()]
offset = json.load(open("state.json"))["offset"] if os.path.exists("state.json") else 0

r = requests.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 0}).json()
for u in r.get("result", []):
    offset = u["update_id"] + 1
    post = u.get("channel_post")
    if post and post["chat"]["id"] == SOURCE:
        for ch in channels:
            requests.post(f"{API}/copyMessage", json={
                "chat_id": ch,
                "from_chat_id": SOURCE,
                "message_id": post["message_id"]})
            time.sleep(1.5)

json.dump({"offset": offset}, open("state.json", "w"))
