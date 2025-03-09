import unittest

from src.xliff_linter.linter import XliffChecker


class TestPlaceables(unittest.TestCase):
    def test_missing_placeables_in_comment(self):
        config = {"placeables": {"enabled": True, "exclusions": []}}
        checker = XliffChecker(config, platform="qt")
        content = """<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file>
    <body>
      <trans-unit id="test_placeables_error_1">
        <source>This is a test with a placeable %1</source>
        <note>This comment does not include the placeable</note>
      </trans-unit>
      <trans-unit id="test_placeables_ok_1">
        <source>This is a test with a placeable %1</source>
        <note>This comment includes %1</note>
      </trans-unit>
      <trans-unit id="test_placeables_error_2">
        <source>This is a test with two placeables: %1 and %2</source>
        <note>This comment does not include the placeable</note>
      </trans-unit>
      <trans-unit id="test_placeables_error_2b">
        <source>This is a test with two placeables: %1 and %2</source>
        <note>This comment includes only one placeable %1</note>
      </trans-unit>
      <trans-unit id="test_placeables_ok_2">
        <source>This is a test with two placeables: %1 and %2</source>
        <note>This comment includes only both placeables: %1 and %2</note>
      </trans-unit>
      <trans-unit id="test_placeables_error_3">
        <source>This is a test with two placeables: %1 and %2</source>
      </trans-unit>
    </body>
  </file>
</xliff>
"""
        errors = checker.process_content(content, "dummy.xliff", ref_path=".")
        self.assertEqual(len(errors), 4)
        self.assertTrue("%1" in errors[0])
        self.assertTrue("%2" in errors[1])
        self.assertTrue("following placeables: %2" in errors[2])
        self.assertTrue("The string doesn't have a comment." in errors[3])


if __name__ == "__main__":
    unittest.main()
