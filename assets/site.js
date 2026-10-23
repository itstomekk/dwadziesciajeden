(() => {
  const base = document.body.dataset.base || "";

  // live block height (mempool.space); silent on failure
  const tips = document.querySelectorAll("[data-tip]");
  if (tips.length && window.fetch) {
    fetch("https://mempool.space/api/blocks/tip/height").then((r) => r.ok ? r.text() : Promise.reject())
      .then((h) => { const n = Number(h); if (n > 0) tips.forEach((t) => { t.textContent = t.textContent.startsWith("#") ? "#" + n.toLocaleString("pl-PL") : String(n); }); })
      .catch(() => tips.forEach((t) => { t.textContent = t.textContent.startsWith("#") ? "po bloku" : "tick tock, next block"; }));
  }

  // mobile menu
  const menuBtn = document.querySelector(".menu-btn");
  const nav = document.getElementById("nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
  }

  // privacy-friendly YouTube: load the iframe only on click
  document.querySelectorAll(".video__frame[data-yt]").forEach((box) => {
    const a = box.querySelector("a");
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      const f = document.createElement("iframe");
      f.src = `https://www.youtube-nocookie.com/embed/${box.dataset.yt}?autoplay=1`;
      f.allow = "autoplay; encrypted-media; picture-in-picture";
      f.allowFullscreen = true;
      f.title = a.textContent.trim() || "YouTube";
      box.replaceChildren(f);
    });
  });

  // copy buttons (npub)
  document.querySelectorAll("[data-copy]").forEach((btn) => btn.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(btn.dataset.copy); btn.textContent = "Skopiowano"; }
    catch { btn.textContent = "Zaznacz i skopiuj"; }
    setTimeout(() => { btn.textContent = "Kopiuj"; }, 2000);
  }));

  // chronicle filters
  const filters = document.querySelectorAll(".filters button");
  filters.forEach((btn) => btn.addEventListener("click", () => {
    filters.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    const cls = btn.dataset.filter;
    document.querySelectorAll(".tl-wrap .tl__item").forEach((li) => {
      li.classList.toggle("is-hidden", !!cls && !li.classList.contains(cls));
    });
    document.querySelectorAll(".tl-wrap .tl-year").forEach((h) => {
      const list = h.nextElementSibling;
      const any = list && list.querySelector(".tl__item:not(.is-hidden)");
      h.style.display = any ? "" : "none";
    });
  }));

  // search
  const dlg = document.getElementById("search");
  const q = document.getElementById("search-q");
  const res = document.getElementById("search-res");
  let index = null;
  const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l");
  async function load() {
    if (index) return index;
    const r = await fetch(`${base}/search.json`);
    index = (await r.json()).map((d) => ({ ...d, n: norm(`${d.t} ${d.g.join(" ")} ${d.x}`), nt: norm(d.t) }));
    return index;
  }
  function open() { dlg.hidden = false; q.focus(); load(); }
  function close() { dlg.hidden = true; }
  document.querySelectorAll("[data-search-open]").forEach((b) => b.addEventListener("click", open));
  document.querySelectorAll("[data-search-close]").forEach((b) => b.addEventListener("click", close));
  dlg.addEventListener("click", (ev) => { if (ev.target === dlg) close(); });
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !dlg.hidden) close();
    if ((ev.key === "/" || (ev.key === "k" && (ev.ctrlKey || ev.metaKey))) && dlg.hidden && !/input|textarea/i.test(document.activeElement.tagName)) {
      ev.preventDefault(); open();
    }
  });
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  q.addEventListener("input", async () => {
    const data = await load();
    const terms = norm(q.value.trim()).split(/\s+/).filter(Boolean);
    if (!terms.length) { res.innerHTML = ""; return; }
    const hits = data
      .map((d) => ({ d, s: terms.every((t) => d.n.includes(t)) ? terms.reduce((a, t) => a + (d.nt.includes(t) ? 5 : 1), 0) : 0 }))
      .filter((h) => h.s > 0).sort((a, b) => b.s - a.s).slice(0, 12);
    res.innerHTML = hits.length ? hits.map(({ d }) => {
      const i = d.n.indexOf(terms[0]);
      const snip = d.x ? d.x.slice(Math.max(0, i - 60), i + 110) : "";
      return `<li><a href="${base}${d.u}"><small>${esc(d.k)}</small><strong>${esc(d.t)}</strong><span>${esc(snip)}</span></a></li>`;
    }).join("") : `<li><a href="${base}/artykuly/"><small>brak wyników</small><strong>Nic nie znaleziono</strong><span>Zobacz wszystkie artykuły</span></a></li>`;
  });
})();
