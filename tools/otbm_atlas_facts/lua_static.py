"""Conservative helpers for extracting literal facts from Lua source without executing it."""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterator

_LONG_OPEN = re.compile(r"\[(=*)\[")
_KEYWORD = re.compile(r"\b(function|if|elseif|for|while|do|repeat|until|end)\b")


def _long_region(text: str, start: int) -> int | None:
    match = _LONG_OPEN.match(text, start)
    if match is None:
        return None
    close = "]" + match.group(1) + "]"
    end = text.find(close, match.end())
    return None if end < 0 else end + len(close)


def strip_comments(text: str) -> str:
    """Remove Lua comments while preserving strings and line layout."""
    out: list[str] = []
    index = 0
    quote: str | None = None
    escape = False
    while index < len(text):
        char = text[index]
        if quote is not None:
            out.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            out.append(char)
            index += 1
            continue
        if text.startswith("--", index):
            long_end = _long_region(text, index + 2)
            if long_end is not None:
                out.extend("\n" for char in text[index:long_end] if char == "\n")
                index = long_end
                continue
            newline = text.find("\n", index + 2)
            if newline < 0:
                break
            out.append("\n")
            index = newline + 1
            continue
        long_end = _long_region(text, index)
        if long_end is not None:
            out.append(text[index:long_end])
            index = long_end
            continue
        out.append(char)
        index += 1
    return "".join(out)


def balanced_region(text: str, start: int, opener: str, closer: str) -> tuple[str | None, int | None]:
    if start >= len(text) or text[start] != opener:
        raise ValueError("balanced region must start on opener")
    depth = 0
    quote: str | None = None
    escape = False
    index = start
    while index < len(text):
        char = text[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        long_end = _long_region(text, index)
        if long_end is not None:
            index = long_end
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start + 1:index], index + 1
        index += 1
    return None, None


def split_arguments(text: str) -> list[str]:
    parts: list[str] = []
    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    quote: str | None = None
    escape = False
    start = 0
    index = 0
    while index < len(text):
        char = text[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        long_end = _long_region(text, index)
        if long_end is not None:
            index = long_end
            continue
        if char in "([{":
            stack.append(char)
        elif char in ")]}" and stack and stack[-1] == pairs[char]:
            stack.pop()
        elif char == "," and not stack:
            parts.append(text[start:index].strip())
            start = index + 1
        index += 1
    parts.append(text[start:].strip())
    return parts


def iter_calls(text: str, name: str) -> Iterator[tuple[int, list[str]]]:
    pattern = re.compile(rf"\b{re.escape(name)}\s*\(")
    cursor = 0
    while True:
        match = pattern.search(text, cursor)
        if match is None:
            return
        body, end = balanced_region(text, match.end() - 1, "(", ")")
        if body is None or end is None:
            return
        yield match.start(), split_arguments(body)
        cursor = end


def assigned_table(text: str, lhs: str) -> str | None:
    match = re.search(rf"{re.escape(lhs)}\s*=\s*\{{", text)
    if match is None:
        return None
    body, _end = balanced_region(text, match.end() - 1, "{", "}")
    return body


def named_tables(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    pattern = re.compile(r"\b(?:local\s+)?([A-Za-z_]\w*)\s*=\s*\{")
    cursor = 0
    while True:
        match = pattern.search(text, cursor)
        if match is None:
            return result
        body, end = balanced_region(text, match.end() - 1, "{", "}")
        if body is None or end is None:
            return result
        result.setdefault(match.group(1), body)
        cursor = end


def numeric_table_entries(body: str) -> dict[int, str]:
    matches: list[tuple[int, int, int]] = []
    depth = 0
    quote: str | None = None
    escape = False
    index = 0
    while index < len(body):
        char = body[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        long_end = _long_region(body, index)
        if long_end is not None:
            index = long_end
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == "[" and depth == 0:
            match = re.match(r"\[\s*(\d+)\s*\]\s*=\s*", body[index:])
            if match is not None:
                matches.append((int(match.group(1)), index, index + match.end()))
                index += match.end()
                continue
        index += 1
    result: dict[int, str] = {}
    for ordinal, (key, _key_start, value_start) in enumerate(matches):
        value_end = matches[ordinal + 1][1] if ordinal + 1 < len(matches) else len(body)
        result[key] = body[value_start:value_end].rstrip(" \t\r\n,")
    return result


def top_level_table_rows(body: str) -> list[str]:
    rows: list[str] = []
    quote: str | None = None
    escape = False
    index = 0
    while index < len(body):
        char = body[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        long_end = _long_region(body, index)
        if long_end is not None:
            index = long_end
            continue
        if char == "{":
            row, end = balanced_region(body, index, "{", "}")
            if row is None or end is None:
                return rows
            rows.append(row)
            index = end
            continue
        index += 1
    return rows


@dataclass(frozen=True)
class FunctionRegion:
    start: int
    body_start: int
    body_end: int
    end: int


def _keyword_tokens(text: str) -> Iterator[re.Match[str]]:
    quote: str | None = None
    escape = False
    index = 0
    while index < len(text):
        char = text[index]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in ("'", '"'):
            quote = char
            index += 1
            continue
        long_end = _long_region(text, index)
        if long_end is not None:
            index = long_end
            continue
        match = _KEYWORD.match(text, index)
        if match is not None:
            yield match
            index = match.end()
            continue
        index += 1


def function_regions(text: str) -> list[FunctionRegion]:
    stack: list[tuple[str, int | None, int | None]] = []
    functions: list[FunctionRegion] = []
    pending_do = 0
    for token in _keyword_tokens(text):
        keyword = token.group(1)
        if keyword == "function":
            paren = text.find("(", token.end())
            body_start = None
            if paren >= 0:
                _args, body_start = balanced_region(text, paren, "(", ")")
            stack.append(("end", token.start(), body_start if isinstance(body_start, int) else None))
        elif keyword == "if":
            stack.append(("end", None, None))
        elif keyword in ("for", "while"):
            stack.append(("end", None, None))
            pending_do += 1
        elif keyword == "do":
            if pending_do:
                pending_do -= 1
            else:
                stack.append(("end", None, None))
        elif keyword == "repeat":
            stack.append(("until", None, None))
        elif keyword == "end":
            if not stack or stack[-1][0] != "end":
                continue
            _terminator, function_start, body_start = stack.pop()
            if function_start is not None and body_start is not None:
                functions.append(FunctionRegion(function_start, body_start, token.start(), token.end()))
        elif keyword == "until" and stack and stack[-1][0] == "until":
            stack.pop()
    return sorted(functions, key=lambda region: region.start)


def containing_function(text: str, offset: int) -> FunctionRegion | None:
    candidates = [region for region in function_regions(text) if region.body_start <= offset <= region.body_end]
    return min(candidates, key=lambda region: region.body_end - region.body_start) if candidates else None


def literal_string(value: str) -> str | None:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return None


def literal_int(value: str) -> int | None:
    value = value.strip()
    return int(value) if re.fullmatch(r"-?\d+", value) else None


def literal_number(value: str) -> int | float | None:
    value = value.strip()
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return None


def literal_position(value: str) -> dict[str, int] | None:
    match = re.fullmatch(r"\s*Position\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*", value)
    if match is None:
        return None
    x, y, z = map(int, match.groups())
    return {"x": x, "y": y, "z": z}
