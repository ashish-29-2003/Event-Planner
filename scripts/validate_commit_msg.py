#!/usr/bin/env python3
"""
Commit message validator enforcing Conventional Commits format for Samaroh.
Usage: python scripts/validate_commit_msg.py <commit_msg_file>
"""

import re
import sys


def validate_commit_msg(filepath: str) -> bool:
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = [line.strip() for line in f if not line.startswith("#")]
    except Exception as e:
        print(f"ERROR: Unable to read commit message file: {e}")
        return False

    if not lines or not lines[0]:
        print("ERROR: Empty commit message.")
        return False

    first_line = lines[0]

    pattern = (
        r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|security|a11y)"
        r"\((api|ai|auth|db|ui|budget|timeline|vendors|ideas|guests|muhurat|export|i18n|a11y|security|tests|ci|docs|deploy|deps|status|release)\): "
        r".{1,72}$"
    )

    if not re.match(pattern, first_line):
        print("ERROR: Commit message does not match Conventional Commits format:")
        print("Format: <type>(<scope>): <imperative summary, max 72 chars, no trailing period>")
        print("Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, security, a11y")
        print("Allowed scopes: api, ai, auth, db, ui, budget, timeline, vendors, ideas, guests, muhurat, export, i18n, a11y, security, tests, ci, docs, deploy, deps, status, release")
        print(f"Received: '{first_line}'")
        return False

    if first_line.endswith("."):
        print("ERROR: Commit message first line must not end with a trailing period.")
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_commit_msg.py <commit_msg_file>")
        sys.exit(1)

    if not validate_commit_msg(sys.argv[1]):
        sys.exit(1)
    sys.exit(0)
