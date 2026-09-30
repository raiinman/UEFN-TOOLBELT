"""
UEFN Toolbelt - list_untested.py (migration shim)
==================================================
This script no longer reports coverage. The registry-derived coverage report
replaced it and runs from a repository checkout, from the repository root:

    py -3 scripts/coverage_report.py

This shim reads no repository file, imports nothing from `scripts/`, registers
no tool, and is never loaded by the editor: deployed projects receive this
package without `scripts/`.

Exit status 3: it only points to the replacement and reports no coverage. The
old script exited 0 (all covered) or 1 (gaps found); 3 is neither, so no
caller can read this as a coverage result.
"""

import sys


def main() -> int:
    print("list_untested.py no longer reports coverage.")
    print("The coverage report now runs from a repository checkout.")
    print("From the repository root, run:")
    print("    py -3 scripts/coverage_report.py")
    print("This script reports no coverage itself (exit status 3).")
    return 3


if __name__ == "__main__":
    sys.exit(main())
