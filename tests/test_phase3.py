import pytest
from butterfly.metadata_extractor import MetadataExtractor


def test_metadata_extractor_standard_header():
    extractor = MetadataExtractor()
    sample_text = """Title: The Midnight Journey
Author: Jane Doe
Date: 1999-10-31
Warnings: Violence, Strong Language
Tags: fantasy, adventure, magic
Synopsis: A young wizard discovers a hidden portal in his attic.

Once upon a time, in a land far away, the wizard stepped through the portal.
It was dark and cold.
"""
    metadata, body = extractor.extract(sample_text)

    assert metadata.title == "The Midnight Journey"
    assert metadata.author == "Jane Doe"
    assert metadata.date == "1999-10-31"
    assert metadata.warnings == ["Violence", "Strong Language"]
    assert metadata.tags == ["fantasy", "adventure", "magic"]
    assert "A young wizard discovers" in metadata.synopsis
    assert body.startswith("Once upon a time")


def test_metadata_extractor_multiline_synopsis():
    extractor = MetadataExtractor()
    sample_text = """Title: Deep Space
Author: SciFi Writer
Synopsis: This is a long synopsis that 
spans multiple lines because the 
original author wrapped their text.

The ship launched at dawn.
"""
    metadata, body = extractor.extract(sample_text)

    assert "spans multiple lines" in metadata.synopsis
    assert body.startswith("The ship launched")


def test_metadata_extractor_no_header():
    extractor = MetadataExtractor()
    sample_text = """This is just a story with no header.
It starts immediately with the narrative.
"""
    metadata, body = extractor.extract(sample_text)

    assert metadata.title is None
    assert metadata.author is None
    assert body == sample_text.strip()


def test_metadata_extractor_messy_tags():
    extractor = MetadataExtractor()
    sample_text = """Title: Test
Tags: romance,  drama ;  sci-fi
"""
    metadata, body = extractor.extract(sample_text)

    assert metadata.tags == ["romance", "drama", "sci-fi"]
