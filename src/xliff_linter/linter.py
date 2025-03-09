#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import os
import re
import sys

from glob import glob

from lxml import etree


class XliffChecker:
    NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}

    def __init__(self, config):
        self.config = config
        self.placeable_pattern = r"%(?:\d+\$@|@|d)"

    def process_content(self, content, file_path="test.xliff", ref_path=None):
        """
        Process a given XLIFF content string.

        Args:
            content (str): The XLIFF content.
            file_path (str): An identifier for error messages.
            ref_path (str): Base path for relative file paths. Defaults to directory of file_path.

        Returns:
            List[str]: A list of error messages.
        """
        errors = []
        if ref_path is None:
            ref_path = os.path.dirname(os.path.realpath(file_path))
        try:
            # Convert to bytes if content is a str
            if isinstance(content, str):
                content = content.encode("utf-8")
            tree = etree.fromstring(content)
        except Exception as e:
            errors.append(f"ERROR: Can't parse {file_path}\n{e}")
            return errors

        # Iterate over all trans-unit nodes
        for trans_node in tree.xpath("//x:trans-unit", namespaces=self.NS):
            # Get the comment (note) text; if missing, XPath returns an empty string.
            comment = trans_node.xpath("string(./x:note)", namespaces=self.NS)
            for source in trans_node.xpath("./x:source", namespaces=self.NS):
                rel_file_path = os.path.relpath(file_path, ref_path)
                string_id = f"{rel_file_path}:{trans_node.get('id')}"
                ref_string = source.text or ""
                self.check_placeables(ref_string, string_id, comment, errors)
                self.check_ellipsis(ref_string, string_id, errors)
                self.check_quotes(ref_string, string_id, errors)
                self.check_brands(ref_string, string_id, errors)
        return errors

    def check_placeables(self, ref_string, string_id, comment, errors):
        config_placeables = self.config.get("placeables", {})
        if not config_placeables.get("enabled", False):
            return

        exclusions = set(config_placeables.get("exclusions", []))
        if string_id in exclusions:
            return

        xml_placeables = set(re.findall(self.placeable_pattern, ref_string))
        if xml_placeables:
            comment_placeables = (
                set(re.findall(self.placeable_pattern, comment)) if comment else set()
            )
            missing = xml_placeables - comment_placeables
            if not comment:
                errors.append(
                    f"Identified placeables in string {string_id}: {', '.join(sorted(xml_placeables))}\n"
                    f"  The string doesn't have a comment.\n"
                    f"  Text: {ref_string!r}\n"
                )
            elif missing:
                errors.append(
                    f"Identified placeables in string {string_id}: {', '.join(sorted(xml_placeables))}\n"
                    f"  Comment does not include the following placeables: {', '.join(sorted(missing))}\n"
                    f"  Text: {ref_string!r}\n"
                    f"  Comment: {comment}"
                )

    def check_ellipsis(self, ref_string, string_id, errors):
        config_ellipsis = self.config.get("ellipsis", {})
        if config_ellipsis.get("enabled", False):
            exclusions = set(config_ellipsis.get("exclusions", []))
            if "..." in ref_string and string_id not in exclusions:
                errors.append(f"'...' found in {string_id}\n  Text: {ref_string!r}")

    def check_quotes(self, ref_string, string_id, errors):
        config_quotes = self.config.get("quotes", {})
        if not config_quotes.get("enabled", False) or string_id in set(
            config_quotes.get("exclusions", [])
        ):
            return
        if "'" in ref_string:
            errors.append(
                f"' found in {string_id} (should use ’)\n  Text: {ref_string!r}"
            )
        if '"' in ref_string:
            errors.append(
                f'" found in {string_id} (should use “”)\n  Text: {ref_string!r}'
            )

    def check_brands(self, ref_string, string_id, errors):
        config_brands = self.config.get("brands", {})
        if not config_brands.get("enabled", False) or string_id in set(
            config_brands.get("exclusions", [])
        ):
            return
        for brand in config_brands.get("brand_names", []):
            if brand in ref_string:
                errors.append(
                    f"{brand} found in {string_id} (should use a run-time placeable)\n  Text: {ref_string!r}"
                )


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        required=True,
        dest="ref_path",
        help="Path to folder with reference XLIFF files",
    )
    parser.add_argument(
        "--config", required=True, dest="config_file", help="Path to JSON config file"
    )
    parser.add_argument(
        "--platform",
        dest="platform",
        help="Platform type",
        choices=["ios", "qt"],
        default="ios",
    )
    args = parser.parse_args()

    try:
        with open(args.config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        sys.exit(f"Error loading config: {e}")

    ref_path = os.path.realpath(args.ref_path)
    files = glob(os.path.join(ref_path, "**", "*.xliff"), recursive=True)
    if not files:
        sys.exit("No XLIFF files found.")
    files.sort()

    checker = XliffChecker(config)
    all_errors = []

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        errors = checker.process_content(content, file_path, ref_path)
        all_errors.extend(errors)

    if all_errors:
        output_lines = [f"\nSource errors ({len(all_errors)})"]
        output_lines.extend(f"\n  {err}" for err in all_errors)
        print("\n".join(output_lines))
        print(f"\nTotal errors: {len(all_errors)}")
        sys.exit(1)
    else:
        print("No issues found.")


if __name__ == "__main__":
    main()
