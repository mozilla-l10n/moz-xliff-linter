import unittest

from src.xliff_linter.linter import XliffChecker


class TestBrands(unittest.TestCase):
    def test_brand_error(self):
        config = {
            "brands": {
                "enabled": True,
                "exclusions": ["dummy.xliff:test_brands_excluded"],
                "brand_names": ["Mozilla"],
            }
        }
        checker = XliffChecker(config)
        content = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file>
    <body>
      <trans-unit id="test_brands">
        <source>This text mentions Mozilla as a brand.</source>
        <note>Some comment</note>
      </trans-unit>
      <trans-unit id="test_brands_excluded">
        <source>This text mentions Mozilla as a brand, but it's excluded.</source>
        <note>Some comment</note>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        errors = checker.process_content(content, "dummy.xliff", ref_path=".")
        self.assertEqual(len(errors), 1)
        self.assertTrue("Mozilla" in errors[0])


if __name__ == "__main__":
    unittest.main()
