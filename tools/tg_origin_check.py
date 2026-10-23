
import asyncio, os, sys
from pathlib import Path
TG_DIR = Path(r"C:\Users\Lenovo\Documents\Claude\Projects\Tomek Telegram Assistant")
sys.path.insert(0, str(TG_DIR)); os.chdir(TG_DIR)
import tg_read
from telethon import TelegramClient, functions
async def main():
    c = TelegramClient(str(tg_read.SESSION_FILE), int(tg_read.API_ID), tg_read.API_HASH)
    await c.connect()
    ent = await c.get_entity(1405511314)
    full = await c(functions.channels.GetFullChannelRequest(ent))
    fc = full.full_chat
    mid = getattr(fc, "migrated_from_chat_id", None)
    print("about:", (fc.about or "")[:300].replace("\n"," | "), "| migrated_from", mid)
    if mid:
        try:
            old = await c.get_entity(-mid if mid > 0 else mid)
        except Exception:
            from telethon.tl.types import PeerChat
            old = await c.get_entity(PeerChat(mid))
        async for m in c.iter_messages(old, reverse=True, limit=3):
            a = getattr(m, "action", None)
            print("OLD", m.id, m.date, type(a).__name__ if a else "", getattr(a, "title", "") if a else "")
    n = 0; yrs = {}
    async for m in c.iter_messages(ent, reverse=True):
        yrs[m.date.year] = yrs.get(m.date.year, 0) + 1
        a = getattr(m, "action", None)
        if a and "Title" in type(a).__name__:
            print("TITLE", m.date, getattr(a, "title", ""))
    print("per year", yrs)
    await c.disconnect()
asyncio.run(main())
