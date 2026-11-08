import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BitcoinWPolsce(unittest.TestCase):
    def test_hub_and_chronicle(self):
        page = (ROOT / 'docs/bitcoinowa-mapa-polski/index.html').read_text(encoding='utf-8')
        self.assertIn('<h1>Bitcoin w Polsce</h1>', page)
        self.assertIn('id="miasta"', page)
        self.assertIn('id="kronika"', page)
        self.assertRegex(page, r'<details[^>]*id="kronika"')
        self.assertIn('class="tl-wrap"', page)
        self.assertIn('href="/projekty/"', page)
        projects = json.loads((ROOT / 'content/projekty.json').read_text(encoding='utf-8'))['projects']
        self.assertIn(f'{len(projects)} projektów', page)

    def test_navigation_and_old_chronicle(self):
        home = (ROOT / 'docs/index.html').read_text(encoding='utf-8')
        nav = re.search(r'<nav[^>]*>.*?</nav>', home, re.S).group()
        self.assertIn('Bitcoin w Polsce', nav)
        self.assertNotIn('>Kronika</a>', nav)
        old = (ROOT / 'docs/kronika/index.html').read_text(encoding='utf-8')
        self.assertIn('class="tl-wrap"', old)


if __name__ == '__main__':
    unittest.main()
