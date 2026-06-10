from typing import List, Optional

from pydantic import BaseModel, Field


class StoryMetadata(BaseModel):
    """Normalized metadata extracted from story headers."""
    title: Optional[str] = Field(default=None, description="The story title")
    author: Optional[str] = Field(default=None, description="The story author")
    date: Optional[str] = Field(default=None, description="Publication or archive date")
    tags: List[str] = Field(default_factory=list, description="Normalized tags/keywords")
    warnings: List[str] = Field(default_factory=list, description="Content warnings")
    synopsis: Optional[str] = Field(default=None, description="Story summary or synopsis")
    story_code: Optional[str] = Field(default=None, description="Archive-specific story code")
    archive_name: Optional[str] = Field(default=None, description="Source archive name")
    chapter_info: Optional[str] = Field(default=None, description="Chapter or part numbering info")

    def is_empty(self) -> bool:
        """Check if no meaningful metadata was extracted."""
        return not any([
            self.title, self.author, self.date, self.tags,
            self.warnings, self.synopsis, self.story_code,
            self.archive_name, self.chapter_info
        ])
