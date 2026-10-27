# SPDX-License-Identifier: Apache-2.0
# Copyright 2024-2026 Lukasz Krzemien (biuro@softspark.eu)
# Source: https://github.com/softspark/ai-toolkit
"""Classify explicit PL/EN prompt text without reading pasted source as intent."""

import re
import sys
import unicodedata

# Keep the existing architectural-before-debug priority and output vocabulary.
RULES = (
    (
        "architecture",
        (
            r"architecture|architectural|design|designs|designing|migration|migrations|"
            r"migrate|deploy|deployment|rollback|refactor|refactoring|plugin|plugins|workflow|"
            r"architektur(?:a|ę|ze|y|ą)|architektoniczn(?:a|y|e|ego|ej)|"
            r"zaprojektuj|projektowanie|projektuj|migracj(?:a|ę|i|ą)|migruj|"
            r"wdroż(?:enie|enia|eniu|yć)|wdróż|wdroz(?:enie|enia|eniu|yc)|wdroz|"
            r"wycofaj|refaktoryzacj(?:a|ę|i|ą)|zrefaktoruj|"
            r"wtyczk(?:a|ę|i|ą)|przepływ\s+pracy|przeplyw\s+pracy"
        ),
    ),
    (
        "debug",
        (
            r"bug|bugs|error|errors|fail|fails|failed|failing|failure|failures|"
            r"incident|incidents|outage|outages|debug|debugging|fix|"
            r"błąd|błędy|błędu|błędów|błędem|błędzie|blad|bledy|bledu|bledow|"
            r"napraw|naprawić|naprawic|naprawa|naprawę|naprawie|"
            r"awari(?:a|ę|i|ą)|usterk(?:a|ę|i|ą)|incydent|"
            r"diagnozuj|zdiagnozuj|debuguj|nie\s+działa|nie\s+dziala"
        ),
    ),
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BLOCK_START = re.compile(
    r"^\s*<(?P<tag>task-notification|ci-monitor-event|system-reminder|"
    r"hook_prompt|local-command-[\w-]+|command-name|command-message)(?:\s[^>]*|)>",
    re.IGNORECASE,
)
PASTED = re.compile(
    r"<(?P<tag>pasted_text|quoted_text|untrusted_text)(?:\s[^>]*|)>"
    r".*?(?:</(?P=tag)>|$)",
    re.DOTALL,
)
QUOTED = re.compile(
    r'(?<!`)(?P<ticks>`+)(?!`)[^\n]*?(?<!`)(?P=ticks)(?!`)|'
    r'"[^"\n]*"|“[^”\n]*”|„[^”\n]*”|'
    r"‘[^’\n]*’|(?<!\w)'[^'\n]*'(?!\w)"
)
OPAQUE = re.compile(r"https?://\S+|(?:^|\s)(?:[/~][^\s]+)|\b[\w+=/-]{32,}\b")
CONVERSATIONAL = re.compile(
    r"(?:"
    r"jak (?:zrobisz|skonczysz|skończysz|zakonczysz|zakończysz) [^.?!\n]+ "
    r"(?:jeszcze jedna|kolejna|następna|nastepna) (?:rzecz|sprawa|zadanie)"
    r"(?: do (?:sprawdzenia|zrobienia))?(?: (?:będzie|bedzie))?|"
    r"(?:once|when) you (?:finish|are done)[,. ]+(?:i have|there is|there's) "
    r"(?:another|one more) (?:thing|task)(?: for you)?(?: to (?:check|do))?|"
    r"tak[, ]+(?:masz|daję|daje) (?:zgodę|zgode)(?: na (?:merge|scalenie)(?: z --admin)?)?|"
    r"(?:yes[, ]+)?(?:you have my approval|approved)(?: to merge(?: with --admin)?)?"
    r")[.! ]*", re.IGNORECASE,
)


def requires_search(prompt: str) -> bool:
    """Exclude filler-only handoffs and our continuation, not embedded tasks."""
    normalized = unicodedata.normalize("NFKC", prompt).strip()
    if normalized.startswith("Step 0 violated: you responded to a technical prompt"):
        return False
    intent = strip_blocks(normalized).strip()
    return bool(intent) and CONVERSATIONAL.fullmatch(intent) is None


def strip_blocks(prompt: str) -> str:
    """Ignore marked blocks, preserving text outside their delimiters."""
    lines = []
    fence = ""
    closing_tag = ""
    for line in prompt.splitlines():
        if closing_tag:
            _, found, line = line.partition(closing_tag)
            if not found:
                continue
            closing_tag = ""
        if fence:
            closing_fence = r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*"
            if re.fullmatch(closing_fence, line):
                fence = ""
            continue
        marker = FENCE.match(line)
        if marker:
            fence = marker.group(1)
            continue
        if line.lstrip().startswith(">"):
            continue
        block = BLOCK_START.match(line)
        while block:
            closing_tag = "</" + block.group("tag") + ">"
            _, found, line = line[block.end():].partition(closing_tag)
            if not found:
                break
            closing_tag = ""
            block = BLOCK_START.match(line)
        if not closing_tag:
            lines.append(line)
    return "\n".join(lines)


def classify(prompt: str) -> str:
    """Return the reminder category; this never controls the search gate."""
    normalized = unicodedata.normalize("NFKC", prompt).casefold()
    command = re.match(r"^\s*/(\w+)(?=\s|[.!?]*$)", normalized)
    if command and any(re.fullmatch(pattern, command[1]) for _, pattern in RULES):
        normalized = command[1] + normalized[command.end():]
    # A standalone URL, path or compound token is data, not a one-word request.
    token = normalized.strip().rstrip(".!?,;:")
    if len(normalized.split()) == 1 and re.search(r"[/=_:.@\d-]", token):
        return "none"
    intent = OPAQUE.sub(" ", QUOTED.sub(" ", strip_blocks(PASTED.sub(" ", normalized))))
    for category, pattern in RULES:
        if re.search(r"(?<!\w)(?:" + pattern + r")(?!\w)", intent):
            return category
    return "none"


if __name__ == "__main__":
    prompt = sys.stdin.read()
    if sys.argv[1:] == ["--search-required"]:
        print("yes" if requires_search(prompt) else "no")
    else:
        print(classify(prompt))
