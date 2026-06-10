import pytest
from butterfly.story_stitcher import StoryStitcher
from butterfly.boilerplate_stripper import BoilerplateStripper


def test_story_stitcher_pagination_removal():
    stitcher = StoryStitcher()
    text = "The hero drew his sword.\n\n[Page 2 of 5]\n\nHe swung it wildly."
    result = stitcher.clean_pagination_and_duplicates(text)

    assert "[Page 2 of 5]" not in result
    assert "The hero drew his sword." in result
    assert "He swung it wildly." in result


def test_story_stitcher_duplicate_suppression():
    stitcher = StoryStitcher()
    # Simulate a badly scraped file with repeated headers
    text = "The Story Title\n\nChapter 1\n\nThe Story Title\n\nThe adventure began."
    result = stitcher.clean_pagination_and_duplicates(text)

    # The second "The Story Title" should be suppressed
    assert result.count("The Story Title") == 1
    assert "Chapter 1" in result


def test_boilerplate_stripper_disclaimers():
    stripper = BoilerplateStripper()
    text = "The end.\n\nDisclaimer: All characters are fictional and any resemblance to real persons is coincidental."
    result = stripper.strip_boilerplate(text)

    assert "Disclaimer:" not in result
    assert "The end." in result


def test_boilerplate_stripper_trailing_notes():
    stripper = BoilerplateStripper()
    text = "And they lived happily ever after.\n\nFeedback welcome at author@email.com\n\nMore stories at USENET.org"
    result = stripper.strip_boilerplate(text)

    assert "happily ever after." in result
    assert "Feedback welcome" not in result
    assert "USENET.org" not in result


def test_pipeline_idempotency():
    # Running the text cleaner twice should not degrade the text further
    from butterfly.text_cleaner import TextCleaner
    cleaner = TextCleaner()
    text = "He waited . . . \n\n***\n\nThe end."

    result1 = cleaner.clean_prose(text, "plaintext_wrapped")
    result2 = cleaner.clean_prose(result1, "plaintext_wrapped")

    assert result1 == result2
