import re


class TextCleaner:
    """Applies advanced heuristic refinements to narrative prose."""

    def clean_prose(self, text: str, format_type: str) -> str:
        """Main entry point for prose cleaning."""
        if format_type == "html":
            # HTML is already mostly structured; we only do light cleanup
            text = self._normalize_whitespace(text)
            text = self._repair_smart_quotes(text)
            text = self._normalize_punctuation(text)
            return text.strip()

        # For plaintext, apply the full refinement pipeline
        text = self._normalize_whitespace(text)
        text = self._normalize_scene_breaks(text)
        text = self._normalize_chapters(text)
        text = self._repair_hyphenation(text)
        text = self._unwrap_lines(text)
        text = self._repair_smart_quotes(text)
        text = self._normalize_punctuation(text)

        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        # Replace tabs with spaces
        text = text.replace('\t', '    ')
        # Collapse more than 2 consecutive newlines into exactly 2 (standard paragraph break)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove trailing spaces on individual lines
        lines = [line.rstrip() for line in text.split('\n')]
        return '\n'.join(lines)

    def _normalize_scene_breaks(self, text: str) -> str:
        # Detect common scene break patterns and standardize them to \n\n---\n\n
        # Matches: ***, * * *, ---, ===, ~~~, or standalone asterisks
        pattern = r'^\s*([\*\-\=\~]\s*){3,}\s*$'
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            if re.match(pattern, line.strip()):
                cleaned_lines.append('\n---\n')
            else:
                cleaned_lines.append(line)

        # Clean up any resulting triple-newlines from the replacement
        return re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned_lines))

    def _normalize_chapters(self, text: str) -> str:
        # Detect chapter/part headings and ensure they are isolated with proper spacing
        # Matches: "Chapter 1", "Part II", "Episode 3", etc.
        pattern = r'^(?:chapter|part|episode|section)\s+(?:[IVXLCDMivxlcdm]+|\d+|[A-Za-z]+).*$'
        lines = text.split('\n')
        cleaned_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if re.match(pattern, stripped, re.IGNORECASE):
                # Ensure blank lines before and after
                if cleaned_lines and cleaned_lines[-1] != '':
                    cleaned_lines.append('')
                cleaned_lines.append(stripped)
                cleaned_lines.append('')
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _repair_hyphenation(self, text: str) -> str:
        # Join words split across lines with a hyphen (e.g., "beau-\ntiful" -> "beautiful")
        # We only do this if the part after the newline starts with a lowercase letter
        # to avoid joining intentional hyphenated compounds at the start of a new line.
        return re.sub(r'(\w+)-\s*\n\s*([a-z]\w*)', r'\1\2', text)

    def _unwrap_lines(self, text: str) -> str:
        # Split into paragraphs first (preserving intentional double-newlines)
        paragraphs = re.split(r'(\n\n+)', text)
        cleaned_paragraphs = []

        for block in paragraphs:
            if re.match(r'^\n+$', block):
                # It's just whitespace, keep it as a single \n\n
                cleaned_paragraphs.append('\n\n')
                continue

            lines = block.split('\n')
            unwrapped_lines = []
            current_line = ""

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if not current_line:
                    current_line = stripped
                    continue

                # Heuristic: Should we merge this line with the previous one?
                # Merge if:
                # 1. Previous line does NOT end with terminal punctuation (. ! ? " ')
                # 2. Current line does NOT look like a structural element (e.g., all caps heading)
                prev_ends_with_punct = re.search(r'[.!?"\']\s*$', current_line)
                current_is_heading = stripped.isupper() and len(stripped) < 50

                if not prev_ends_with_punct and not current_is_heading:
                    # Merge with a space
                    current_line = f"{current_line} {stripped}"
                else:
                    # Keep separate (new paragraph or intentional line break)
                    unwrapped_lines.append(current_line)
                    current_line = stripped

            if current_line:
                unwrapped_lines.append(current_line)

            cleaned_paragraphs.append('\n'.join(unwrapped_lines))

        return ''.join(cleaned_paragraphs)

    def _repair_smart_quotes(self, text: str) -> str:
        # FIX: Legacy DOS issue where smart quotes were replaced by '?'
        # e.g., "wasn?t" -> "wasn’t", "I?ve" -> "I’ve"
        return re.sub(r'([a-zA-Z])\?([a-zA-Z])', r'\1’\2', text)

    def _normalize_punctuation(self, text: str) -> str:
        # Fix spaced ellipses (e.g., ". . ." or ". . .") -> "..."
        text = re.sub(r'\.\s*\.\s*\.', '...', text)
        # Fix spaced em-dashes (e.g., "word - - word") -> "word -- word" or "word—word"
        text = re.sub(r'\s+-\s+-\s+', ' -- ', text)
        # Remove spaces before commas and periods
        text = re.sub(r'\s+([,.])', r'\1', text)
        return text
