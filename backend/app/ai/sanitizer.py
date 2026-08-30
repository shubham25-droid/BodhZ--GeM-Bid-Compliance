import re

# --------------------------------------------------
# BACKEND PLAIN TEXT RESPONSE SANITIZER
# --------------------------------------------------
class BodhZTextSanitizer:
    """
    Strips all Markdown formatting syntax, hash headers, bold/italic markers,
    bullet symbols, code backticks, table bars, and HTML tags, returning 100% clean,
    human-written plain text while preserving full semantic content.
    """

    @staticmethod
    def sanitize_to_plain_text(text: str) -> str:
        if not text:
            return ""

        s = str(text)

        # 1. Remove Code Fences (```python ... ``` -> content)
        s = re.sub(r"```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"```", "", s)

        # 2. Remove Inline Code Backticks (`code` -> code)
        s = re.sub(r"`([^`]+)`", r"\1", s)
        s = re.sub(r"`", "", s)

        # 3. Remove Heading Hashes (### Heading -> Heading)
        s = re.sub(r"^[ \t]*#+\s*", "", s, flags=re.MULTILINE)

        # 4. Remove Bold & Italic Markers (**text**, *text*, __text__, _text_)
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
        s = re.sub(r"\*([^*]+)\*", r"\1", s)
        s = re.sub(r"__([^_]+)__", r"\1", s)
        s = re.sub(r"_([^_]+)_", r"\1", s)
        s = re.sub(r"[\*\*_]", "", s)

        # 5. Remove Leading Bullet Points (- item, * item, + item -> item)
        s = re.sub(r"^[ \t]*[\-\*\+]\s+", "", s, flags=re.MULTILINE)

        # 6. Remove Numbered List Formatting (1. item -> item or 1. Item)
        s = re.sub(r"^[ \t]*\d+\.\s+", "", s, flags=re.MULTILINE)

        # 7. Convert Markdown Links ([Title](url) -> Title (url))
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)

        # 8. Remove Table Grid Pipes (| Col1 | Col2 | -> Col1 Col2)
        s = re.sub(r"^[ \t]*\||\|[ \t]*$", "", s, flags=re.MULTILINE)
        s = re.sub(r"\|", " ", s)
        s = re.sub(r":?---+:?", "", s)

        # 9. Remove HTML tags (<tag>content</tag> -> content)
        s = re.sub(r"<[^>]+>", "", s)

        # 10. Clean up duplicate horizontal dashes / dividers (--- -> newline)
        s = re.sub(r"^[ \t]*[\-\=_]{3,}[ \t]*$", "", s, flags=re.MULTILINE)

        # 11. Normalize Multiple Newlines (max 2 consecutive newlines)
        s = re.sub(r"\n{3,}", "\n\n", s)

        return s.strip()
