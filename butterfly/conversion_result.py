from typing import List, Optional

from pydantic import BaseModel, Field

from .story_metadata import StoryMetadata


class ConversionResult(BaseModel):
    """The output contract for processing a single file."""
    success: bool = Field(description="Whether the conversion completed without fatal errors")
    input_path: str = Field(description="Original file path")
    output_path: Optional[str] = Field(default=None, description="Target Markdown file path")
    markdown_content: str = Field(default="", description="The final Markdown output")
    metadata: StoryMetadata = Field(default_factory=StoryMetadata, description="Extracted frontmatter data")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings or fallback notifications")
    used_llm_fallback: bool = Field(default=False, description="True if LLM was invoked for ambiguity resolution")
    applied_transformations: List[str] = Field(default_factory=list, description="List of transformation IDs applied")
    is_non_story: bool = Field(default=False, description="True if file was identified as index/nav and skipped")

    def to_yaml_frontmatter(self) -> str:
        """Generate YAML frontmatter string from metadata."""
        if self.metadata.is_empty():
            return ""

        # Filter out None values and empty lists for clean YAML
        clean_meta = {
            k: v for k, v in self.metadata.model_dump().items()
            if v is not None and (not isinstance(v, list) or len(v) > 0)
        }

        if not clean_meta:
            return ""

        import yaml
        yaml_str = yaml.dump(clean_meta, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n\n"
