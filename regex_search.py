from __future__ import annotations

import re
from bisect import bisect_right
from dataclasses import dataclass
from enum import Enum


class RegexSearchMode(str, Enum):
    AMEX_CARD = "amex_card"
    AMEX_CARD_AUTOMATON = "amex_card_automaton"


@dataclass(frozen=True)
class SearchMatch:
    value: str
    start: int
    length: int
    line: int
    column: int


class RegexSearchService:
    # Adapted from ^3[47]\d{2}[ -]?\d{6}[ -]?\d{5}$ for substring search in text.
    _AMEX_PATTERN = re.compile(r"3[47]\d{2}[ -]?\d{6}[ -]?\d{5}")

    def mode_items(self) -> list[tuple[RegexSearchMode, str]]:
        return [
            (RegexSearchMode.AMEX_CARD, "Amex Card (Regex)"),
            (RegexSearchMode.AMEX_CARD_AUTOMATON, "Amex Card (Automaton)"),
        ]

    def find(self, text: str, mode: RegexSearchMode) -> list[SearchMatch]:
        if mode == RegexSearchMode.AMEX_CARD:
            return self.find_amex_regex(text)
        if mode == RegexSearchMode.AMEX_CARD_AUTOMATON:
            return self.find_amex_automaton(text)
        return []

    def find_amex_regex(self, text: str) -> list[SearchMatch]:
        line_starts = _build_line_starts(text)
        matches: list[SearchMatch] = []
        for match in self._AMEX_PATTERN.finditer(text):
            if not _has_valid_right_boundary(text, match.end()):
                continue
            start = match.start()
            line, column = _offset_to_line_col(start, line_starts)
            matches.append(
                SearchMatch(
                    value=match.group(0),
                    start=start,
                    length=match.end() - match.start(),
                    line=line,
                    column=column,
                )
            )
        return matches

    def find_amex_automaton(self, text: str) -> list[SearchMatch]:
        line_starts = _build_line_starts(text)
        matches: list[SearchMatch] = []
        i = 0
        n = len(text)

        while i < n:
            if text[i] != "3":
                i += 1
                continue

            length = _consume_amex_from_index(text, i)
            if length == 0:
                i += 1
                continue

            line, column = _offset_to_line_col(i, line_starts)
            matches.append(
                SearchMatch(
                    value=text[i : i + length],
                    start=i,
                    length=length,
                    line=line,
                    column=column,
                )
            )
            i += length

        return matches


def _build_line_starts(text: str) -> list[int]:
    starts = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            starts.append(idx + 1)
    return starts


def _offset_to_line_col(offset: int, line_starts: list[int]) -> tuple[int, int]:
    line_index = bisect_right(line_starts, offset) - 1
    line_start = line_starts[line_index]
    return line_index + 1, (offset - line_start) + 1


def _consume_amex_from_index(text: str, start: int) -> int:
    n = len(text)
    i = start

    if i >= n or text[i] != "3":
        return 0
    i += 1

    if i >= n or text[i] not in {"4", "7"}:
        return 0
    i += 1

    for _ in range(2):
        if i >= n or not text[i].isdigit():
            return 0
        i += 1

    if i < n and text[i] in {" ", "-"}:
        i += 1

    for _ in range(6):
        if i >= n or not text[i].isdigit():
            return 0
        i += 1

    if i < n and text[i] in {" ", "-"}:
        i += 1

    for _ in range(5):
        if i >= n or not text[i].isdigit():
            return 0
        i += 1

    if not _has_valid_right_boundary(text, i):
        return 0

    return i - start


def _has_valid_right_boundary(text: str, end: int) -> bool:
    """Allow end-of-text, non-digit boundary, or immediate start of next Amex."""
    if end >= len(text):
        return True

    if not text[end].isdigit():
        return True

    return end + 1 < len(text) and text[end] == "3" and text[end + 1] in {"4", "7"}
