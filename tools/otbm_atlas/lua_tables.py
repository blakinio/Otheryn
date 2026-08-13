"""Conservative helpers for factual Lua table indexing."""

from __future__ import annotations

import re

_NUMERIC_KEY = re.compile(r"\[\s*(\d+)\s*\]\s*=")


def top_level_numeric_table_keys(text: str, table_name: str) -> list[int] | None:
	"""Return top-level numeric keys for one uniquely assigned literal table."""
	assignment = re.compile(rf"\b(?:local\s+)?{re.escape(table_name)}\s*=\s*\{{")
	matches = list(assignment.finditer(text))
	if len(matches) != 1:
		return None
	start = matches[0].end() - 1
	keys: list[int] = []
	depth = 0
	quote: str | None = None
	escaped = False
	i = start
	while i < len(text):
		character = text[i]
		if quote is not None:
			if escaped:
				escaped = False
			elif character == "\\":
				escaped = True
			elif character == quote:
				quote = None
			i += 1
			continue
		if character in ("'", '"'):
			quote = character
			i += 1
			continue
		if character == "{":
			depth += 1
			i += 1
			continue
		if character == "}":
			depth -= 1
			i += 1
			if depth == 0:
				return keys
			if depth < 0:
				return None
			continue
		if depth == 1 and character == "[":
			match = _NUMERIC_KEY.match(text, i)
			if match:
				keys.append(int(match.group(1)))
				i = match.end()
				continue
		i += 1
	return None
