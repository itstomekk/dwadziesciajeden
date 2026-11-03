from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class InvitationFlowTests(unittest.TestCase):
    def test_join_page_has_invitation_form_for_email_or_npub(self):
        page = (DOCS / "dolacz-do-nas" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-invite-form', page)
        self.assertRegex(page, r'<form[^>]+method="POST"[^>]*data-invite-form')
        self.assertRegex(page, r'<input[^>]+name="contact"')
        self.assertIn("e-mail albo npub", page.lower())
        self.assertIn('name="consent"', page)
        self.assertIn('name="_honey"', page)

    def test_public_site_has_no_telegram_destination_urls(self):
        urls = []
        for suffix in (".html", ".md", ".txt", ".xml", ".json"):
            for page in DOCS.rglob(f"*{suffix}"):
                text = page.read_text(encoding="utf-8")
                urls.extend((page.relative_to(DOCS), url) for url in re.findall(
                    r'https?://(?:t\.me|telegram\.me|telegram\.dog)/[^\s"\'<>)]*', text, re.I))
        self.assertEqual([], urls, f"Telegram destination URLs remain: {urls[:10]}")


if __name__ == "__main__":
    unittest.main()
