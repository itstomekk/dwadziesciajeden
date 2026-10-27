"""Monthly refresh of the BTC Map snapshot on dwadziesciajeden.pl (Hermes cron, no agent).

Works in a fresh clone of the published repo (never in the interactive working copy, so half-done local edits are
never published): fetch BTC Map data, rebuild, commit only the snapshot + docs/, push. The Nominatim geocode cache is
copied into the clone and back, so only new places are geocoded.

Stdout = the Telegram message (one line). Prints a ⚠️ line on any failure.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/itstomekk/dwadziesciajeden.git"
CACHE_REL = Path("source-archive") / "btcmap" / "geocode-cache.json"
SNAP_REL = Path("content") / "btcmap-pl.json"
URL = "https://dwadziesciajeden.pl/bitcoinowa-mapa-polski/"
GIT_AUTH = ["-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential"]


def run(cmd, cwd, timeout=900):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", PYTHONIOENCODING="utf-8")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, env=env)
    if r.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd[:3]))}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout


def main():
    tmp = Path(tempfile.mkdtemp(prefix="dj-btcmap-"))
    try:
        clone = tmp / "repo"
        run(["git", *GIT_AUTH, "clone", "--depth", "1", REPO, str(clone)], tmp)
        old = json.loads((clone / SNAP_REL).read_text(encoding="utf-8"))
        if (PROJECT / CACHE_REL).exists():
            (clone / CACHE_REL).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(PROJECT / CACHE_REL, clone / CACHE_REL)
        run([sys.executable, "tools/fetch_btcmap.py"], clone)
        new = json.loads((clone / SNAP_REL).read_text(encoding="utf-8"))
        if new["count"] < 0.8 * old["count"]:
            print(f"⚠️ Mapa 21: odświeżenie przerwane, BTC Map zwrócił {new['count']} miejsc (było {old['count']}). Nic nie opublikowano.")
            return
        (PROJECT / CACHE_REL).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(clone / CACHE_REL, PROJECT / CACHE_REL)
        run([sys.executable, "build.py"], clone, timeout=300)
        run(["git", "add", str(SNAP_REL), "docs"], clone)
        if not run(["git", "status", "--porcelain"], clone).strip():
            return  # nothing changed, stay quiet
        old_ids = {p["id"] for p in old["places"]}
        new_ids = {p["id"] for p in new["places"]}
        added, removed = len(new_ids - old_ids), len(old_ids - new_ids)
        run(["git", "-c", "user.name=Hermes cron", "-c", "user.email=hermes@localhost", "commit", "-q", "-m",
             f"BTC Map snapshot {new['fetched']}: {new['count']} places (+{added}/-{removed})"], clone)
        run(["git", *GIT_AUTH, "push", "-q", "origin", "HEAD:main"], clone)
        print(f"✅ Mapa 21 odświeżona: {new['count']} miejsc (było {old['count']}, nowe +{added}, usunięte -{removed}). {URL}")
    except Exception as ex:  # one line for Telegram
        print(f"⚠️ Mapa 21: odświeżenie nie wyszło: {str(ex)[:300]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
