# XLIFF Linter

[![PyPI version](https://badge.fury.io/py/moz-xliff-linter.svg)](https://badge.fury.io/py/moz-xliff-linter)

[![Unit Tests](https://github.com/mozilla-l10n/moz-xliff-linter/actions/workflows/tests.yml/badge.svg)](https://github.com/mozilla-l10n/moz-xliff-linter/actions/workflows/tests.yml)

It allows to check reference FTL XLIFF for common issues:
* Use of incorrect characters (e.g. `'` instead of `’`).
* Lack of localization comments for strings with placeables.
* Use of hard-coded brand names.

See [config.json](src/xliff_linter/config.json) for a bare config file.
