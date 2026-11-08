"""The Bitcoin mission page. The historic text is supplied by the importer."""
import re

# GUS annual consumer price index, previous year = 100 (stat.gov.pl, "Roczne wskazniki cen
# towarow i uslug konsumpcyjnych od 1950 r."). Checked against the live table on 2026-11-06.
GUS_CPI = {1995: 127.8, 1996: 119.9, 1997: 114.9, 1998: 111.8, 1999: 107.3, 2000: 110.1,
           2001: 105.5, 2002: 101.9, 2003: 100.8, 2004: 103.5, 2005: 102.1, 2006: 101.0,
           2007: 102.5, 2008: 104.2, 2009: 103.5, 2010: 102.6, 2011: 104.3, 2012: 103.7,
           2013: 100.9, 2014: 100.0, 2015: 99.1, 2016: 99.4, 2017: 102.0, 2018: 101.6,
           2019: 102.3, 2020: 103.4, 2021: 105.1, 2022: 114.4, 2023: 111.4, 2024: 103.6,
           2025: 103.6}


def chain(first, last):
    """Price multiplier across first..last (annual averages, indices chained)."""
    out = 1.0
    for year in range(first, last + 1):
        out *= GUS_CPI[year] / 100
    return out


def _pl(pct):
    return f'{pct:+.1f}%'.replace('.', ',')


def _cpi_chart():
    """Inline SVG: annual inflation 1995-2025 (index - 100), orange bars at 10% and above."""
    scale, base, pitch, bar = 3.6, 124, 12.5, 9
    bars, years = [], list(GUS_CPI)
    for i, year in enumerate(years):
        pct = round(GUS_CPI[year] - 100, 1)
        h = abs(pct) * scale
        y = base - h if pct >= 0 else base
        cls = ' class="hi"' if pct >= 10 else ''
        bars.append(f'<rect{cls} x="{i * pitch + 1:.1f}" y="{y:.1f}" width="{bar}" '
                    f'height="{max(h, 0.6):.1f}"><title>{year}: {_pl(pct)}%</title></rect>')
    anchors = {1995: ('start', 1.0), 2005: ('middle', 10 * pitch + 5.5), 2015: ('middle', 20 * pitch + 5.5),
               2025: ('end', 30 * pitch + 10.0)}
    ticks = ''.join(f'<text x="{x:.1f}" y="{base + 24}" text-anchor="{a}">{y}</text>' for y, (a, x) in anchors.items())
    guide = (f'<line x1="0" x2="390" y1="{base - 10 * scale:.1f}" y2="{base - 10 * scale:.1f}" '
             f'stroke="#8F6400" stroke-width=".8" stroke-dasharray="3 3"/>')
    labels = (f'<text x="{0 * pitch + 1:.1f}" y="{base - 27.8 * scale - 5:.1f}">27,8%</text>'
              f'<text x="{years.index(2022) * pitch - 6:.1f}" y="{base - 14.4 * scale - 5:.1f}">14,4%</text>')
    return (f'<svg viewBox="0 0 390 152" role="img" aria-labelledby="cpi-t cpi-d">'
            f'<title id="cpi-t">Inflacja w Polsce, średnio rocznie, 1995-2025</title>'
            f'<desc id="cpi-d">Słupki pokazują wzrost cen rok do roku według GUS: 27,8% w 1995 r., '
            f'poniżej 5% od 2003 do 2021 r., 14,4% w 2022 r., 11,4% w 2023 r. i 3,6% w 2025 r.</desc>'
            f'<line x1="0" x2="390" y1="{base}" y2="{base}" stroke="currentColor" stroke-width=".6"/>'
            + guide + ''.join(bars) + labels + ticks + '</svg>')


def render(base, original):
    """Render the mission and the original 2022 text without modifying the latter."""
    chart = _cpi_chart()
    html = f'''<article class="mpage">
<header class="mission__hero">
  <p class="kicker">Nasza misja · Bitcoin Only</p>
  <h1>Dlaczego Bitcoin?</h1>
  <p class="mission__standfirst">Pieniądz jest zbyt ważny, żeby zależał wyłącznie od czyjejś obietnicy.</p>
  <p class="lede">Wierzymy, że każdy powinien móc oszczędzać, przechowywać i przesyłać wartość na własnych zasadach. Bitcoin daje nam narzędzie, by spróbować. Nie trzeba nam wierzyć na słowo: jego zasady można sprawdzić.</p>
  <nav class="mission__nav" aria-label="Na tej stronie"><a href="#pieniadz">Problem pieniądza</a><a href="#jak-dziala">Jak działa</a><a href="#wolnosc">Wolność</a><a href="#bitcoin-only">Dlaczego Bitcoin Only</a><a href="#pytania">Trudne pytania</a><a href="#misja">Nasza misja</a></nav>
</header>
<section class="mission__section" id="pieniadz">
  <div class="mission__label">Punkt wyjścia</div><div class="mission__content">
  <h2>Oszczędzanie nie powinno być wyścigiem.</h2>
  <p>Pracujesz, odkładasz pieniądze, a po latach ta sama kwota kupuje mniej. To nie musi oznaczać, że ktoś zabrał złotówki z konta: zmieniła się ich siła nabywcza. Inflacja nie dotyka wszystkich tak samo, a oszczędzający nie decydują bezpośrednio o podaży pieniądza.</p>
  <p>Polska zna ten temat z bliska. Poniżej kilka faktów z oficjalnych i naukowych źródeł. Przy każdej liczbie piszemy, skąd pochodzi i co dokładnie znaczy.</p>
  <div class="mission__stats">
    <div><strong>×4,04</strong><h3>Ceny 1995–2025</h3><p>Koszyk dóbr, który w 1995 r. kosztował przeciętnie 100 zł, w 2025 r. kosztował ok. 404 zł. Inaczej: 100 zł z 2025 r. kupuje tyle, co ok. 25 zł z 1995 r. To nasz przelicznik z rocznych wskaźników GUS (średnie roczne, zaokrąglone).</p></div>
    <div><strong>+27%</strong><h3>Dwa lata: 2022 i 2023</h3><p>Według GUS średnioroczne ceny wzrosły o 14,4% w 2022 r. i o 11,4% w 2023 r. Razem daje to ok. 27% (1,144 × 1,114).</p></div>
    <div><strong>10 000 : 1</strong><h3>Denominacja 1995</h3><p>1 stycznia 1995 r. nowy złoty zastąpił 10 000 starych złotych. Najmniejsza wymieniana kwota to 100 starych złotych, czyli 1 grosz. <a href="https://nbp.pl/pytania-i-odpowiedzi/" rel="noopener">NBP ↗</a></p></div>
    <div><strong>685,8</strong><h3>Rok 1990</h3><p>Wskaźnik GUS za 1990 r. (rok poprzedni = 100): ceny były średnio 6,9 raza wyższe niż w 1989 r. Rok wcześniej wskaźnik wynosił 351,1.</p></div>
  </div>
  <figure class="mission__chart">
    {chart}
    <figcaption>Inflacja w Polsce, średnio rocznie, 1995–2025 (wzrost cen rok do roku). Linia przerywana: 10%. Słupki od 10% w górę są wyróżnione kolorem. W 2023 r.: 11,4%. <a href="https://stat.gov.pl/obszary-tematyczne/ceny-handel/wskazniki-cen/wskazniki-cen-towarow-i-uslug-konsumpcyjnych-pot-inflacja-/roczne-wskazniki-cen-towarow-i-uslug-konsumpcyjnych" rel="noopener">Tabela GUS ↗</a></figcaption>
  </figure>
  <h3>Trzy przystanki w historii</h3>
  <ol class="mission__timeline">
    <li><b>1517</b><span>Mikołaj Kopernik pisze pierwszą wersję traktatu o pieniądzu <em>Meditata</em>. O nowej, gorszej monecie wprowadzonej obok dawnej, lepszej, zapisał, że „zaraziła dawną, ale, że tak powiem, z obiegu ją wypędziła”. <a href="https://ekonomista.pte.pl/pdf-155587-82416?filename=Znaczenie-traktatu-moneta.pdf" rel="noopener">Cytat za: M. Bochenek, Ekonomista 2017 ↗</a></span></li>
    <li><b>1923–24</b><span>Hiperinflacja. Pod koniec września 1923 r. za dolara trzeba było zapłacić 75,8 tys. marek polskich, w połowie stycznia 1924 r. już 9,8 mln. Reforma Grabskiego wprowadziła w 1924 r. złotego, wymienianego za 1,8 miliona marek polskich. To przestroga z historii, nie prognoza na dziś. <a href="https://dzieje.pl/aktualnosci/rocznica-reformy-walutowo-skarbowej-premiera-w-grabskiego" rel="noopener">dzieje.pl ↗</a> · <a href="https://ipn.gov.pl/pl/historia-z-ipn/215844,Reforma-walutowa.html" rel="noopener">IPN ↗</a></span></li>
    <li><b>1971</b><span>Prezydent USA Richard Nixon kończy wymienialność dolara na złoto. Decyzja wkrótce kończy system z Bretton Woods. <a href="https://www.federalreservehistory.org/essays/gold-convertibility-ends" rel="noopener">Federal Reserve History ↗</a></span></li>
  </ol>
  <p>Dziś Narodowy Bank Polski utrzymuje cel inflacyjny 2,5% z przedziałem ±1 pkt proc. (na 2026 r.). Przy stałej inflacji 2,5% rocznie ceny podwajają się po ok. 28 latach (to nasz rachunek: ln 2 / ln 1,025). To nie zarzut, tylko arytmetyka: banki centralne celowo godzą się na powolny wzrost cen, a Bitcoin proponuje inny kompromis. <a href="https://www.pb.pl/nbp-utrzymuje-w-2026-r-cel-inflacyjny-25-proc-z-przedzialem-1-pkt-proc-1249318" rel="noopener">Cel NBP, PAP ↗</a></p>
  <p>Nie twierdzimy, że każdy wzrost cen ma jedną przyczynę ani że Bitcoin rozwiąże wszystkie problemy gospodarki. Pytamy o coś prostszego: <strong>czy możemy mieć też pieniądz, którego zasady emisji są publiczne i trudne do samowolnej zmiany?</strong></p>
</div></section>
<section class="mission__section" id="jak-dziala"><div class="mission__label">Propozycja</div><div class="mission__content">
  <h2>Otwarte zasady zamiast obietnicy.</h2>
  <p>Bitcoin to jednocześnie sieć do przesyłania wartości i bitcoin, jej cyfrowy pieniądz. Transakcje zapisuje wspólny rejestr, a uczestnicy mogą samodzielnie sprawdzać, czy przestrzegają zasad. Nie ma banku, który sam prowadzi tę księgę. <a href="https://bitcoin.org/en/how-it-works" rel="noopener">Jak działa Bitcoin ↗</a></p>
  <div class="mission__principles">
    <div><strong>21 milionów</strong><h3>Przewidywalna podaż</h3><p>Obecne zasady ograniczają emisję do niespełna 21 milionów bitcoinów. Emisja nowych monet maleje z czasem. To zasada egzekwowana przez uczestników, nie gwarancja przyszłej ceny.</p></div>
    <div><strong>100 milionów</strong><h3>Małe części</h3><p>Jeden bitcoin dzieli się na 100 milionów satoshi, czyli satów. Nie trzeba posiadać całej monety.</p></div>
    <div><strong>Sprawdź sam</strong><h3>Weryfikacja</h3><p>Własny węzeł pozwala sprawdzać reguły sieci. Kod i historia transakcji są publiczne, choć korzystanie z sieci nie wymaga uruchamiania węzła.</p></div>
  </div>
  <p class="mission__source"><a href="https://bitcoin.org/en/faq" rel="noopener">Źródło: Bitcoin.org, pytania i odpowiedzi ↗</a></p>
  <h3>Reguły, które da się sprawdzić</h3>
  <dl class="mission__rules">
    <div><dt>210 000 bloków</dt><dd>Co tyle bloków nagroda dla górnika spada o połowę, mniej więcej co 4 lata. Start: 50 BTC. Ostatnio stało się to 20 kwietnia 2024 r. (blok 840 000): nagroda spadła z 6,25 do 3,125 BTC.</dd></div>
    <div><dt>10 minut</dt><dd>Docelowy czas między blokami. Co 2016 bloków (ok. 2 tygodnie) sieć koryguje trudność kopania, żeby ten czas utrzymać.</dd></div>
    <div><dt>21 000 000 BTC</dt><dd>Górna granica podaży, zapisana w kodzie jako stała <code>MAX_MONEY</code>. Jeden bitcoin to 100 000 000 satoshi.</dd></div>
    <div><dt>3 stycznia 2009</dt><dd>Data pierwszego bloku. Zapisano w nim nagłówek „The Times”: „Chancellor on brink of second bailout for banks” (po polsku: kanclerz na progu drugiego ratunku dla banków, tłumaczenie własne).</dd></div>
    <div><dt>ok. 20 tys.</dt><dd>Tyle węzłów dostępnych z zewnątrz liczył serwis Bitnodes 6 listopada 2026 r. To nie liczba użytkowników, tylko komputerów, które da się znaleźć w sieci i zapytać o dane.</dd></div>
  </dl>
  <p class="mission__source">Źródła: kod Bitcoin Core v28.0: <a href="https://github.com/bitcoin/bitcoin/blob/v28.0/src/kernel/chainparams.cpp" rel="noopener">chainparams.cpp</a>, <a href="https://github.com/bitcoin/bitcoin/blob/v28.0/src/validation.cpp" rel="noopener">validation.cpp</a>, <a href="https://github.com/bitcoin/bitcoin/blob/v28.0/src/consensus/amount.h" rel="noopener">amount.h</a> · <a href="https://wearebitcoin.org/news/2024/04/20/fourth-halving" rel="noopener">halving 2024 ↗</a> · <a href="https://bitnodes.io/api/v1/snapshots/latest/" rel="noopener">Bitnodes ↗</a></p>
  <blockquote class="mission__quote">„The root problem with conventional currency is all the trust that's required to make it work.”<cite>Satoshi Nakamoto, 11 lutego 2009 (wolne tłumaczenie: podstawowy problem walut konwencjonalnych to zaufanie, którego wymagają, by działać). <a href="https://satoshi.nakamotoinstitute.org/posts/p2pfoundation/1/" rel="noopener">Wpis na P2P Foundation ↗</a></cite></blockquote>
  <h3>Skąd bierze się bezpieczeństwo?</h3>
  <p>Górnicy zużywają energię, by proponować bloki w procesie zwanym dowodem pracy. Węzły niezależnie sprawdzają zgodność bloków z regułami. Zmiana historii wymagałaby ponownego wykonania pracy dla zmienianych bloków i nadrobienia kolejnych; bezpieczeństwo nie jest jednak magiczną gwarancją przed każdym atakiem. <a href="{base}/bitcoin-whitepaper/">Przeczytaj whitepaper po polsku →</a></p>
  <h3>Twoje klucze, Twoja odpowiedzialność</h3>
  <p>Portfel kontrolowany samodzielnie pozwala podpisywać transakcje bez powierzania kluczy giełdzie. To ważna różnica: platforma Celsius w 2022 r. wstrzymała wypłaty, a potem ogłosiła upadłość. Samodzielne przechowywanie też ma ryzyko: utrata kopii odzyskiwania lub kradzież kluczy może oznaczać utratę środków. <a href="https://dfr.vermont.gov/consumer-alert/celsius-network-files-chapter-11-bankruptcy" rel="noopener">Komunikat regulatora o Celsius ↗</a></p>
  <p>Własny portfel utrudnia blokadę przez pośrednika, ale nie czyni nikogo niewidzialnym ani nie gwarantuje ochrony przed przymusem lub konfiskatą. <a href="https://www.ourcommons.ca/documentviewer/en/44-1/FINA/report-5/page-54" rel="noopener">Kanadyjska Izba Gmin o portfelach ↗</a></p>
</div></section>
<section class="mission__section" id="wolnosc"><div class="mission__label">Dlaczego to ważne</div><div class="mission__content">
  <h2>Dostęp do pieniędzy bywa decyzją kogoś innego.</h2>
  <p>Na co dzień konto w banku po prostu działa. Znamy jednak przypadki, w których dostęp do rachunków ograniczano z dnia na dzień. Nie oceniamy tu racji żadnej ze stron. Pokazujemy, że tak się zdarza.</p>
  <div class="mission__stats mission__cases">
    <div><strong>Kanada, 2022</strong><p>Przedstawicielka ministerstwa finansów powiedziała posłom, że na podstawie finansowych przepisów Emergencies Act zamrożono do 210 rachunków, na których było ok. 7,8 mln dolarów kanadyjskich. <a href="https://www.cbc.ca/news/politics/emergency-bank-measures-finance-committee-1.6360769" rel="noopener">CBC ↗</a></p></div>
    <div><strong>Nigeria, 2020</strong><p>Podczas protestów #EndSARS zamknięto rachunek Feminist Coalition, a organizacja zaczęła przyjmować bitcoiny. <a href="https://www.coindesk.com/tech/2020/10/16/nigerian-banks-shut-them-out-so-these-activists-are-using-bitcoin-to-battle-police-brutality" rel="noopener">CoinDesk ↗</a> Według Human Rights Watch bank centralny uzyskał 5 listopada nakaz zamrożenia 20 rachunków w pięciu bankach na trzy miesiące, a wniosek złożył 20 października, kilka dni po zablokowaniu pierwszych kont. <a href="https://www.hrw.org/news/2020/11/13/nigeria-punitive-financial-moves-against-protesters" rel="noopener">HRW ↗</a></p></div>
    <div><strong>Ukraina, 2022</strong><p>26 lutego rząd Ukrainy opublikował adresy do wpłat w bitcoinie i etherze. Wiceminister cyfryzacji mówił, że darowizny w kryptowalutach zbliżają się do 100 mln dolarów, ale zastrzegł, że nie odgrywają „głównej” roli w całej gospodarce kraju. <a href="https://decrypt.co/94712/crypto-helping-ukraine-russia-invasion-deputy-minister" rel="noopener">Decrypt ↗</a></p></div>
  </div>
  <p>Według Human Rights Foundation w 2025 r. 76% ludności świata żyło w reżimach autorytarnych. <a href="https://hrf.org/latest/2025-annual-report/" rel="noopener">HRF ↗</a> To nie znaczy, że Bitcoin chroni przed każdym przymusem: samodzielny portfel utrudnia blokadę przez pośrednika, ale transakcje są publiczne, a sądy mogą nakazać wydanie środków osobie, którą uda się zidentyfikować.</p>
</div></section>
<section class="mission__section" id="bitcoin-only"><div class="mission__label">Nasze stanowisko</div><div class="mission__content">
  <h2>Dlaczego Bitcoin Only?</h2>
  <p>Nie używamy słowa „krypto” jako obietnicy, że wszystkie projekty działają tak samo. Naszym zdaniem warto odróżnić otwartą sieć pieniężną od tokena, którego zasady, emisja albo dostęp zależą od firmy czy wąskiej grupy. Decentralizacja nie jest przełącznikiem: trzeba pytać, kto proponuje zmiany, kto je akceptuje i kto może je zweryfikować.</p>
  <p>Przykład: Ethereum w 2022 r. przeszło na proof of stake i zmieniło sposób emisji ETH. Tether z kolei opisuje politykę zamrażania wskazanych portfeli swojego tokena. To nie jest dowód, że każde inne rozwiązanie jest bezużyteczne. Pokazuje, że mają inne zasady i inne punkty kontroli. <a href="https://ethereum.org/roadmap/merge/issuance/" rel="noopener">Ethereum o zmianie emisji ↗</a> · <a href="https://tether.io/news/tether-introduces-new-policy-to-strengthen-ecosystem-security/" rel="noopener">Tether o zamrażaniu ↗</a></p>
  <p>Dlatego skupiamy się na Bitcoinie, a nie na promowaniu kolejnych monet. Nie sprzedajemy tokena ani nie obiecujemy zysków. Maksymalizm rozumiemy jako nacisk na pieniądz, którego zasad nie da się łatwo narzucić innym, nie jako obowiązek zgadzania się z nami we wszystkim.</p>
  <p>Spór o rozmiar bloków pokazał też, że zmiany wymagają społecznej akceptacji: uczestnicy nie muszą uruchamiać oprogramowania z zasadami, których nie chcą. Istnieją różne interpretacje tego sporu. <a href="https://blog.lopp.net/reflections-upon-bitcoins-block-size-debate" rel="noopener">Jameson Lopp o obu perspektywach ↗</a></p>
</div></section>
<section class="mission__section" id="pytania"><div class="mission__label">Bez zamiatania pod dywan</div><div class="mission__content">
<h2>Trudne pytania są potrzebne.</h2>
<div class="mission__faq">
<details><summary>Energia: czy Bitcoin jej nie marnuje?</summary><p>Zużywa jej dużo i ma wpływ na środowisko. Cambridge szacowało w badaniu z 2025 r. roczne zużycie na 138 TWh, około 0,5% światowego zużycia energii elektrycznej. W tej samej analizie 52,4% energii określono jako zrównoważoną, wliczając energię jądrową. To szacunki oparte na danych z próby, nie pomiar każdego górnika. Naszym zdaniem koszt energii trzeba zestawić z wartością bezpieczeństwa otwartej sieci; to ocena, nad którą można dyskutować. <a href="https://www.jbs.cam.ac.uk/2025/cambridge-study-sustainable-energy-rising-in-bitcoin-mining" rel="noopener">Badanie Cambridge ↗</a></p></details>
<details><summary>Czy Bitcoin jest stabilny i bezpieczny dla oszczędności?</summary><p>Zmienność kursu jest duża: potrafi on gwałtownie spadać i rosnąć. Według analizy 21Shares (firmy wydającej fundusze na krypto, więc nie jest to źródło bezstronne) zmienność roczna sięgała rekordowych 181% w 2013 r., a w 2025 r. spadła nawet do 23%. <a href="https://www.21shares.com/en-eu/insights/how-volatile-is-bitcoin" rel="noopener">21Shares ↗</a> Bitcoin nie daje gwarancji zysku ani zachowania siły nabywczej w wybranym okresie. Można też paść ofiarą oszustwa albo stracić klucze. Ucz się we własnym tempie i nie ryzykuj pieniędzy, których utrata byłaby dla Ciebie katastrofą. To nie jest porada inwestycyjna.</p></details>
<details><summary>Czy nie służy głównie przestępcom?</summary><p>Jak inne formy pieniądza, bywa wykorzystywany do przestępstw, ale także do legalnych płatności i oszczędzania. Transakcje w głównym łańcuchu są publiczne; Bitcoin nie zapewnia automatycznej anonimowości. Według Chainalysis adresy powiązane z nielegalną działalnością otrzymały w 2025 r. co najmniej 154 mld dolarów, czyli mniej niż 1% wszystkich transakcji kryptowalutowych. To dane o całym rynku krypto, nie tylko o Bitcoinie, a „co najmniej” oznacza, że to tylko to, co udało się zidentyfikować. <a href="https://www.chainalysis.com/blog/2026-crypto-crime-report-introduction/" rel="noopener">Chainalysis ↗</a> Dla porównania ONZ szacuje, że rocznie pierze się 2–5% światowego PKB, czyli 800 mld–2 bln dolarów, na całym świecie. <a href="https://www.unodc.org/unodc/rs/money-laundering/overview.html" rel="noopener">UNODC ↗</a> Te liczby powstały różnymi metodami, więc traktuj je jako rząd wielkości, nie jako precyzyjne porównanie. <a href="https://bitcoin.org/en/faq" rel="noopener">Bitcoin.org o prywatności ↗</a></p></details>
<details><summary>Czy Bitcoin nadaje się do codziennych płatności?</summary><p>Główny łańcuch ma ograniczoną przepustowość, a opłaty i czas potwierdzenia się zmieniają. Lightning wykorzystuje kanały płatności poza głównym łańcuchem, by ułatwić szybsze, mniejsze płatności. Różne portfele mają różne kompromisy: czasem kontrolujesz klucze samodzielnie, a czasem powierzasz je operatorowi. <a href="https://help.blockstream.com/education/glossary/lightning-network" rel="noopener">Jak działa Lightning ↗</a></p></details>
<details><summary>Jak w Polsce rozlicza się podatek?</summary><p>Według serwisu podatki.gov.pl (aktualizacja z 24 czerwca 2026 r.) dochód z odpłatnego zbycia kryptowaluty, na przykład sprzedaży za złotówki albo zapłaty nią za towar, opodatkowany jest stawką 19% i rozlicza się go w zeznaniu PIT-38, składanym od 15 lutego do 30 kwietnia kolejnego roku. Wymiana jednej kryptowaluty na inną nie podlega opodatkowaniu. Wydatki na nabycie trzeba wykazać w zeznaniu, nawet jeśli nic nie sprzedałeś. To ogólna informacja, nie porada podatkowa: w swojej sytuacji zapytaj doradcę. <a href="https://podatki.gov.pl/podatki-osobiste/pit/informacje-podstawowe/co-jest-opodatkowane/zbycie-kryptowalut" rel="noopener">Zbycie kryptowalut, podatki.gov.pl ↗</a></p></details>
<details><summary>Co z komputerami kwantowymi?</summary><p>Wystarczająco silne komputery kwantowe mogłyby zagrozić części stosowanej dziś kryptografii. Nie wiadomo, kiedy taka technologia będzie dostępna. Rozwiązania wymagają badań i ewentualnego uzgodnienia zmian, nie ma podstaw, by traktować problem jako już rozwiązany. <a href="https://www.nist.gov/blogs/taking-measure/quantum-computers-may-put-internet-traffic-risk-nist-safeguarding-computers-new" rel="noopener">NIST o zagrożeniu ↗</a></p></details>
</div></div></section>
<section class="mission__section" id="misja"><div class="mission__label">Dwadzieścia Jeden</div><div class="mission__content">
<h2>Po co jest nasza społeczność?</h2>
<p>Przybliżamy Bitcoina w Polsce. Tłumaczymy materiały, dzielimy się wiedzą, spotykamy się w miastach i budujemy projekty. Jesteśmy częścią sieci TwentyOne. Nie musisz być ekspertem ani kupować bitcoina, żeby zacząć zadawać pytania.</p>
<p>Chcesz czytać po polsku? Dwie książki wydało Freedom Publishing: <a href="https://www.swiatksiazki.pl/standard-bitcoina-6711322-ksiazka.html" rel="noopener">„Standard Bitcoina” Saifedeana Ammousa (2020) ↗</a> i <a href="https://www.swiatksiazki.pl/dlaczego-bitcoin-7037940-ksiazka.html" rel="noopener">„Dlaczego Bitcoin” Vijaya Boyapatiego (2022) ↗</a>. O akcji przekazania „Standardu Bitcoina” posłom i senatorom przeczytasz w <a href="{base}/bitcoin-w-parlamencie/">relacji z kampanii</a>.</p>
<p class="cta-row"><a class="btn btn--primary" href="{base}/edukacja/">Zacznij od edukacji</a><a class="btn btn--ghost" href="{base}/bitcoinowa-mapa-polski/">Znajdź społeczność</a></p>
</div></section>
<section class="mission__section mission__archive" id="oryginalny-tekst"><div class="mission__label">Z archiwum</div><div class="mission__content">
<h2>Od czego zaczynaliśmy</h2><p>Oryginalny tekst „Kim jesteśmy?” autorstwa @JesterHodl z 2022 roku zachowujemy poniżej. Przedstawia ówczesny głos społeczności, nie jest aktualizowanym opisem wszystkich faktów.</p>
<details><summary>Rozwiń oryginalny tekst z 2022 roku</summary><div class="prose">@@ORIGINAL@@</div></details>
</div></section>
</article>'''
    # Polish typography on our copy only: keep one-letter words and the link arrow with their neighbours.
    html = re.sub(r'(?<=\s)([wziouaWZIOUA]) (?![^<>]*>)', r'\1&nbsp;', html)
    html = html.replace(' ↗<', '&nbsp;↗<')
    return html.replace('@@ORIGINAL@@', original)
