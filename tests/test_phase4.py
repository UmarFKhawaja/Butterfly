import pytest
from butterfly.text_cleaner import TextCleaner


def test_text_cleaner_unwrap_lines():
    cleaner = TextCleaner()
    wrapped_text = "This is a line of text that is hard wrapped\nat a specific length without proper paragraph\nbreaks. It continues on the next line.\n\nThis is a new paragraph."

    result = cleaner.clean_prose(wrapped_text, "plaintext_wrapped")

    # First paragraph should be merged into one line
    assert "This is a line of text that is hard wrapped at a specific length without proper paragraph breaks." in result
    # Second sentence should also be merged
    assert "It continues on the next line." in result
    # Paragraph break should be preserved
    assert "\n\nThis is a new paragraph." in result


def test_text_cleaner_scene_breaks():
    cleaner = TextCleaner()
    text_with_breaks = "The end of the scene.\n\n***\n\nThe next scene begins."

    result = cleaner.clean_prose(text_with_breaks, "plaintext_wrapped")

    assert "\n---\n" in result
    assert "***" not in result


def test_text_cleaner_hyphenation_repair():
    cleaner = TextCleaner()
    # Test case with an ACTUAL hyphen at the end of the line
    hyphenated_text = "The beau-\ntiful butterfly flew across the sky."

    result = cleaner.clean_prose(hyphenated_text, "plaintext_wrapped")

    # The hyphen and newline should be removed, cleanly joining the word
    assert "beautiful" in result
    assert "beau-" not in result
    assert "\ntiful" not in result


def test_text_cleaner_chapter_normalization():
    cleaner = TextCleaner()
    text_with_chapter = "End of previous part.\nChapter 1\nThe beginning."

    result = cleaner.clean_prose(text_with_chapter, "plaintext_wrapped")

    # Chapter heading should be isolated with blank lines
    assert "\n\nChapter 1\n\n" in result


def test_text_cleaner_punctuation():
    cleaner = TextCleaner()
    messy_punct = "He waited . . . and then he left ."

    result = cleaner.clean_prose(messy_punct, "plaintext_wrapped")

    assert "..." in result
    assert " ." not in result  # Space before period removed
