#!/usr/bin/python
import optparse
import sys
import unittest

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the Google App Engine SDK installation
PATTERN     Pattern for tests (e.g., *_test.py)"""


def main(sdk_path, pattern):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(
        './test', pattern=pattern)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        sys.exit(1)
    SDK_PATH = args[0]
    PATTERN = args[1] if len(args) == 2 else ''
    main(SDK_PATH, PATTERN)
