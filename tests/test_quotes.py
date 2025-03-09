import unittest

from src.xliff_linter.linter import XliffChecker


class TestQuotes(unittest.TestCase):
    def test_quotes_error(self):
        config = {"quotes": {"enabled": True, "exclusions": []}}
        checker = XliffChecker(config)
        content = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file>
    <body>
      <trans-unit id="test_quotes">
        <source>This text has a 'single quote' and "double quote"</source>
        <note>Some comment</note>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        errors = checker.process_content(content, "dummy.xliff", ref_path=".")
        self.assertTrue(any("found in" in error and "'" in error for error in errors))
        self.assertTrue(any("found in" in error and '"' in error for error in errors))


if __name__ == "__main__":
    unittest.main()
