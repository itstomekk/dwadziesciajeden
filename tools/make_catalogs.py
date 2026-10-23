"""One-off generator: research/*.json -> content/biblioteka.json, inicjatywy.json, zasady.json, projekty additions.
After the first run, edit the content/*.json files directly; this script is kept as a record."""
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
books = json.loads((R / "research/books-tmp.json").read_text(encoding="utf-8"))


def bk(i):
    d = {k: i.get(k) for k in ("title", "author", "url", "description_pl", "image_local")}
    d["publisher"] = "Freedom Publishing" if "wydawnictwofp" in i["url"] else "Helion"
    return d


fp = [bk(b) for b in books if "wydawnictwofp" in b["url"] and b["type"] == "book" and "zlota" not in b["url"]]
gilder = [bk(b) for b in books if "zlota" in b["url"]]
bundles = [bk(b) for b in books if b["type"] == "bundle"]
tech = [bk(b) for b in books if "helion" in b["url"]]

lib = {"checked": "2026-10-23", "categories": [
    {"id": "ksiazki", "title": "Książki o Bitcoinie i pieniądzu", "layout": "books",
     "intro": "Polskie wydania, od których warto zacząć. Większość wydaje Freedom Publishing, które dostarczyło też książki do naszej kampanii w Parlamencie.",
     "items": fp + gilder + bundles},
    {"id": "technicznie", "title": "Technicznie", "layout": "books",
     "intro": "Dla tych, którzy chcą zrozumieć protokół od środka albo na nim budować.", "items": tech},
    {"id": "strony", "title": "Strony i tłumaczenia", "items": [
        {"title": "Archiwum Bitcoina", "author": "Mato", "type_label": "blog", "url": "https://archiwumbitcoina.pl/",
         "description_pl": "Polskie tłumaczenia najważniejszych tekstów o Bitcoinie, zebrane w jednym miejscu."},
        {"title": "Bitcoin.org po polsku", "type_label": "strona", "url": "https://bitcoin.org/pl/",
         "description_pl": "Polska wersja klasycznej strony o Bitcoinie: jak działa, jak zacząć, jak wybrać portfel."},
        {"title": "Whitepaper po polsku na bitcoin.org", "author": "tłum. Damian Mee", "type_label": "PDF",
         "url": "https://bitcoin.org/files/bitcoin-paper/bitcoin_pl.pdf",
         "description_pl": "To samo tłumaczenie białej księgi, które hostujemy u siebie, w wersji z bitcoin.org."},
        {"title": "Nostr: przyszłość sieci społecznościowych", "author": "Gracjan Pietras", "type_label": "artykuł",
         "url": "https://www.linkedin.com/pulse/nostr-przysz%C5%82o%C5%9B%C4%87-sieci-spo%C5%82eczno%C5%9Bciowych-gracjan-pietras-thwpf/",
         "description_pl": "Polskie wprowadzenie do protokołu Nostr, polecane przez nas we wrześniu 2024."},
        {"title": "Raport ODF o portfelach non-custodial", "author": "Gracjan Pietras, Marcin Liszka", "type_label": "raport, EN",
         "url": "https://en.odfoundation.eu/a/726702,impact-of-the-eu-and-fatf-regulatory-frameworks-on-non-custodial-crypto-assets-wallets/",
         "description_pl": "Analiza wpływu regulacji UE i FATF na portfele, w których sam trzymasz klucze. Autorzy z polskiej społeczności."}]},
    {"id": "nagrania", "title": "Podcasty i nagrania", "items": [
        {"title": "Bujać", "author": "Mateusz Gadaj", "type_label": "podcast", "url": "https://fountain.fm/show/boUD5XjpLuK9gOpCsmbb",
         "description_pl": "Polski podcast o Bitcoinie, dostępny też na Spotify i w innych aplikacjach."},
        {"title": "Gdzie jest problem? (polski lektor)", "type_label": "film", "url": "https://www.youtube.com/watch?v=3VupBwORhLk",
         "description_pl": "Film krok po kroku pokazujący, jak państwowy wpływ na pieniądz rodzi kolejne problemy. Polską wersję przygotowali bitcoinerzy z naszej społeczności."},
        {"title": "Bitcoin: Odkrywanie Nowego Świata (wykład)", "author": "Wiktor Lisowski", "type_label": "wykład",
         "url": "https://www.youtube.com/watch?v=wECefAXbJWw", "description_pl": "Solidny wstęp do Bitcoina po polsku, polecany przez nas w 2024."},
        {"title": "Jak połączyć Trezor One ze Sparrow Wallet?", "author": "Dlaczego bitcoin?", "type_label": "poradnik wideo",
         "url": "https://youtu.be/Jnw-jwobIRU", "description_pl": "Praktyczny poradnik z polskojęzycznego kanału o samodzielnym przechowywaniu."},
        {"title": "Bitcoin Polska", "author": "Oskar Pilch", "type_label": "YouTube", "url": "https://www.youtube.com/@bitcoinpolska",
         "description_pl": "Bitcoinowe słuchowisko: czytane teksty o Bitcoinie. Kanał nie publikuje od kilku lat, archiwum wciąż warto przesłuchać."},
        {"title": "Czy bitcoin to marnotrawstwo energii?", "author": "Radio WNET", "type_label": "audycja",
         "url": "https://wnet.fm/2025/02/05/czy-bitcoin-to-marnotrawstwo-energii-wyjasniaja-lech-wilczynski-i-gracjan-pietras/",
         "description_pl": "Lech Wilczyński i Gracjan Pietras rozprawiają się z mitami o energii i Bitcoinie."}]},
]}
(R / "content/biblioteka.json").write_text(json.dumps(lib, ensure_ascii=False, indent=1), encoding="utf-8")

ini = {"checked": "2026-10-23", "categories": [
    {"id": "polskie-projekty", "title": "Polskie projekty bitcoinowe",
     "intro": "Narzędzia i firmy, które budują Bitcoina w Polsce albo dla Polaków. Znasz kolejne? Daj znać na czacie.", "items": [
         {"title": "bitblik", "type_label": "aplikacja, open source", "url": "https://bitblik.app/",
          "description_pl": "Most między bitcoinem a BLIK-iem: płacisz bitcoinem wszędzie, gdzie działa BLIK, albo sprzedajesz kody BLIK za sats. Peer-to-peer, bez KYC, rozliczenie przez Lightning hold-invoice."},
         {"title": "Satsback", "type_label": "cashback w bitcoinie", "url": "https://satsback.com/",
          "description_pl": "Zwrot w bitcoinie za zakupy w setkach polskich sklepów internetowych. Współorganizował krakowskie meetupy i wsparł naszą kampanię w Parlamencie."},
         {"title": "Cryptosteel", "type_label": "metalowy backup seeda", "url": "https://cryptosteel.com/",
          "description_pl": "Stalowe kapsuły i kasety do przechowywania frazy odzyskiwania, odporne na ogień i wodę. Darczyńca kampanii Standard Bitcoina w Parlamencie."},
         {"title": "Kancelaria DJP: Bitcoin desk", "type_label": "usługi prawne", "url": "https://djp.pl/",
          "description_pl": "Warszawska kancelaria, która przyjmuje bitcoin, ma zespół prawników-bitcoinerów i trzyma BTC w rezerwach firmy."}]},
    {"id": "organizacje", "title": "Organizacje i sieci", "items": [
        {"title": "Polskie Stowarzyszenie Bitcoin", "type_label": "stowarzyszenie, od 2013", "url": "https://bitcoin.org.pl/",
         "description_pl": "Najstarsza polska organizacja bitcoinowa, ze Szczecina. Przekazała 1 mln satoshi na naszą kampanię w Parlamencie i wsparła Bitcoin FilmFest 2026."},
        {"title": "TwentyOne", "author": "Gigi", "type_label": "sieć społeczności", "url": "https://twentyone.world/",
         "description_pl": "Międzynarodowa sieć lokalnych społeczności Bitcoin Only. Dwadzieścia Jeden jest jej polską gałęzią."},
        {"title": "BTC Map: Polska", "type_label": "mapa", "url": "https://btcmap.org/country/pl",
         "description_pl": "Wszystkie miejsca w Polsce, w których zapłacisz bitcoinem. Dane uzupełnia społeczność, także my."}]},
    {"id": "wydarzenia", "title": "Wydarzenia i spotkania", "items": [
        {"title": "Bitcoin FilmFest", "type_label": "festiwal, Warszawa", "url": "https://bitcoinfilmfest.com/",
         "description_pl": "Festiwal kina o Bitcoinie, pieniądzu i wolności, robiony przez bitcoinerów dla bitcoinerów."},
        {"title": "BitcoinWalk Warszawa", "type_label": "spacer, soboty 11:30", "url": "https://bitcoinwalk.org/warszawa",
         "description_pl": "Cotygodniowy spacer i rozmowa o Bitcoinie, zbiórka przy Fontannie Wielkiej w Ogrodzie Saskim. Mile widziani także anglojęzyczni."},
        {"title": "Bitcoin Warsaw", "type_label": "Meetup, poniedziałki 18:00", "url": "https://www.meetup.com/bitcoin-warsaw/",
         "description_pl": "Wielojęzyczna grupa warszawskich wydarzeń. W poniedziałki Bitcoin Café: spotkanie w małych grupach, bez prezentacji, wokół Twoich pytań."},
        {"title": "Poznań BitcoinWalk", "type_label": "spacer, Poznań", "url": "https://www.meetup.com/pl-PL/pozna%C5%84-bitcoinwalk/",
         "description_pl": "Bitcoinowe spacery po Poznaniu, ogłaszane na Meetup i na naszej poznańskiej grupie."}]},
    {"id": "spolecznosci", "title": "Czaty i społeczności", "items": [
        {"title": "Dwadzieścia Jeden", "type_label": "Telegram", "url": "https://t.me/dwadziesciajeden",
         "description_pl": "Nasz główny czat. Tu dzieje się większość rzeczy."},
        {"title": "Dwadzieścia Jeden Poznań", "type_label": "Telegram", "url": "https://t.me/DwadziesciaJedenPoznan",
         "description_pl": "Poznańska grupa społeczności."},
        {"title": "BitcoinWalk Warszawa na Nostrze", "type_label": "Nostr (Flotilla)", "url": "https://app.flotilla.social/join?r=warszawa.bitcoinwalk.org&c=OWY8E116",
         "description_pl": "Czat warszawskich spacerów, prowadzony na Nostrze."}]},
]}
(R / "content/inicjatywy.json").write_text(json.dumps(ini, ensure_ascii=False, indent=1), encoding="utf-8")

z = {"checked": "2026-10-23",
     "concept_html": "<p>TwentyOne (<a href=\"https://twentyone.world/\" rel=\"noopener\">twentyone.world</a>) to sieć otwartych, lokalnych społeczności bitcoinerów, zainicjowana przez Gigiego z niemieckiego EINUNDZWANZIG. Każda nazywa się „dwadzieścia jeden” w swoim języku i stoi na tym samym schemacie: stały sygnał (podcast, newsletter lub inna regularna publikacja), lokalny język i kultura oraz otwarta grupa, do której łatwo dołączyć.</p><p>Treści dotyczą wyłącznie Bitcoina. Meetupy mogą wyrosnąć z takiej społeczności, ale zaczyna się od internetu, bo on się skaluje. Koncepcja jest open source: każdy może ją skopiować i dopasować do siebie. Polska jest na <a href=\"https://twentyone.world/network.html\" rel=\"noopener\">liście sieci</a> jako Dwadzieścia Jeden.</p>",
     "rules": [
         {"title": "Tylko Bitcoin", "text": "Rozmawiamy o Bitcoinie. Altcoiny, tokeny i „okazje inwestycyjne” nie mają tu miejsca."},
         {"title": "Nie zarabiamy na uczestnikach", "text": "Jesteśmy tu dla idei, nie po to, żeby sprzedawać ludziom z grupy albo promować kolejny projekt."},
         {"title": "Gościnnie, ale czujnie", "text": "Witamy nowych, ale nie ufamy w ciemno. Nikt z nas nie poprosi Cię o seed, klucze ani przelew. Ktoś prosi? To scam: zgłoś go adminom."},
         {"title": "Otwarta grupa", "text": "Do społeczności łatwo dołączyć: czat na Telegramie jest publiczny."},
         {"title": "Po polsku", "text": "Tworzymy i tłumaczymy treści dla Polaków. Każda pomoc przy tłumaczeniach jest mile widziana."},
         {"title": "Najpierw internet, potem meetupy", "text": "Podstawą jest regularny sygnał i grupa online. Spotkania na żywo wyrastają z nich, a nie odwrotnie."},
         {"title": "Konsekwencja", "text": "Regularność wygrywa z zapałem. Cokolwiek zaczynasz, trzymaj się tego przez co najmniej 21 tygodni."},
         {"title": "Nie działaj sam", "text": "Znajdź kogoś do współpracy i wspieraj cudze inicjatywy. Społeczność jest tym, co z niej zrobimy."},
         {"title": "Sygnał, nie szum", "text": "Dbamy o jakość. Mniej spamu i powtórek, więcej rzeczy, które się przydadzą."}],
     "more_html": "<h2>Wymogi sieci</h2><p>Żeby społeczność była na mapie TwentyOne, musi mówić lokalnym językiem, mieć aktywny „beacon”, który nadaje od co najmniej 21 tygodni, i otwartą grupę z co najmniej 21 członkami (<a href=\"https://github.com/twentyone-world/twentyone-world.github.io/blob/main/CONTRIBUTING.md\" rel=\"noopener\">CONTRIBUTING.md</a>). Wpis sieci dla Polski prowadzi na dwadziesciajeden.pl.</p><h2>Logo</h2><p>Logo sieci to słowo „twentyone” w lokalnym języku, złożone krojem The Bold Font, z małym symbolem Bitcoina. Polska wersja jest w <a href=\"https://twentyone.world/logo/\" rel=\"noopener\">galerii forków</a>.</p>"}
(R / "content/zasady.json").write_text(json.dumps(z, ensure_ascii=False, indent=1), encoding="utf-8")

p = json.loads((R / "content/projekty.json").read_text(encoding="utf-8"))
p["projects"] = [x for x in p["projects"] if x["id"] not in ("bitblik", "bitcoin-district", "cryptosteel")]
p["projects"] += [
    {"id": "bitblik", "name": "bitblik", "status": "aplikacja, open source", "kind": "friends", "image": None,
     "text": "Most między bitcoinem a BLIK-iem. Płacisz bitcoinem w Żabce, na Allegro czy w bankomacie, albo sprzedajesz kody BLIK za sats. Peer-to-peer, bez KYC, środki zablokowane w Lightning hold-invoice, a nie u pośrednika. Instalacja przez Zapstore, APK albo AltStore.",
     "links": [{"label": "bitblik.app", "url": "https://bitblik.app/"}, {"label": "Kod źródłowy", "url": "https://gitworkshop.dev/bitblik.app/relay.ngit.dev/bitblik"}],
     "origin": "owner request 2026-10-23; bitblik.app"},
    {"id": "cryptosteel", "name": "Cryptosteel", "status": "partner", "kind": "friends", "image": None,
     "text": "Stalowe kapsuły i kasety na frazę odzyskiwania, odporne na ogień, wodę i czas. Cryptosteel był jednym z pierwszych darczyńców kampanii Standard Bitcoina w Parlamencie.",
     "links": [{"label": "cryptosteel.com", "url": "https://cryptosteel.com/"}], "origin": "owner request 2026-10-23; post 2025-11-01"},
    {"id": "bitcoin-district", "name": "Bitcoin District", "status": "Próspera, Roatán", "kind": "friends", "image": None,
     "text": "Bitcoinowa dzielnica w Próspera na wyspie Roatán w Hondurasie: miejsce do życia, pracy i budowania na standardzie Bitcoina.",
     "links": [{"label": "thebitcoindistrict.com", "url": "https://thebitcoindistrict.com/"}], "origin": "owner request 2026-10-23"}]
(R / "content/projekty.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")
