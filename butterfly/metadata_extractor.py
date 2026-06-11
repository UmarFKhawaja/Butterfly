import re
from typing import Tuple

from butterfly.story_metadata import StoryMetadata


class MetadataExtractor:
    """Extracts and normalizes metadata from story headers, separating it from the body."""

    def __init__(self):
        # Allow optional leading whitespace (\s*) for all patterns
        self.patterns = {
            "title": re.compile(r'^\s*(?:title|story title)\s*:\s*(.+)$', re.IGNORECASE),
            "author": re.compile(r'^\s*(?:author|by|written by)[:\s]+(.+)$', re.IGNORECASE),
            "date": re.compile(r'^\s*(?:date|posted|published)\s*:\s*(.+)$', re.IGNORECASE),
            "warnings": re.compile(r'^\s*(?:warnings?|content warnings?)\s*:\s*(.+)$', re.IGNORECASE),
            "tags": re.compile(r'^\s*(?:tags?|keywords?|categories?)\s*:\s*(.+)$', re.IGNORECASE),
            "synopsis": re.compile(r'^\s*(?:synopsis|summary|description)\s*:\s*(.+)$', re.IGNORECASE),
            "archive_name": re.compile(r'^\s*(?:archive|archive name|source)\s*:\s*(.+)$', re.IGNORECASE),
            "story_code": re.compile(r'^\s*(?:story code|code|id)\s*:\s*(.+)$', re.IGNORECASE),
        }

    def extract(self, text: str) -> Tuple[StoryMetadata, str]:
        """
        Parses the header and returns (metadata, body_text).
        """
        metadata = StoryMetadata()
        lines = text.split('\n')

        current_key = None
        last_metadata_line = -1
        # Scan up to 30 lines to find all header metadata
        scan_limit = min(30, len(lines))

        for i in range(scan_limit):
            original_line = lines[i]
            stripped = original_line.strip()

            # Blank line often signifies the end of a multi-line value or the header block
            if not stripped:
                if current_key is not None:
                    current_key = None
                continue

            # Check if this line starts a new metadata field
            matched_key = None
            for key, pattern in self.patterns.items():
                # Match against the original line to preserve whitespace handling via ^\s*
                match = pattern.match(original_line)
                if match:
                    matched_key = key
                    value = match.group(1).strip()
                    self._add_to_metadata(metadata, key, value)
                    current_key = key
                    last_metadata_line = i
                    break

            # If no new key matched, but we are in a multi-line value, append to it
            if current_key and not matched_key:
                # Continuation of a multi-line value (e.g., a wrapped Synopsis)
                self._append_to_metadata(metadata, current_key, stripped)
                last_metadata_line = i

        # If no metadata was found at all, return the original text as the body
        if last_metadata_line == -1:
            return metadata, text.strip()

        # Find body start: the first blank line AFTER the last matched metadata line
        body_start = last_metadata_line + 1
        for i in range(last_metadata_line + 1, scan_limit):
            if not lines[i].strip():
                body_start = i + 1
                break

        # Reconstruct the body text from where the header ended
        body_text = '\n'.join(lines[body_start:]).strip()

        return metadata, body_text

    def _add_to_metadata(self, metadata: StoryMetadata, key: str, value: str):
        if key == "author":
            # Clean up common parentheticals like (a pseudonym) or (pen name)
            value = re.sub(r'\s*\(.*?(?:pseudonym|pen\s*name|alias|anonymous).*?\)', '', value, flags=re.IGNORECASE).strip()
            metadata.author = value
        elif key == "tags":
            metadata.tags = [t.strip() for t in re.split(r'[,;]', value) if t.strip()]
        elif key == "warnings":
            metadata.warnings = [w.strip() for w in re.split(r'[,;]', value) if w.strip()]
        else:
            setattr(metadata, key, value)

    def _append_to_metadata(self, metadata: StoryMetadata, key: str, value: str):
        current_val = getattr(metadata, key, "")
        if isinstance(current_val, str):
            setattr(metadata, key, f"{current_val} {value}".strip())
        elif isinstance(current_val, list):
            new_items = [t.strip() for t in re.split(r'[,;]', value) if t.strip()]
            current_val.extend(new_items)
