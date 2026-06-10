import re


class FormatClassifier:
    """Classifies input as plaintext_wrapped, plaintext_flow, or html."""

    def classify(self, text: str) -> str:
        # Check for HTML markers (case-insensitive)
        if re.search(r'<(html|body|div|p|font|br)\b', text, re.IGNORECASE):
            return "html"

        # Check for hard-wrapped plaintext
        # Heuristic: Look at the first 100 lines. If most are < 85 chars and don't end in sentence terminators, it's wrapped.
        lines = text.split('\n')[:100]
        if not lines:
            return "plaintext_flow"

        short_lines = 0
        mid_sentence_breaks = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if len(stripped) < 85:
                short_lines += 1
            # If a short line doesn't end with punctuation or a quote, it's likely a mid-sentence wrap
            if len(stripped) < 85 and not re.search(r'[.!?"\']\s*$', stripped):
                mid_sentence_breaks += 1

        # If > 60% of non-empty lines are short and frequently break mid-sentence
        non_empty_lines = [l for l in lines if l.strip()]
        if len(non_empty_lines) > 10 and (short_lines / len(non_empty_lines)) > 0.6 and (mid_sentence_breaks / len(non_empty_lines)) > 0.3:
            return "plaintext_wrapped"

        return "plaintext_flow"
