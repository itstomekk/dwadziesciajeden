"""Regression tests for the Bitcoin mission and preserved community text."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MissionPageTest(unittest.TestCase):
    def test_generated_mission_and_original_are_accessible(self):
        page = (ROOT / 'docs/kim-jestesmy/index.html').read_text(encoding='utf-8')
        self.assertIn('<h1>Dlaczego Bitcoin', page)
        self.assertIn('Bitcoin Only', page)
        self.assertIn('id="oryginalny-tekst"', page)
        self.assertIn('@JesterHodl', page)
        self.assertIn('https://bitcoin.org/en/faq', page)
        self.assertIn('zmienność', page.lower())
        self.assertIn('Energia', page)
        index = json.loads((ROOT / 'docs/search.json').read_text(encoding='utf-8'))
        hits = [p for p in index if p['u'] == '/kim-jestesmy/']
        self.assertEqual(len(hits), 1)
        self.assertIn('Dlaczego Bitcoin', hits[0]['t'])
        twin = (ROOT / 'docs/kim-jestesmy/index.md').read_text(encoding='utf-8')
        self.assertIn('Dlaczego Bitcoin', twin)

    def test_verified_numbers_and_polish_context(self):
        page = (ROOT / 'docs/kim-jestesmy/index.html').read_text(encoding='utf-8')
        for needle in ('10 000 : 1', '75,8 tys.', '9,8 mln', '685,8', '×4,04', 'Meditata',
                       '2,5%', '840 000', '3,125 BTC', '210 rachunków', '7,8 mln',
                       '154 mld', '19%', 'PIT-38', '181%', 'Dlaczego Bitcoin'):
            self.assertIn(needle, page, needle)
        for host in ('stat.gov.pl', 'nbp.pl', 'dzieje.pl', 'federalreservehistory.org',
                     'github.com/bitcoin/bitcoin', 'bitnodes.io', 'cbc.ca', 'hrw.org',
                     'decrypt.co', 'chainalysis.com', 'unodc.org', 'podatki.gov.pl'):
            self.assertIn(host, page, host)
        self.assertIn('id="wolnosc"', page)
        self.assertIn('<svg', page.split('id="pieniadz"')[1].split('id="jak-dziala"')[0])

    def test_cpi_arithmetic_matches_gus_series(self):
        import sys
        sys.path.insert(0, str(ROOT))
        import mission_page as mp
        self.assertEqual(len(mp.GUS_CPI), 31)
        self.assertAlmostEqual(mp.chain(1996, 2025), 4.0435, places=3)
        self.assertAlmostEqual(100 / mp.chain(1996, 2025), 24.73, places=2)
        self.assertAlmostEqual(mp.chain(2022, 2023), 1.2744, places=3)


if __name__ == '__main__':
    unittest.main()
