"""Read-only export of the predecessor group 'yellowpilled' (2021-04, migrated to a supergroup
on 2021-04-12) including its pre-migration basic chat, using Tomek's saved Telethon session.
Output: source-archive/telegram/yellowpilled.json (private, gitignored). Nothing is sent or marked read.
Run with the Hermes venv python (telethon)."""
import asyncio
import json
import os
import sys
from pathlib import Path

TG_DIR = Path(r"C:\Users\Lenovo\Documents\Claude\Projects\Tomek Telegram Assistant")
sys.path.insert(0, str(TG_DIR))
os.chdir(TG_DIR)
import tg_read  # noqa: E402
from telethon import TelegramClient, functions  # noqa: E402
from telethon.tl.types import PeerChat  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "source-archive" / "telegram"
OUT.mkdir(parents=True, exist_ok=True)
YELLOW_ID = 1405511314


def row(m, part):
    urls = [getattr(e, "url", None) for e in (m.entities or []) if getattr(e, "url", None)]
    return {"id": m.id, "part": part, "date": m.date.isoformat(), "sender_id": m.sender_id,
            "text": m.message or "", "urls": urls,
            "media": type(m.media).__name__ if m.media else None,
            "webpage": getattr(getattr(m.media, "webpage", None), "url", None) if m.media else None,
            "reply_to": getattr(m.reply_to, "reply_to_msg_id", None) if m.reply_to else None}


async def main():
    c = TelegramClient(str(tg_read.SESSION_FILE), int(tg_read.API_ID), tg_read.API_HASH)
    await c.connect()
    ent = await c.get_entity(YELLOW_ID)
    full = await c(functions.channels.GetFullChannelRequest(ent))
    rows = []
    mid = getattr(full.full_chat, "migrated_from_chat_id", None)
    if mid:
        old = await c.get_entity(PeerChat(mid))
        async for m in c.iter_messages(old, reverse=True):
            rows.append(row(m, "basic-chat"))
    async for m in c.iter_messages(ent, reverse=True):
        rows.append(row(m, "supergroup"))
    fn = OUT / "yellowpilled.json"
    fn.write_text(json.dumps({"group": ent.title, "count": len(rows), "messages": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("exported", len(rows), "->", fn)
    await c.disconnect()

asyncio.run(main())
