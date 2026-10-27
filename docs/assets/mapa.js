/* Bitcoinowa Mapa Polski: BTC Map snapshot (assets/btcmap-pl.json) on Leaflet, with filters and grouping.
   Built by build.py btcmap_app(); data from tools/fetch_btcmap.py. No cookies, no tracking; map tiles from OpenStreetMap. */
(function () {
  "use strict";
  var CATS = [
    ["jedzenie", "Jedzenie i picie"], ["sklepy", "Sklepy"], ["uslugi", "Usługi"], ["zdrowie", "Zdrowie i uroda"],
    ["nocleg", "Noclegi"], ["rozrywka", "Sport i rozrywka"], ["kantor", "Kantory"], ["atm", "Bankomaty BTC"]
  ];
  var CAT_LABEL = {}; CATS.forEach(function (c) { CAT_LABEL[c[0]] = c[1]; });
  var DEFAULT_OFF = { atm: true, kantor: true };   // "where can I pay": merchants first, exchanges on request
  var PAYS = [["ln", "⚡ Lightning"], ["oc", "₿ On-chain"], ["nfc", "Zbliżeniowo"]];
  var GROUPS = [["city", "miasta"], ["woj", "województwa"], ["c", "rodzaju"]];
  var DAY = 864e5;

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    for (var k in attrs || {}) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "html") n.innerHTML = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l"); }
  function age(v) { return v ? (Date.now() - Date.parse(v)) / DAY : Infinity; }
  function ageLabel(v) {
    if (!v) return "niepotwierdzone";
    var d = age(v);
    if (d < 45) return "potwierdzone niedawno";
    if (d < 365) return "potwierdzone " + Math.round(d / 30) + " mies. temu";
    var y = Math.floor(d / 365);
    return "potwierdzone " + (y === 1 ? "rok" : y + (y < 5 ? " lata" : " lat")) + " temu";
  }
  function fresh(v) { var d = age(v); return d <= 365 ? "f1" : d <= 730 ? "f2" : "f3"; }

  function init(root) {
    if (!window.L) return;
    var lockCity = root.getAttribute("data-city") || "";
    var params = new URLSearchParams(location.search);
    var st = {
      q: params.get("q") || "",
      cats: {}, pays: {},
      city: lockCity || params.get("miasto") || "",
      fresh: params.get("swiezosc") || "",
      group: params.get("grupuj") || (lockCity ? "c" : "city")
    };
    var catParam = params.get("kat");
    CATS.forEach(function (c) { st.cats[c[0]] = catParam ? catParam.split(",").indexOf(c[0]) > -1 : !DEFAULT_OFF[c[0]] || !!lockCity; });
    (params.get("platnosc") || "").split(",").forEach(function (p) { if (p) st.pays[p] = true; });

    var mapBox = root.querySelector(".bmap__map"), list = root.querySelector(".bmap__list"),
        tools = root.querySelector(".bmap__tools"), count = root.querySelector("[data-count]");
    var map = L.map(mapBox, { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([52.07, 19.48], 6);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · dane: <a href="https://btcmap.org/country/pl">BTC Map</a>'
    }).addTo(map);
    mapBox.addEventListener("click", function () { map.scrollWheelZoom.enable(); }, { once: true });
    var cluster = L.markerClusterGroup({
      showCoverageOnHover: false, maxClusterRadius: 46, spiderfyOnMaxZoom: true,
      iconCreateFunction: function (c) {
        var n = c.getChildCount();
        return L.divIcon({ className: "bmap-cl", html: "<span>" + n + "</span>", iconSize: n > 99 ? [46, 34] : [38, 34] });
      }
    }).addTo(map);

    fetch(root.getAttribute("data-src")).then(function (r) { return r.json(); }).then(function (data) {
      var all = data.places, markers = {};
      root.querySelector("[data-fetched]").textContent = data.fetched;
      if (lockCity) all = all.filter(function (p) { return p.city === lockCity; });

      // ---- controls
      var search = el("input", { type: "search", class: "bmap__q", placeholder: "Szukaj: nazwa, ulica, miasto", "aria-label": "Szukaj miejsca", value: st.q });
      var catBox = el("div", { class: "bmap__chips", role: "group", "aria-label": "Rodzaj miejsca" });
      var payBox = el("div", { class: "bmap__chips", role: "group", "aria-label": "Sposób płatności" });
      var cityNames = {};
      all.forEach(function (p) { if (p.city) cityNames[p.city] = (cityNames[p.city] || 0) + 1; });
      var citySel = el("select", { "aria-label": "Miasto" }, [el("option", { value: "", text: "Cała Polska" })]);
      Object.keys(cityNames).sort(function (a, b) { return cityNames[b] - cityNames[a] || a.localeCompare(b, "pl"); }).forEach(function (c) {
        citySel.appendChild(el("option", { value: c, text: c + " (" + cityNames[c] + ")" }));
      });
      citySel.value = st.city;
      var freshSel = el("select", { "aria-label": "Kiedy potwierdzone" }, [
        el("option", { value: "", text: "Wszystkie potwierdzenia" }),
        el("option", { value: "1", text: "Potwierdzone w ostatnim roku" }),
        el("option", { value: "2", text: "Potwierdzone w ostatnich 2 latach" })]);
      freshSel.value = st.fresh;
      var groupSel = el("select", { "aria-label": "Grupuj listę" });
      GROUPS.forEach(function (g) { groupSel.appendChild(el("option", { value: g[0], text: "Grupuj według " + g[1] })); });
      groupSel.value = st.group;
      var reset = el("button", { type: "button", class: "bmap__reset", text: "Wyczyść filtry" });

      function chip(box, key, label, on, kind) {
        var b = el("button", { type: "button", "aria-pressed": on ? "true" : "false", "data-key": key },
          [el("span", { class: "bmap__lbl", text: label }), el("span", { class: "bmap__n" })]);
        b.addEventListener("click", function () {
          var on;
          if (kind === "exch") { on = !(st.cats.atm || st.cats.kantor); st.cats.atm = st.cats.kantor = on; }
          else { var set = kind === "cat" ? st.cats : st.pays; on = set[key] = !set[key]; }
          b.setAttribute("aria-pressed", on ? "true" : "false"); update(true);
        });
        box.appendChild(b);
      }
      CATS.forEach(function (c) {
        if (!DEFAULT_OFF[c[0]] && all.some(function (p) { return p.c === c[0]; })) chip(catBox, c[0], c[1], st.cats[c[0]], "cat");
      });
      // ATMs and exchanges: one switch for both
      if (all.some(function (p) { return DEFAULT_OFF[p.c]; })) chip(catBox, "exch", "Bankomaty i kantory", st.cats.atm || st.cats.kantor, "exch");
      PAYS.forEach(function (p) { chip(payBox, p[0], p[1], st.pays[p[0]], "pay"); });

      tools.appendChild(el("div", { class: "bmap__row" }, [search, lockCity ? null : citySel, freshSel, groupSel]));
      tools.appendChild(el("div", { class: "bmap__chiprow" }, [catBox, payBox, reset]));

      var t;
      search.addEventListener("input", function () { clearTimeout(t); t = setTimeout(function () { st.q = search.value; update(true); }, 150); });
      citySel.addEventListener("change", function () { st.city = citySel.value; update(true); });
      freshSel.addEventListener("change", function () { st.fresh = freshSel.value; update(false); });
      groupSel.addEventListener("change", function () { st.group = groupSel.value; update(false); });
      reset.addEventListener("click", function () {
        st.q = ""; search.value = ""; st.city = lockCity; citySel.value = lockCity; st.fresh = ""; freshSel.value = "";
        CATS.forEach(function (c) { st.cats[c[0]] = !DEFAULT_OFF[c[0]] || !!lockCity; });
        st.pays = {};
        root.querySelectorAll(".bmap__chips button").forEach(function (b) {
          var k = b.getAttribute("data-key");
          b.setAttribute("aria-pressed", (k === "exch" ? st.cats.atm : st.cats[k] || st.pays[k]) ? "true" : "false");
        });
        update(true);
      });

      // ---- markers
      all.forEach(function (p) {
        var m = L.marker([p.lat, p.lon], {
          title: p.n, keyboard: false,
          icon: L.divIcon({ className: "bmap-pin bmap-pin--" + p.c + " bmap-pin--" + fresh(p.v), iconSize: [16, 16], iconAnchor: [8, 8] })
        });
        m.bindPopup(function () { return card(p, true); }, { maxWidth: 300, className: "bmap-pop" });
        markers[p.id] = m;
      });

      function passes(p, skip) {
        if (skip !== "cat" && !st.cats[p.c]) return false;
        for (var k in st.pays) if (st.pays[k] && skip !== "pay" && !p[k]) return false;
        if (st.city && p.city !== st.city) return false;
        if (st.fresh && age(p.v) > 365 * +st.fresh) return false;
        if (st.q) {
          var h = norm([p.n, p.a, p.city, p.woj, p.op, CAT_LABEL[p.c]].join(" "));
          if (norm(st.q).split(/\s+/).some(function (w) { return w && h.indexOf(w) < 0; })) return false;
        }
        return true;
      }

      function card(p, inPopup) {
        var pays = [p.ln ? "⚡ Lightning" : "", p.oc ? "₿ on-chain" : "", p.nfc ? "zbliżeniowo" : ""].filter(Boolean).join(" · ");
        var where = [p.a, p.city && (!p.a || p.a.indexOf(p.city) < 0) ? p.city : ""].filter(Boolean).join(", ");
        var links = [
          '<a href="https://btcmap.org/merchant/' + p.id + '" rel="noopener">BTC Map</a>',
          '<a href="https://www.openstreetmap.org/?mlat=' + p.lat + "&mlon=" + p.lon + "#map=18/" + p.lat + "/" + p.lon + '" rel="noopener">Mapa OSM</a>',
          p.web ? '<a href="' + encodeURI(p.web) + '" rel="noopener nofollow">Strona</a>' : ""
        ].filter(Boolean).join(" ");
        var esc = function (s) { return String(s || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
        return '<div class="bmap-card' + (inPopup ? " bmap-card--pop" : "") + '">' +
          '<span class="bmap-card__meta">' + esc(CAT_LABEL[p.c]) + (p.op ? " · " + esc(p.op) : "") + "</span>" +
          (inPopup ? "<strong>" + esc(p.n) + "</strong>" : '<button type="button" class="bmap-card__go" aria-label="Pokaż na mapie: ' + esc(p.n) + '">' + esc(p.n) + "</button>") +
          (where ? '<span class="bmap-card__addr">' + esc(where) + "</span>" : "") +
          (pays ? '<span class="bmap-card__pay">' + pays + "</span>" : "") +
          (p.oh && inPopup ? '<span class="bmap-card__oh">' + esc(p.oh) + "</span>" : "") +
          '<span class="bmap-card__v bmap-card__v--' + fresh(p.v) + '"' + (p.v ? ' title="' + p.v + '"' : "") + ">" + ageLabel(p.v) + "</span>" +
          '<span class="bmap-card__links">' + links + "</span></div>";
      }

      function syncUrl() {
        if (lockCity) return;
        var q = new URLSearchParams();
        var on = CATS.filter(function (c) { return st.cats[c[0]]; }).map(function (c) { return c[0]; });
        var def = CATS.filter(function (c) { return !DEFAULT_OFF[c[0]]; }).map(function (c) { return c[0]; });
        if (on.join() !== def.join()) q.set("kat", on.join(","));
        var pays = Object.keys(st.pays).filter(function (k) { return st.pays[k]; });
        if (pays.length) q.set("platnosc", pays.join(","));
        if (st.city) q.set("miasto", st.city);
        if (st.fresh) q.set("swiezosc", st.fresh);
        if (st.group !== "city") q.set("grupuj", st.group);
        if (st.q) q.set("q", st.q);
        var s = q.toString();
        history.replaceState(null, "", location.pathname + (s ? "?" + s : "") + location.hash);
      }

      function update(refit) {
        var shown = all.filter(function (p) { return passes(p); });
        // chip counts: what you would get with that chip on, given the other filters
        catBox.querySelectorAll("button").forEach(function (b) {
          var k = b.getAttribute("data-key");
          b.querySelector(".bmap__n").textContent = all.filter(function (p) {
            return (k === "exch" ? DEFAULT_OFF[p.c] : p.c === k) && passes(p, "cat");
          }).length;
        });
        payBox.querySelectorAll("button").forEach(function (b) {
          var k = b.getAttribute("data-key");
          b.querySelector(".bmap__n").textContent = all.filter(function (p) { return p[k] && passes(p, "pay"); }).length;
        });
        cluster.clearLayers();
        cluster.addLayers(shown.map(function (p) { return markers[p.id]; }));
        count.textContent = shown.length;
        if (refit && shown.length) {
          var b = L.latLngBounds(shown.map(function (p) { return [p.lat, p.lon]; }));
          map.fitBounds(b.pad(0.08), { maxZoom: shown.length === 1 ? 16 : 13, animate: false });
        }
        renderList(shown);
        syncUrl();
      }

      function renderList(shown) {
        list.innerHTML = "";
        if (!shown.length) {
          list.appendChild(el("p", { class: "bmap__empty", text: "Nic nie pasuje do filtrów. Wyczyść je albo dodaj miejsce na BTC Map." }));
          return;
        }
        var key = st.group, groups = {};
        shown.forEach(function (p) {
          var g = key === "c" ? CAT_LABEL[p.c] : (p[key] || (key === "woj" ? "Bez województwa" : "Bez miasta"));
          (groups[g] = groups[g] || []).push(p);
        });
        var names = Object.keys(groups).sort(function (a, b) { return groups[b].length - groups[a].length || a.localeCompare(b, "pl"); });
        names.forEach(function (g, i) {
          var det = el("details", { class: "bmap__grp" });
          if (i < 3 || names.length <= 4 || shown.length <= 40) det.open = true;
          det.appendChild(el("summary", {}, [el("span", { text: g }), el("span", { class: "bmap__n", text: String(groups[g].length) })]));
          var ul = el("ul");
          groups[g].sort(function (a, b) { return age(a.v) - age(b.v) || a.n.localeCompare(b.n, "pl"); }).forEach(function (p) {
            var btn = el("div", { class: "bmap__item", html: card(p, false) });
            btn.querySelector(".bmap-card__go").addEventListener("click", function () {
              cluster.zoomToShowLayer(markers[p.id], function () { markers[p.id].openPopup(); });
              if (window.matchMedia("(max-width:860px)").matches) mapBox.scrollIntoView({ behavior: "smooth", block: "center" });
            });
            ul.appendChild(el("li", {}, [btn]));
          });
          det.appendChild(ul);
          list.appendChild(det);
        });
      }

      update(true);
    }).catch(function () {
      list.innerHTML = '<p class="bmap__empty">Nie udało się wczytać danych. Zobacz mapę na <a href="https://btcmap.org/country/pl">btcmap.org</a>.</p>';
    });
  }

  document.querySelectorAll("[data-bmap]").forEach(init);
})();
