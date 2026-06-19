#!/usr/bin/env python3
"""Pashto Arabic-script normalization utilities."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata


PASHTO_LETTERS = set(
    "اآأإبپتټثجچحخڅځدډذرړزژږسښشصضطظعغفقکګگكلمنڼوؤهۀءیيۍېےئئ"
)

PASHTO_SPECIFIC_LETTERS = set("پټډړږښڅځڼګۍې")

CHAR_MAP = {
    "ك": "ک",
    "ک": "ک",
    "گ": "ګ",
    "ݢ": "ګ",
    "ڬ": "ګ",
    "ي": "ی",
    "ى": "ی",
    "ی": "ی",
    "ے": "ې",
    "ۀ": "ه",
    "ة": "ه",
    "ؤ": "و",
    "أ": "ا",
    "إ": "ا",
    "ٱ": "ا",
    "ٲ": "ا",
    "ٳ": "ا",
    "ـ": "",
    "\u200c": " ",
    "\u200d": "",
    "\ufeff": "",
}

ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
KEEP_CHARS = re.compile(r"[^\u0600-\u06ff0-9\s،؛؟,.!?]")
WHITESPACE = re.compile(r"\s+")


def normalize_pashto(text: str, *, remove_punctuation: bool = False) -> str:
    """Normalize common Arabic/Persian-script variants in Pashto text."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(CHAR_MAP.get(ch, ch) for ch in text)
    text = ARABIC_DIACRITICS.sub("", text)
    text = KEEP_CHARS.sub(" ", text)
    if remove_punctuation:
        text = re.sub(r"[،؛؟,.!?]", " ", text)
    text = WHITESPACE.sub(" ", text).strip()
    return text


def pashto_character_ratio(text: str) -> float:
    chars = [ch for ch in normalize_pashto(text, remove_punctuation=True) if not ch.isspace()]
    if not chars:
        return 0.0
    valid = sum(1 for ch in chars if ch.isdigit() or ch in PASHTO_LETTERS)
    return valid / len(chars)


def pashto_specific_coverage(text: str) -> float:
    normalized = set(normalize_pashto(text))
    if not PASHTO_SPECIFIC_LETTERS:
        return 0.0
    return len(normalized & PASHTO_SPECIFIC_LETTERS) / len(PASHTO_SPECIFIC_LETTERS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Pashto text from stdin or arguments.")
    parser.add_argument("text", nargs="*", help="Text to normalize. Reads stdin when omitted.")
    parser.add_argument("--no-punctuation", action="store_true", help="Remove punctuation.")
    args = parser.parse_args()

    text = " ".join(args.text) if args.text else sys.stdin.read()
    print(normalize_pashto(text, remove_punctuation=args.no_punctuation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
