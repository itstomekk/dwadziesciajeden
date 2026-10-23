from playwright.sync_api import sync_playwright
B="http://127.0.0.1:8721/dwadziesciajeden"
with sync_playwright() as p:
    br=p.firefox.launch(); pg=br.new_page(viewport={"width":1280,"height":900})
    for path,name in [("/","home"),("/edukacja/","edu"),("/bitcoinowa-mapa-polski/","mapa")]:
        pg.goto(B+path); pg.wait_for_timeout(3200); pg.screenshot(path=f"qa/shots/new-{name}.png",full_page=True)
    br.close()
