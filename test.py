#!/usr/bin/env python3

import subprocess
import tempfile
import os
import sys
import argparse
from dataclasses import dataclass
from typing import Callable, List, Tuple

MDDIFF = "./mddiff"


# ----------------------------
# Test structures
# ----------------------------

@dataclass
class TestCase:
    name: str
    a: str
    b: str
    args: List[str]
    check: Callable[[str], Tuple[bool, str]]


# ----------------------------
# Utility helpers
# ----------------------------

def run_mddiff(args, a_text, b_text):
    with tempfile.NamedTemporaryFile("w", delete=False) as fa:
        fa.write(a_text)
        a_path = fa.name

    with tempfile.NamedTemporaryFile("w", delete=False) as fb:
        fb.write(b_text)
        b_path = fb.name

    try:
        cmd = [MDDIFF] + args + [a_path, b_path]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout
    finally:
        os.unlink(a_path)
        os.unlink(b_path)


def parse_summary(output):
    """
    Returns [unchanged, modified, added, deleted]
    """
    result = [0, 0, 0, 0]
    mapping = {
        "unchanged": 0,
        "modified": 1,
        "added": 2,
        "deleted": 3,
    }

    for line in output.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            if k in mapping:
                try:
                    result[mapping[k]] = int(v.strip())
                except ValueError:
                    pass

    return result


# ----------------------------
# Check helpers
# ----------------------------

def check_summary(expected):
    """
    expected = [unchanged, modified, added, deleted]
    """
    def _check(output):
        summary = parse_summary(output)
        if summary == expected:
            return True, ""
        return False, f"expected {expected}, got {summary}"
    return _check


def check_contains(text):
    def _check(output):
        if text in output:
            return True, ""
        return False, f"expected to find '{text}' in '{output}'"
    return _check


# ----------------------------
# Test definitions
# ----------------------------

TESTS: List[TestCase] = [

    TestCase(
        name="identical_shortstat",
        a="# A\nhello\n",
        b="# A\nhello\n",
        args=["--shortstat"],
        check=check_summary([1,0,0,0])
    ),

    TestCase(
        name="added_block",
        a="# A\nhello\n",
        b="# A\nhello\n\n# B\nworld\n",
        args=["--shortstat"],
        check=check_summary([1,0,1,0])
    ),

    TestCase(
        name="deleted_block",
        a="# A\nhello\n\n# B\nworld\n",
        b="# A\nhello\n",
        args=["--shortstat"],
        check=check_summary([1,0,0,1])
    ),

    TestCase(
        name="modified_block",
        a="# A\nhello\n",
        b="# A\nhello there\n",
        args=["--shortstat"],
        check=check_summary([0,1,0,0])
    ),

    TestCase(
        name="case_sensitive_difference",
        a="# A\nHello\n",
        b="# A\nhello\n",
        args=["--shortstat"],
        check=check_summary([0,1,0,0])
    ),

    TestCase(
        name="ignore_case",
        a="# A\nHello\n",
        b="# A\nhello\n",
        args=["-i", "--shortstat"],
        check=check_summary([1,0,0,0])
    ),

    TestCase(
        name="multiple_changes",
        a="# A\none\n\n# B\ntwo\n",
        b="# A\none changed\n\n# C\nthree\n",
        args=["--shortstat"],
        check=check_summary([0,1,1,1])
    ),

    TestCase(
        name="word_diff_output",
        a="# A\nquick brown fox\n",
        b="# A\nquick red fox\n",
        args=[],
        check=check_contains("quick")
    ),

    TestCase(
        name="context_mode",
        a="# A\n1\n\n# B\n2\n\n# C\n3\n",
        b="# A\n1\n\n# B\nchanged\n\n# C\n3\n",
        args=["-c"],
        check=check_contains("changed")
    ),

    TestCase(
        name="context_collapse",
        a="# A\n1\n\n# B\n2\n\n# C\n3\n\n# D\n4\n",
        b="# A\n1\n\n# B\nchanged\n\n# C\n3\n\n# D\n4\n",
        args=["-C","1"],
        check=check_contains("...")
    ),

    TestCase(
        name="match_threshold",
        a="# A\nalpha beta gamma\n",
        b="# A\nalpha beta delta\n",
        args=["--match-threshold","20","--shortstat"],
        check=check_contains("modified")
    ),

    TestCase(
        name="report_identical",
        a="# A\nhello\n",
        b="# A\nhello\n",
        args=["-s"],
        check=check_contains("Files are identical")
    ),

]


# ----------------------------
# Test runner
# ----------------------------

def run_test(test: TestCase):
    output = run_mddiff(test.args, test.a, test.b)
    ok, msg = test.check(output)
    return ok, msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    failures = 0

    for test in TESTS:
        ok, msg = run_test(test)

        if not args.quiet:
            if ok:
                print(f"PASS {test.name}")
            else:
                print(f"FAIL {test.name}: {msg}")

        if not ok:
            failures += 1

    if not args.quiet:
        print(f"\n{len(TESTS) - failures}/{len(TESTS)} tests passed")

    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
