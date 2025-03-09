import unittest

from src.xliff_linter.linter import XliffChecker


class TestEllipsis(unittest.TestCase):
    def test_ellipsis_error(self):
        config = {
            "ellipsis": {
                "enabled": True,
                "exclusions": ["dummy.xliff:test_ellipsis_excluded"],
            }
        }
        checker = XliffChecker(config)
        content = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file>
    <body>
      <trans-unit id="test_ellipsis">
        <source>This text contains an ellipsis with 3 dots ...</source>
        <note>Some comment</note>
      </trans-unit>
      <trans-unit id="test_ellipsis_ok">
        <source>This text contains a correct ellipsis …</source>
        <note>Some comment</note>
      </trans-unit>
      <trans-unit id="test_ellipsis_excluded">
        <source>This text contains an ellipsis with 3 dots ... but it's excluded</source>
        <note>Some comment</note>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        errors = checker.process_content(content, "dummy.xliff", ref_path=".")
        self.assertEqual(len(errors), 1)
        self.assertTrue("..." in errors[0])


if __name__ == "__main__":
    unittest.main()
