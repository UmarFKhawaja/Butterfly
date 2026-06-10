# Butterfly

Butterfly is a Python CLI for converting archived USENET story files into clean Markdown. It combines heuristic cleanup with an optional local `llama-cpp-python` fallback for especially messy prose.

The current pipeline focuses on story-like plaintext, HTML, and RTF sources commonly found in archive dumps, while skipping non-story files such as directory listings and navigation pages.

## What It Does

- Repairs legacy encodings and common mojibake.
- Converts RTF sources into plain text before the main cleanup pipeline.
- Classifies input as HTML, hard-wrapped plaintext, or flowing plaintext.
- Skips non-story files like index pages and link-heavy archive navigation.
- Cleans HTML archive chrome and converts meaningful content to Markdown.
- Extracts header metadata into YAML frontmatter, including more flexible `By Author` style headers.
- Normalizes prose by unwrapping hard line breaks, repairing split words, preserving scene breaks, and fixing common broken-apostrophe artifacts.
- Removes pagination artifacts, repeated headers/footers, disclaimers, archive-posting lines, and trailing feedback boilerplate.
- Optionally uses a local GGUF model through `llama-cpp-python` when heuristic cleanup still looks ambiguous.

## Requirements

- Python 3.12+
- A local environment with the project dependencies installed
- `striprtf` is used for RTF-to-text conversion
- Optional: a local GGUF model file if you want to use `--use-llm`

## Installation

Create and activate a virtual environment, then install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

If you want GPU-enabled `llama-cpp-python` builds, install with CUDA flags before the editable install:

```bash
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install -e .
```

## Usage

After installation, the CLI entry point is `convert`.

With no arguments, Butterfly uses:

- `input/` for source files
- `output/` for converted Markdown
- `skip/` for skipped non-story files

```bash
convert
```

Useful options:

- `--dry-run`: process files without writing output
- `--verbose` or `-v`: print detailed failures and warnings
- `--use-llm`: enable the optional local LLM fallback
- `--model PATH`: path to a local GGUF model file
- `--discard-skips`: do not save skipped non-story files

Positional arguments:

- `input_dir`: source directory, defaults to `input`
- `output_dir`: Markdown output directory, defaults to `output`
- `skip_dir`: skipped-file directory, defaults to `skip`

Examples:

```bash
convert
convert ./input ./output ./skip --dry-run --verbose
convert ./input ./output ./skipped --use-llm --model /models/story-cleaner.gguf
convert ./input ./output ./skip --discard-skips
```

## How Output Is Written

- Butterfly scans the input directory recursively.
- Hidden files are ignored.
- Output files keep the same relative directory structure.
- Converted files are written with a `.md` extension.
- Files classified as non-story content are skipped from Markdown output.
- By default, skipped source files are copied into a `skip/` directory.
- You can change that location by passing a different third positional argument, or disable skip copies with `--discard-skips`.

Example output:

```md
---
title: The Midnight Journey
author: Jane Doe
date: 1999-10-31
tags:
  - fantasy
  - adventure
warnings:
  - Violence
---

Once upon a time, in a land far away, the wizard stepped through the portal.
```

## Pipeline Overview

1. `EncodingRepairer` decodes raw bytes and fixes mojibake.
2. `RtfHandler` detects RTF input and converts it to plain text.
3. `FormatClassifier` selects the processing path.
4. `ContentFilter` skips index pages and similar non-story files.
5. `HtmlCleaner` removes archive chrome and converts HTML to Markdown when needed.
6. `MetadataExtractor` separates structured header fields from the body and normalizes more byline variants.
7. `TextCleaner` normalizes prose formatting and repairs common broken-apostrophe artifacts.
8. `StoryStitcher` removes pagination and repeated boundary text.
9. `BoilerplateStripper` trims disclaimers, archive-posting lines, and trailing feedback/contact notes.
10. `LlmEnhancer` optionally refines ambiguous output when enabled.

## Extracted Metadata

The converter can emit YAML frontmatter fields such as:

- `title`
- `author`
- `date`
- `tags`
- `warnings`
- `synopsis`
- `story_code`
- `archive_name`

Frontmatter is only emitted when at least one metadata field is populated.

Author extraction is tolerant of both `Author: Name` and `By Name` style headers, and it strips common parenthetical notes such as pseudonym markers when present.

## Supported Source Shapes

- Archive HTML pages with story content wrapped in presentational markup
- RTF files that begin with a standard `{\rtf...}` header
- Plaintext stories with hard-wrapped lines
- Plaintext stories that already flow normally
- Story files with lightweight archive headers, bylines, and trailing feedback/contact boilerplate

## Testing

The repository includes `pytest` coverage for core conversion behaviors, including:

- encoding repair
- RTF conversion
- format classification
- HTML cleanup
- metadata extraction
- prose normalization
- pagination cleanup
- boilerplate stripping
- idempotent text cleanup

Run the test suite with:

```bash
pytest
```

## Project Layout

```text
butterfly/
  cli.py
  conversion_pipeline.py
  conversion_result.py
  content_filter.py
  encoding_repairer.py
  format_classifier.py
  html_cleaner.py
  llm_enhancer.py
  metadata_extractor.py
  rtf_handler.py
  story_metadata.py
  story_stitcher.py
  text_cleaner.py
  boilerplate_stripper.py
tests/
spec/
```

## Notes

- The CLI writes Markdown plus YAML frontmatter; it does not currently emit separate metadata files.
- The optional multipart stitching helper exists in the codebase, but the main CLI currently processes files independently.
- The LLM fallback is conservative: it only runs when enabled, a model loads successfully, and the cleaned body still looks unusually fragmented.
- Skip-copy behavior only applies outside `--dry-run`; dry runs do not write Markdown or skipped files.
- The current CLI defaults make `convert` usable without arguments when your folders are named `input`, `output`, and `skip`.
- The prose cleaner now repairs some legacy `?` apostrophe corruption such as `wasn?t` to `wasn’t`, but it is still a heuristic cleanup step rather than full OCR correction.
