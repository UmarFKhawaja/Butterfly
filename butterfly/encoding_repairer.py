import chardet
import ftfy


class EncodingRepairer:
    """Detects legacy encodings, decodes safely to UTF-8, and repairs mojibake."""

    def repair(self, raw_bytes: bytes) -> str:
        # 1. Detect encoding
        detection = chardet.detect(raw_bytes)
        encoding = detection.get('encoding', 'utf-8') or 'utf-8'
        confidence = detection.get('confidence', 0.0)

        # 2. Decode with replacement safety
        try:
            text = raw_bytes.decode(encoding, errors='replace')
        except LookupError:
            # Fallback if chardet guesses something invalid
            text = raw_bytes.decode('utf-8', errors='replace')

        # 3. Repair mojibake
        repaired_text = ftfy.fix_text(text)

        return repaired_text
