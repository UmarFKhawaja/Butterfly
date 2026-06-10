import re
from typing import Tuple

from butterfly.story_metadata import StoryMetadata


class MetadataExtractor:
    """Extracts and normalizes metadata from story headers, separating it from the body."""

    def __init__(self):
        # Case-insensitive regex patterns for common USENET/header fields
        self.patterns = {
            "title": re.compile(r'^(?:title|story title)\s*:\s*(.+)$', re.IGNORECASE),
            "author": re.compile(r'^(?:author|by|written by)[:\s]+(.+)$', re.IGNORECASE),
            "date": re.compile(r'^(?:date|posted|published)\s*:\s*(.+)$', re.IGNORECASE),
            "warnings": re.compile(r'^(?:warnings?|content warnings?)\s*:\s*(.+)$', re.IGNORECASE),
            "tags": re.compile(r'^(?:tags?|keywords?|categories?)\s*:\s*(.+)$', re.IGNORECASE),
            "synopsis": re.compile(r'^(?:synopsis|summary|description)\s*:\s*(.+)$', re.IGNORECASE),
            "archive_name": re.compile(r'^(?:archive|archive name|source)\s*:\s*(.+)$', re.IGNORECASE),
            "story_code": re.compile(r'^(?:story code|code|id)\s*:\s*(.+)$', re.IGNORECASE),
        }

    def extract(self, text: str) -> Tuple[StoryMetadata, str]:
        """
        Parses the header and returns (metadata, body_text).
        """
        metadata = StoryMetadata()
        lines = text.split('\n')

        current_key = None
        header_end_line = -1

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Blank line often signifies the end of a multi-line value or the header block
            if not stripped:
                if current_key is not None:
                    current_key = None
                continue

            # Check if this line starts a new metadata field
            matched_key = None
            for key, pattern in self.patterns.items():
                match = pattern.match(stripped)
                if match:
                    matched_key = key
                    value = match.group(1).strip()
                    self._add_to_metadata(metadata, key, value)
                    current_key = key
                    header_end_line = i
                    break

            # If no new key matched, but we are in a multi-line value, append to it
            if current_key and not matched_key:
                self._append_to_metadata(metadata, current_key, stripped)
                header_end_line = i
            elif not matched_key and current_key is None and i > 5:
                # We've gone past the likely header region without matching new keys.
                # Assume the body has started.
                header_end_line = i - 1
                break

        # Reconstruct the body text from where the header ended
        body_start = header_end_line + 1
        body_text = '\n'.join(lines[body_start:]).strip()

        return metadata, body_text

    def _add_to_metadata(self, metadata: StoryMetadata, key: str, value: str):
        if key == "author":
            # Clean up common parentheticals like (a pseudonym)
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
