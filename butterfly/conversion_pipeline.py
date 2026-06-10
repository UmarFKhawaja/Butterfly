from pathlib import Path

from butterfly.boilerplate_stripper import BoilerplateStripper
from butterfly.content_filter import ContentFilter
from butterfly.conversion_result import ConversionResult
from butterfly.encoding_repairer import EncodingRepairer
from butterfly.format_classifier import FormatClassifier
from butterfly.html_cleaner import HtmlCleaner
from butterfly.llm_enhancer import LlmEnhancer
from butterfly.metadata_extractor import MetadataExtractor
from butterfly.story_stitcher import StoryStitcher
from butterfly.text_cleaner import TextCleaner


class ConversionPipeline:
    def __init__(self, use_llm: bool = False, model_path: str = None):
        self.repairer = EncodingRepairer()
        self.classifier = FormatClassifier()
        self.filter = ContentFilter()
        self.html_cleaner = HtmlCleaner()
        self.metadata_extractor = MetadataExtractor()
        self.text_cleaner = TextCleaner()
        self.stitcher = StoryStitcher()
        self.boilerplate_stripper = BoilerplateStripper()
        self.llm_enhancer = LlmEnhancer(model_path) if use_llm else None

    def process_file(self, input_path: Path, output_path: Path, dry_run: bool = False) -> ConversionResult:
        applied = []
        warnings = []

        try:
            # 1. Read & Repair
            raw_bytes = input_path.read_bytes()
            applied.append("encoding-repair")
            text = self.repairer.repair(raw_bytes)

            # 2. Classify & Filter
            applied.append("format-classification")
            format_type = self.classifier.classify(text)

            applied.append("non-story-filtering")
            if self.filter.is_non_story(text, format_type):
                return ConversionResult(
                    success=True,
                    input_path=str(input_path),
                    is_non_story=True,
                    applied_transformations=applied
                )

            # 3. Initial Clean
            if format_type == "html":
                applied.extend(["html-wrapper-removal", "preformatted-text-extraction", "html-to-markdown-conversion"])
                cleaned_text = self.html_cleaner.clean_and_convert(text)
            else:
                cleaned_text = text

            # 4. Metadata Extraction
            applied.append("metadata-extraction")
            applied.append("metadata-body-separation")
            metadata, body_text = self.metadata_extractor.extract(cleaned_text)
            applied.append("yaml-frontmatter-generation")

            # 5. Advanced Prose Refinement
            applied.extend([
                "whitespace-normalization", "scene-break-normalization",
                "chapter-normalization", "hyphenation-repair",
                "hard-line-break-removal", "paragraph-boundary-preservation",
                "punctuation-normalization"
            ])

            final_body = self.text_cleaner.clean_prose(body_text, format_type)

            # 6. Operational Edge Cases (Pagination, Duplicates, Boilerplate)
            applied.extend(["pagination-normalization", "duplicate-header-footer-suppression"])

            final_body = self.stitcher.clean_pagination_and_duplicates(final_body)

            applied.extend(["boilerplate-stripping", "trailing-boilerplate-stripping", "disclaimer-removal"])

            final_body = self.boilerplate_stripper.strip_boilerplate(final_body)

            # 7. Optional LLM Fallback (if enabled and text is still messy/ambiguous)
            if self.llm_enhancer and self.llm_enhancer.is_available() and len(final_body) > 500:
                # Heuristic trigger: if the text still has excessive short lines after cleaning
                lines = final_body.split('\n')
                short_lines_ratio = sum(1 for l in lines if len(l.strip()) < 40 and l.strip()) / max(len(lines), 1)
                if short_lines_ratio > 0.3:
                    warnings.append("Heuristic cleanup incomplete; invoking LLM fallback.")
                    applied.append("llm-enhancement-fallback")
                    final_body = self.llm_enhancer.enhance_prose(final_body)

            # 8. Idempotency Check (Optional debug step)
            # Running the cleaner twice should yield the same result.
            # (We trust the regex to be idempotent, but this is where you'd add a check if needed).

            return ConversionResult(
                success=True,
                input_path=str(input_path),
                output_path=str(output_path) if not dry_run else None,
                markdown_content=final_body,
                metadata=metadata,
                warnings=warnings,
                applied_transformations=list(set(applied)),  # Deduplicate
                used_llm_fallback="llm-enhancement-fallback" in applied
            )

        except Exception as e:
            # fallback-safe-processing
            return ConversionResult(
                success=False,
                input_path=str(input_path),
                warnings=[f"Pipeline error: {str(e)}"],
                applied_transformations=applied
            )
