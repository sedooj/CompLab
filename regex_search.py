from __future__ import annotations

import re
from bisect import bisect_right
from dataclasses import dataclass
from enum import Enum


class RegexSearchMode(str, Enum):
    RUSSIAN_PASSPORT = "russian_passport"
    AMEX_CARD = "amex_card"
    ENGLISH_NAME = "english_name"


@dataclass(frozen=True)
class SearchMatch:
    value: str
    start: int
    length: int
    line: int
    column: int


class RegexSearchService:
    _PASSPORT_PATTERN = re.compile(r"\d{2}\s?\d{2}\s?\d{6}")
    _AMEX_PATTERN = re.compile(r"3[47]\d{2}[ -]?\d{6}[ -]?\d{5}")
    _ENGLISH_NAME_PATTERN = re.compile(
        r"[A-Z][a-z]+,\s[A-Z][a-z]+\s[A-Z][a-z]+"
    )

    def mode_items(self) -> list[tuple[RegexSearchMode, str]]:
        return [
            (RegexSearchMode.RUSSIAN_PASSPORT, "Russian passport"),
            (RegexSearchMode.AMEX_CARD, "Amex card"),
            (RegexSearchMode.ENGLISH_NAME, "English full name"),
        ]

    def find(self, text: str, mode: RegexSearchMode) -> list[SearchMatch]:
        if mode == RegexSearchMode.RUSSIAN_PASSPORT:
            return self.find_russian_passport(text)
        if mode == RegexSearchMode.AMEX_CARD:
            return self.find_amex_regex(text)
        if mode == RegexSearchMode.ENGLISH_NAME:
            return self.find_english_name(text)
        return []

    def find_russian_passport(self, text: str) -> list[SearchMatch]:
        return _collect_numeric_matches(text, self._PASSPORT_PATTERN)

    def find_amex_regex(self, text: str) -> list[SearchMatch]:
        return _collect_numeric_matches(text, self._AMEX_PATTERN)

    def find_english_name(self, text: str) -> list[SearchMatch]:
        line_starts = _build_line_starts(text)
        matches: list[SearchMatch] = []
        for match in self._ENGLISH_NAME_PATTERN.finditer(text):
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


def _collect_numeric_matches(
    text: str,
    pattern: re.Pattern[str],
) -> list[SearchMatch]:
    line_starts = _build_line_starts(text)
    matches: list[SearchMatch] = []
    previous_end = -1

    for match in pattern.finditer(text):
        start = match.start()
        end = match.end()

        if start > 0 and text[start - 1].isdigit() and start != previous_end:
            continue
        if not _has_valid_right_boundary(text, end, pattern):
            continue

        line, column = _offset_to_line_col(start, line_starts)
        matches.append(
            SearchMatch(
                value=match.group(0),
                start=start,
                length=end - start,
                line=line,
                column=column,
            )
        )
        previous_end = end

    return matches


def _has_valid_right_boundary(
    text: str,
    end: int,
    pattern: re.Pattern[str],
) -> bool:
    if end >= len(text):
        return True

    if not text[end].isdigit():
        return True

    return pattern.match(text, end) is not None
