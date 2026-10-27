"""Snapshot of BTC Map places in Poland -> content/btcmap-pl.json (read by build.py, rendered by assets/mapa.js).

Source: BTC Map REST v4 (`/v4/places`, all places, chosen fields) filtered to the Polish border polygon from
`/v3/areas/pl`. City and voivodeship come from OpenStreetMap Nominatim reverse geocoding (1 request/second,
cached in source-archive/btcmap/geocode-cache.json, so a refresh only asks about new places).
Places that Nominatim puts outside Poland are dropped (the BTC Map polygon is coarse at the borders).

Run:  python tools/fetch_btcmap.py        (stdlib only, ~25 s + 1 s per uncached place)
"""
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "btcmap-pl.json"
CACHE = ROOT / "source-archive" / "btcmap" / "geocode-cache.json"
UA = {"User-Agent": "dwadziesciajeden.pl map snapshot (https://dwadziesciajeden.pl)"}

FIELDS = ("id,lat,lon,name,icon,address,opening_hours,verified_at,website,phone,boosted_until,required_app_url,"
          "osm:addr:city,osm:payment:lightning,osm:payment:onchain,osm:payment:lightning_contactless,"
          "osm:amenity,osm:shop,osm:tourism,osm:craft,osm:office,osm:healthcare,osm:leisure,osm:brand,osm:operator")

# icon / OSM tag -> category key (labels live in assets/mapa.js)
CAT_ICON = {
    "local_atm": "atm", "currency_exchange": "kantor",
    "restaurant": "jedzenie", "lunch_dining": "jedzenie", "local_pizza": "jedzenie", "bakery_dining": "jedzenie",
    "cake": "jedzenie", "local_cafe": "jedzenie", "coffee": "jedzenie", "sports_bar": "jedzenie", "local_bar": "jedzenie",
    "nightlife": "jedzenie", "liquor": "jedzenie", "fastfood": "jedzenie", "icecream": "jedzenie", "ramen_dining": "jedzenie",
    "hotel": "nocleg", "cottage": "nocleg", "camping": "nocleg", "home": "nocleg", "bed": "nocleg", "holiday_village": "nocleg",
    "storefront": "sklepy", "local_grocery_store": "sklepy", "computer": "sklepy", "diamond": "sklepy", "window": "sklepy",
    "local_printshop": "sklepy", "shopping_cart": "sklepy", "checkroom": "sklepy", "smartphone": "sklepy", "menu_book": "sklepy",
    "pedal_bike": "sklepy", "local_florist": "sklepy",
    "spa": "zdrowie", "dentistry": "zdrowie", "medical_services": "zdrowie", "fitness_center": "zdrowie",
    "content_cut": "zdrowie", "local_pharmacy": "zdrowie", "self_improvement": "zdrowie", "psychology": "zdrowie",
    "paragliding": "rozrywka", "sports": "rozrywka", "attractions": "rozrywka", "theater_comedy": "rozrywka",
    "sports_esports": "rozrywka", "museum": "rozrywka",
    "sports_martial_arts": "rozrywka", "directions_boat": "rozrywka", "surfing": "rozrywka", "golf_course": "rozrywka",
}
NOMINATIM = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=10&accept-language=pl&lat={}&lon={}"


def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())


def inside(x, y, rings):
    hit = False
    for ring in rings:
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                hit = not hit
            j = i
    return hit


def category(p):
    icon = p.get("icon") or ""
    if icon in CAT_ICON:
        return CAT_ICON[icon]
    if p.get("osm:amenity") in ("restaurant", "cafe", "bar", "pub", "fast_food", "ice_cream"):
        return "jedzenie"
    if p.get("osm:tourism") in ("hotel", "guest_house", "apartment", "hostel", "camp_site", "chalet"):
        return "nocleg"
    if p.get("osm:shop"):
        return "sklepy"
    if p.get("osm:healthcare") or p.get("osm:leisure") in ("fitness_centre", "sports_centre"):
        return "zdrowie"
    return "uslugi"


def geocode(p, cache):
    key = str(p["id"])
    if key not in cache:
        time.sleep(1.1)
        try:
            r = get(NOMINATIM.format(p["lat"], p["lon"]))
        except Exception as ex:  # keep going; the place is kept with the BTC Map city only
            print("  geocode failed", p["id"], ex)
            return {}
        a = r.get("address", {})
        cache[key] = {"cc": a.get("country_code"), "state": a.get("state"),
                      "city": a.get("city") or a.get("town") or a.get("village") or a.get("municipality") or a.get("county")}
    return cache[key]


def main():
    area = get("https://api.btcmap.org/v3/areas/pl")
    gj = area["tags"]["geo_json"]
    gj = gj if isinstance(gj, dict) else json.loads(gj)
    polys = gj["coordinates"] if gj["type"] == "MultiPolygon" else [gj["coordinates"]]
    places = get("https://api.btcmap.org/v4/places?fields=" + urllib.parse.quote(FIELDS, safe=",:"))
    print("BTC Map places worldwide:", len(places))
    pl = [p for p in places if p.get("lat") and 48.9 < p["lat"] < 55.0 and 14.0 < p["lon"] < 24.3
          and any(inside(p["lon"], p["lat"], poly) for poly in polys)]
    print("inside the PL polygon:", len(pl))

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    rows, dropped = [], []
    for p in pl:
        g = geocode(p, cache)
        if g.get("cc") and g["cc"] != "pl":
            dropped.append(p.get("name"))
            continue
        state = (g.get("state") or "").replace("województwo ", "") or None
        city = p.get("osm:addr:city") or g.get("city")
        ver = (p.get("verified_at") or "")[:10] or None
        if ver and ver > datetime.now(timezone.utc).strftime("%Y-%m-%d"):
            ver = None  # a few OSM check_date tags are typos in the future (2028, 2042)
        cat = category(p)
        row = {
            "id": p["id"], "n": (p.get("name") or "").strip() or ("Bankomat BTC" if cat == "atm" else "Bez nazwy"),
            "lat": round(p["lat"], 6), "lon": round(p["lon"], 6), "c": cat, "i": p.get("icon"),
            "a": p.get("address"), "city": city, "woj": state, "v": ver,
            "ln": p.get("osm:payment:lightning") == "yes", "oc": p.get("osm:payment:onchain") == "yes",
            "nfc": p.get("osm:payment:lightning_contactless") == "yes",
            "oh": p.get("opening_hours"), "web": p.get("website"),
            "op": p.get("osm:operator") or p.get("osm:brand") if cat in ("atm", "kantor") else None,
            "boost": bool(p.get("boosted_until") and p["boosted_until"] > datetime.now(timezone.utc).isoformat()),
        }
        rows.append({k: v for k, v in row.items() if v not in (None, "", False)})
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    rows.sort(key=lambda r: (r.get("city") or "~", r["n"].lower()))
    OUT.write_text(json.dumps({"source": "BTC Map (api.btcmap.org v4), OpenStreetMap Nominatim for city/voivodeship",
                               "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                               "count": len(rows), "places": rows}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print("kept", len(rows), "dropped outside PL:", dropped)


if __name__ == "__main__":
    main()
