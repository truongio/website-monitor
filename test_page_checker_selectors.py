import unittest
from unittest.mock import MagicMock
from monitor.checker import PageChecker


class PageCheckerSelectorTests(unittest.TestCase):
    def test_check_page_uses_selector_override(self):
        checker = PageChecker()
        checker.fetch_page = MagicMock(return_value="<html><button>Buy</button></html>")
        checker.cleaner.process_html_with_selectors = MagicMock(
            return_value=("button content", "btn-hash")
        )
        checker.cleaner.process_html = MagicMock(
            return_value=("full content", "full-hash")
        )

        result = checker.check_page(
            "https://example.com/product",
            previous_state=None,
            selectors_override=['button.buy']
        )

        self.assertEqual(result['content_hash'], "btn-hash")
        self.assertEqual(result['snippet'], "button content")
        self.assertEqual(result['selectors'], ['button.buy'])
        checker.cleaner.process_html_with_selectors.assert_called_once_with(
            "<html><button>Buy</button></html>",
            ['button.buy']
        )
        checker.cleaner.process_html.assert_not_called()

    def test_check_page_defaults_to_full_content_without_selectors(self):
        checker = PageChecker()
        checker.fetch_page = MagicMock(return_value="<html><body>Full page</body></html>")
        checker.cleaner.process_html_with_selectors = MagicMock(
            return_value=("button content", "btn-hash")
        )
        checker.cleaner.process_html = MagicMock(
            return_value=("full content", "full-hash")
        )

        result = checker.check_page("https://example.com/product", previous_state=None)

        self.assertEqual(result['content_hash'], "full-hash")
        self.assertEqual(result['snippet'], "full content")
        self.assertIsNone(result.get('selectors'))
        checker.cleaner.process_html.assert_called_once()
        checker.cleaner.process_html_with_selectors.assert_not_called()


if __name__ == "__main__":
    unittest.main()
