import re


class StoryStitcher:
    """Handles pagination artifacts, duplicate headers/footers, and multipart stitching."""

    def clean_pagination_and_duplicates(self, text: str) -> str:
        """Removes page navigation markers and repeated boundary content."""
        lines = text.split('\n')
        cleaned_lines = []

        # Patterns for common pagination artifacts
        pagination_patterns = [
            r'^\s*\[?\s*page\s+\d+\s*(?:of\s+\d+)?\s*\]?\s*$',
            r'^\s*\[?\s*(?:click\s+here\s+for\s+)?(?:next|previous)\s+(?:page|part)\s*\]?\s*$',
            r'^\s*-\s*-\s*-\s*\d+\s*-\s*-\s*-\s*$',
        ]

        # Pattern for repeated headers/footers (e.g., title repeating every few pages)
        # We'll use a simple heuristic: if a short line (< 50 chars) repeats exactly, skip subsequent occurrences
        seen_short_lines = set()

        for line in lines:
            stripped = line.strip()

            # 1. Check for pagination artifacts
            if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in pagination_patterns):
                continue

            # 2. Suppress duplicate short headers/footers (e.g., repeated "The Story Title" or "End of Part 1")
            if len(stripped) < 50 and stripped:
                if stripped in seen_short_lines:
                    # Check if it's a legitimate structural repeat (like a chapter heading)
                    # If it's just noise, skip it. For safety, we only skip if it's not a chapter marker.
                    if not re.match(r'^(?:chapter|part|episode)\s+', stripped, re.IGNORECASE):
                        continue
                else:
                    seen_short_lines.add(stripped)

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def stitch_files(self, file_contents: list[str]) -> str:
        """
        Optional: Joins multiple parts of a story. 
        Removes the header of parts 2+ to avoid duplication.
        """
        if not file_contents:
            return ""
        if len(file_contents) == 1:
            return file_contents[0]

        # Keep the full first part
        result = file_contents[0]

        # For subsequent parts, we would ideally run them through metadata_extractor 
        # to strip their headers, then append the body. 
        # For now, we just append with a clear separator.
        for i in range(1, len(file_contents)):
            result += "\n\n---\n\n[Continued from previous part]\n\n" + file_contents[i]

        return result
