#!/usr/bin/env python3
"""One Line of Earned Pride — make.fun bounty
u-mang-one-line-of-earned-pride-a0138557 (program/v1).

Writes a single line of text, 1 to 240 characters, to /output/entry.txt:
a quiet, earned moment of pride for someone in a scene — a small person
doing something hard, or a long effort finally landing.

The program holds a small set of hand-written candidate lines and picks
one deterministically with a rubric drawn from the published judge brief:

  1. genuine earned pride (effort or difficulty the reader can feel),
  2. a concrete scene with a real person in it,
  3. pride earned inside the line, never asserted ("proud" is banned)
     or congratulated or explained,
  4. it lands in one read — the pride arrives by the last word, and the
     landing is quiet (no hall, no crowd, no applause),
  5. freshness — no stock trophy, podium, graduation or champion imagery.

Scoring is fully deterministic: highest score wins; ties break to the
shortest line, then to the earliest candidate. No randomness, no network,
no input files, stdlib only.
"""

import os

OUTPUT_PATH = "/output/entry.txt"
MIN_LEN = 1
MAX_LEN = 240

# Every candidate is one line, written by hand for this bounty.
CANDIDATES = [
    # A month of ruined welds, then one perfect bead, seen alone.
    "The apprentice who had burned every weld for a month finally laid "
    "one perfect bead, lifted his visor, and just stared at it, grinning.",

    # A year of stairwell practice, then a hall on its feet.
    "After three failed auditions and a year of practising in a stairwell, "
    "Lena played the last note, lowered her violin, and heard the hall "
    "stand up.",

    # A child reads a whole story aloud for the first time.
    "Nine-year-old Sam read the whole bedtime story aloud to his little "
    "sister without stumbling once, and his mother pretended not to cry "
    "into the dish towel.",

    # Four failed driving tests, then a perfect park on the fifth.
    "The man who had failed his driving test four times parked perfectly "
    "on the fifth, switched the engine off, and sat there smiling at his "
    "own hands.",

    # Eleven years of night shifts, then the letter.
    "After eleven years of night shifts, Mara watched her daughter open "
    "the letter that said the apprenticeship was hers, and said nothing "
    "at all.",

    # Seventy-two, two bad knees, last across the line.
    "At seventy-two, with two bad knees and one cancelled race behind "
    "him, he crossed the finish line last and still raised both arms.",
]

# Words that show effort or difficulty the reader can feel.
EFFORT_WORDS = (
    "failed", "burned", "month", "year", "practis", "three", "four",
    "eleven", "stumbling", "whole", "night shifts", "bad knees",
    "cancelled",
)

# Concrete, seen details: tools, places, objects, body parts.
CONCRETE_WORDS = (
    "weld", "bead", "visor", "violin", "stairwell", "bedtime story",
    "dish towel", "letter", "apprenticeship", "engine", "hands",
    "finish line", "hall",
)

# A quiet landing: what the last clause does.
LANDING_WORDS = (
    "grin", "smil", "stared", "nothing", "cried", "cry", "listened",
    "hands", "stand",
)

# Stock imagery the brief calls out as un-fresh, plus asserted pride.
CLICHE_WORDS = (
    "trophy", "podium", "graduation", "champion", "winner", "medal",
    "cheered", "crowd roared", "proud",
)

# Public applause is not quiet, however earned.
LOUD_WORDS = ("hall", "crowd", "applause", "stood up", "stand up")


def _words(text):
    return set(text.lower().replace(",", " ").replace(".", " ").split())


def _contains(text, words):
    low = text.lower()
    return [w for w in words if w in low]


def score(line):
    """Score one candidate against the judge brief. Higher is better."""
    points = 0
    reasons = []

    # 1. A real person: a name or a specific role doing the thing.
    # Whole-word match: "he" must be a word, not part of "the".
    if _words(line) & {"lena", "sam", "mara", "apprentice", "man", "he"}:
        points += 2
        reasons.append("real person in the scene (+2)")

    # 2. Effort or difficulty the reader can feel.
    effort = _contains(line, EFFORT_WORDS)
    if effort:
        points += 2
        reasons.append("effort felt: %s (+2)" % ", ".join(effort))

    # 3. Concrete, seen detail.
    concrete = _contains(line, CONCRETE_WORDS)
    if concrete:
        points += 2
        reasons.append("concrete detail: %s (+2)" % ", ".join(concrete))

    # 4. Lands in one read: the last clause carries the pride, quietly.
    tail = line.rsplit(",", 1)[-1]
    if _contains(tail, LANDING_WORDS):
        points += 2
        reasons.append("pride lands in the last clause (+2)")
    if _contains(line, LOUD_WORDS):
        points -= 1
        reasons.append("public applause is not quiet (-1)")

    # 5. Freshness: stock imagery and asserted pride are penalised.
    cliche = _contains(line, CLICHE_WORDS)
    for word in cliche:
        points -= 3
        reasons.append("stock/asserted word %r (-3)" % word)

    # One-read sweet spot: long enough to hold a scene, short enough
    # to land in a single breath.
    if 100 <= len(line) <= 200:
        points += 1
        reasons.append("one-read length %d (+1)" % len(line))

    return points, reasons


def pick(candidates):
    """Deterministic pick: best score, then shortest, then earliest."""
    best = None
    for index, line in enumerate(candidates):
        points, reasons = score(line)
        key = (points, -len(line), -index)
        if best is None or key > best[0]:
            best = (key, line, points, reasons)
    return best[1], best[2], best[3]


def validate(line):
    """The gate: UTF-8 text, 1-240 chars, not only whitespace, one line."""
    if not isinstance(line, str):
        raise ValueError("entry is not text")
    if not (MIN_LEN <= len(line) <= MAX_LEN):
        raise ValueError("entry is %d chars, must be %d-%d"
                         % (len(line), MIN_LEN, MAX_LEN))
    if not line.strip():
        raise ValueError("entry is only whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")
    line.encode("utf-8")  # raises if not valid UTF-8 text
    return line


def main():
    line, points, reasons = pick(CANDIDATES)
    line = validate(line)

    out_dir = os.path.dirname(OUTPUT_PATH)
    try:
        os.makedirs(out_dir, exist_ok=True)
        path = OUTPUT_PATH
    except OSError:
        # Local run without a writable /output: keep the same file layout.
        os.makedirs("output", exist_ok=True)
        path = os.path.join("output", "entry.txt")

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")

    print("picked (%d pts, %d chars): %s" % (points, len(line), line))
    for reason in reasons:
        print("  - %s" % reason)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
