import re


class BoilerplateStripper:
    """Removes standard disclaimers and trailing non-narrative boilerplate."""

    def strip_boilerplate(self, text: str) -> str:
        """Applies all boilerplate removal transformations."""
        text = self._remove_disclaimers(text)
        text = self._remove_trailing_notes(text)
        return text.strip()

    def _remove_disclaimers(self, text: str) -> str:
        # Common USENET/legal disclaimers
        disclaimer_patterns = [
            r'(?i)^\s*(?:disclaimer|note|copyright):\s*all\s+characters\s+are\s+fictional.*$',
            r'(?i)^\s*this\s+is\s+a\s+work\s+of\s+fiction\..*$',
            r'(?i)^\s*no\s+animals\s+were\s+harmed\s+in\s+the\s+making\s+of\s+this\s+story.*$',
            r'(?i)^\s*copyright\s+\d{4}\..*$',
            r'(?i)^\s*posted\s+to\s+asstr.*$',
        ]

        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if not any(re.match(pattern, line.strip()) for pattern in disclaimer_patterns):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _remove_trailing_notes(self, text: str) -> str:
        lines = text.split('\n')

        trailing_patterns = [
            r'(?i)^\s*(?:feedback|comments|criticism)\s+(?:welcome|appreciated).*$',
            r'(?i)^\s*more\s+stories\s+(?:by\s+this\s+author\s+)?(?:can\s+be\s+found\s+)?at.*$',
            r'(?i)^\s*please\s+(?:rate|review|comment)\s+on\s+this\s+story.*$',
            r'(?i)^\s*thanks\s+for\s+reading!?\s*$',
            r'(?i)^\s*the\s+end\.?\s*$',
            r'(?i)^\s*fini\.?\s*$',
            r'(?i)^\s*any\s+comments?\s*\?.*$',
            r'(?i)^\s*email\s+me\s+at:\s*.*$',
            r'(?i)^\s*comments?\s+to:\s*.*$',
        ]

        cutoff_index = len(lines)
        # Look backwards through the text to find contiguous trailing boilerplate
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if not stripped:
                continue
            if any(re.match(pattern, stripped) for pattern in trailing_patterns):
                cutoff_index = i
            else:
                # Once we hit a line that doesn't match boilerplate, stop looking backward
                break

        # If we found boilerplate, and we are not stripping the entire text
        if cutoff_index < len(lines) and cutoff_index > 0:
            return '\n'.join(lines[:cutoff_index]).strip()

        return text
