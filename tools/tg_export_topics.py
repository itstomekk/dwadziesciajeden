"""Read-only export of the 'Bitcoin po Polsku' and 'Bitcoin w Polsce' topics from the public
Dwadzieścia Jeden Telegram group (t.me/dwadziesciajeden) using Tomek's saved Telethon session.
Output: source-archive/telegram/<topic>.json (private, gitignored). Nothing is sent or marked read.
Run with the Hermes venv python (telethon 1.37.0)."""
import asyncio
import json
import os
import sys
from pathlib import Path

TG_DIR = Path(r"C:\Users\Lenovo\Documents\Claude\Projects\Tomek Telegram Assistant")
sys.path.insert(0, str(TG_DIR))
os.chdir(TG_DIR)
import tg_read  # noqa: E402  (loads API id/hash from its .env without printing them)
from telethon import TelegramClient, functions  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "source-archive" / "telegram"
OUT.mkdir(parents=True, exist_ok=True)
WANT = ("bitcoin po polsku", "bitcoin w polsce", "linki i polecajki", "projekty, appki")
ALL = "--all" in sys.argv      # export every topic not exported yet (General included)
LIST = "--list" in sys.argv    # only list topics


async def main():
    client = TelegramClient(str(tg_read.SESSION_FILE), int(tg_read.API_ID), tg_read.API_HASH)
    await client.connect()
    ent = await client.get_entity("dwadziesciajeden")
    print("group:", getattr(ent, "title", ent.id), "forum:", getattr(ent, "forum", False))
    topics = await client(functions.channels.GetForumTopicsRequest(channel=ent, offset_date=None, offset_id=0, offset_topic=0, limit=100))
    for t in topics.topics:
        print("topic", t.id, repr(getattr(t, "title", "")), "top_message", getattr(t, "top_message", None))
    if LIST:
        await client.disconnect()
        return
    for t in topics.topics:
        title = getattr(t, "title", "")
        fn = OUT / ("topic-" + str(t.id) + ".json")
        if ALL:
            if fn.exists():
                continue
        elif not any(w in title.lower() for w in WANT):
            continue
        rows = []
        if t.id == 1:  # General: messages that are not inside any other topic
            it = (m async for m in client.iter_messages(ent, limit=None)
                  if not (m.reply_to and getattr(m.reply_to, "forum_topic", False)))
        else:
            it = client.iter_messages(ent, reply_to=t.id, limit=None)
        async for m in it:
            urls = []
            for e in (m.entities or []):
                u = getattr(e, "url", None)
                if u:
                    urls.append(u)
            rows.append({"id": m.id, "date": m.date.isoformat(), "sender_id": m.sender_id,
                         "text": m.message or "", "urls": urls,
                         "media": type(m.media).__name__ if m.media else None,
                         "webpage": getattr(getattr(m.media, "webpage", None), "url", None) if m.media else None})
        fn.write_text(json.dumps({"topic": title, "topic_id": t.id, "count": len(rows), "messages": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(title, t.id, len(rows), "->", fn.name)
    await client.disconnect()


asyncio.run(main())
