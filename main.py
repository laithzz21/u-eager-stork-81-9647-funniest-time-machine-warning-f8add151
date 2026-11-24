#!/usr/bin/env python3
"""Entry for make.fun bounty: the funniest time machine warning.

Prints the single-line warning label to stdout and also writes it to the
output directory (``/output/entry.txt`` by default, or ``$MAKEFUN_OUTPUT``
when set), verifying the written file by reading it back.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

ENTRY = (
    "WARNING: Do not meet yourself. He knows what you did, "
    "and he's already warned you about this."
)


def validate(text: str) -> None:
    """The entry must be a single line of 1-120 characters.

    It is a warning label, so it must start with "WARNING:" and carry no
    leading/trailing whitespace or doubled spaces.
    """
    if not 1 <= len(text) <= 120:
        raise ValueError(f"entry must be 1-120 characters, got {len(text)}")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    if "  " in text:
        raise ValueError("entry must not contain doubled spaces")
    if not text.startswith("WARNING:"):
        raise ValueError("entry must start with 'WARNING:'")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    print(ENTRY, flush=True)
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back: exact text and length.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY or len(written) != len(ENTRY):
            print(
                "error: verification failed: written entry does not match",
                file=sys.stderr,
            )
            return 1
    except OSError as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
