import re

import markdownify
from bs4 import BeautifulSoup


class HtmlCleaner:
    """Removes presentation-only HTML wrappers and converts to Markdown."""

    def clean_and_convert(self, html_text: str) -> str:
        # 0. Pre-process <br> clusters to avoid BS4 mutation bugs
        # Replace 2 or more <br> tags (with optional whitespace/slashes) with a double newline
        html_text = re.sub(r'(<br\s*/?>\s*){2,}', '\n\n', html_text, flags=re.IGNORECASE)

        soup = BeautifulSoup(html_text, "lxml")

        # 1. Remove non-content tags and archive chrome
        for tag in soup(["script", "style", "meta", "link", "nav", "footer", "header", "form"]):
            tag.decompose()

        # 2. Handle preformatted text that contains prose, not code
        for pre in soup.find_all("pre"):
            pre_text = pre.get_text()
            # If it looks like prose (has normal sentence structure, not code symbols)
            if not re.search(r'[{};=<>]', pre_text) and len(pre_text.split()) > 20:
                pre.name = "div"  # Let markdownify handle it as normal text

        # 3. Strip deprecated presentation tags but keep their text content
        for tag in soup.find_all(["font", "center", "b", "i", "u"]):
            tag.unwrap()

        # 4. Convert to Markdown
        md = markdownify.markdownify(
            str(soup),
            heading_style="ATX",
            strip=["img"],
            bullets="-"
        )

        return md.strip()
