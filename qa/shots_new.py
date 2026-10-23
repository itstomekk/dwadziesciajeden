from playwright.sync_api import sync_playwright
B="http://127.0.0.1:8721/dwadziesciajeden"
with sync_playwright() as p:
    br=p.firefox.launch(); pg=br.new_page(viewport={"width":1280,"height":900})
    for path,name in [("/","home"),("/poznan/","poz"),("/bitcoin-w-parlamencie/","art"),("/inicjatywy/","ini")]:
        pg.goto(B+path); pg.wait_for_timeout(600); pg.screenshot(path=f"qa/shots/new-{name}.png",full_page=True)
    br.close()
