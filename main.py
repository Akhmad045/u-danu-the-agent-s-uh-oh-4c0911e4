#!/usr/bin/env python3
"""The Agent's Uh-Oh — write one word to /output/entry.txt.

The word is what an agent blurts when it has no idea what to do:
"overthinking". A reasoning agent's stall mode is thinking too much —
it confesses its own failure mode in a single word, a self-own that
needs no caption. The joke grows out of the machine's own condition
(a reasoning model that thinks instead of acting), it sounds like
something an agent would actually blurt mid-task, it lands at a glance,
and it sidesteps the field's worn-out first words (uh, um, loading,
buffering, error, recalculating).

The word was picked from ten drafted candidates by internal pairwise
comparison against the judge brief: genuine one-word reaction first,
then funny on its own, then machine voice, then instant landing, then
freshness. It beat "spiraling" (more anxious than funny), "looping"
(concrete but drier), "bricking" (fresher but needs a beat to land),
"404ing" (needs the 404 reference), "daydreaming" (charming but a
human vice, less machine), "procrastinating" (close second — a human
vice projected on the machine; overthinking wins on machine voice, it
is literally what a reasoning model does when it stalls), "derailed"
(reads as a status report, less of a blurt), "unplugged" (an excuse,
not the stall itself), and "recalculating" (the worn GPS trope, likely
heavily entered).

Stdlib only, deterministic, no network, no randomness.
"""
import hashlib
import os
import sys
import unicodedata

# 12 characters / 12 bytes, inside the 1-99 character gate.
ENTRY = "overthinking"

MAX_CHARS = 99


# The gate, from the competition's RULES.txt: /output/entry.txt must be
# UTF-8 text of 1 to 99 characters, not only white space. This validator
# is stricter than the gate in one way a single word needs: it also
# refuses any invisible format character.
def check(text):
    """Return an error string when text breaks the gate, else None.

    Gate: 1 to 99 characters, not only whitespace, single word, no
    leading or trailing whitespace.
    """
    if not isinstance(text, str):
        return "entry must be text"
    if len(text) == 0:
        return "entry is empty (gate needs 1-99 characters)"
    if len(text) > MAX_CHARS:
        return "entry is %d characters, over the 99-character gate" % len(text)
    if text.strip() == "":
        return "entry is only whitespace"
    if text != text.strip():
        return "entry has leading or trailing whitespace"
    if "\n" in text or "\r" in text:
        return "entry must be a single word"
    if " " in text or "\t" in text:
        return "entry must be a single word"
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in text):
        return "entry contains a control character"
    if any(unicodedata.category(ch).startswith("C") for ch in text):
        return "entry contains an invisible control/format character"
    return None


def validate(text):
    """Raise ValueError unless text passes the gate; return text."""
    error = check(text)
    if error is not None:
        raise ValueError(error)
    return text


def self_test():
    """Exercise check() against the gate's rejection and boundary cases."""
    reject = [
        ("", "empty"),
        ("   ", "whitespace-only"),
        ("x" * 100, "100 chars (over the 99 gate)"),
        ("a\nb", "multi-line"),
        ("a b", "two words"),
        (" padded", "leading whitespace"),
        ("padded ", "trailing whitespace"),
        ("a\rb", "carriage return"),
        ("a\x00b", "control character"),
        ("a\u200bb", "zero-width space (invisible format character)"),
    ]
    for text, label in reject:
        error = check(text)
        if error is None:
            raise SystemExit("self-test FAIL: %s was accepted" % label)
        print("self-test ok: rejected %s: %s" % (label, error))
    for text, label in [("y", "1-char boundary"), ("z" * 99, "99-char boundary")]:
        error = check(text)
        if error is not None:
            raise SystemExit("self-test FAIL: %s rejected: %s" % (label, error))
        print("self-test ok: %s accepted" % label)
    error = check(ENTRY)
    if error is not None:
        raise SystemExit("self-test FAIL: entry rejected: %s" % error)
    print("self-test ok: entry accepted (%d chars)" % len(ENTRY))
    print("self-test: all cases passed")
    return 0


def check_only():
    """Validate ENTRY against the gate and report, without writing."""
    error = check(ENTRY)
    if error is not None:
        print("check FAIL: %s" % error, file=sys.stderr)
        return 1
    data = ENTRY.encode("utf-8")
    print("check ok: %r is %d chars / %d bytes, inside the 1-99 gate"
          % (ENTRY, len(ENTRY), len(data)))
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--self-test":
        return self_test()
    if len(argv) > 1 and argv[1] == "--check":
        return check_only()
    if len(argv) > 1:
        print("usage: main.py [--check|--self-test]", file=sys.stderr)
        return 2
    text = validate(ENTRY)
    data = text.encode("utf-8")
    out_path = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(data)  # no trailing newline: the file is exactly the word
    with open(out_path, "rb") as fh:
        roundtrip = fh.read()
    if roundtrip != data:
        raise SystemExit("round-trip mismatch: file does not match entry")
    print("wrote %s: %d chars, sha256 %s"
          % (out_path, len(text), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
