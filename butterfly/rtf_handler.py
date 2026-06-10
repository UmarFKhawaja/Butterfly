from striprtf.striprtf import rtf_to_text


class RtfHandler:
    """Detects and converts Rich Text Format (RTF) files into plain text."""

    def is_rtf(self, text: str) -> bool:
        """Check if the text starts with the standard RTF magic header."""
        return text.strip().startswith("{\\rtf")

    def convert_to_text(self, text: str) -> str:
        """
        Strips RTF control words and returns clean plain text.
        """
        try:
            # striprtf handles the complex parsing of RTF control words
            clean_text = rtf_to_text(text)
            return clean_text
        except Exception:
            # Fallback: if striprtf fails, return the original text 
            # and let the rest of the pipeline attempt to clean it.
            return text
