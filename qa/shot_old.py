from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br=p.firefox.launch(); pg=br.new_page(viewport={"width":1280,"height":900})
    for u,n in [("https://dwadziesciajeden.pl/","old-home"),("https://dwadziesciajeden.pl/kim-jestesmy/","old-kim")]:
        pg.goto(u,timeout=60000); pg.wait_for_timeout(2500); pg.screenshot(path=f"qa/shots/{n}.png",full_page=True)
    print(pg.evaluate("()=>{const s=getComputedStyle(document.body),h=document.querySelector('h1,h2');return [s.fontFamily,s.color,s.backgroundColor,h&&getComputedStyle(h).fontFamily,h&&getComputedStyle(h).fontWeight]}"))
    br.close()
