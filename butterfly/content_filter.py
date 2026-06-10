import re

from bs4 import BeautifulSoup


class ContentFilter:
    """Identifies files that are not actual stories and should be skipped."""

    def is_non_story(self, text: str, format_type: str) -> bool:
        if format_type == "html":
            soup = BeautifulSoup(text, "lxml")

            # Check for directory listing titles
            title = soup.title.string if soup.title else ""
            if title and re.search(r'^Index of\s+', title, re.IGNORECASE):
                return True

            # Check for directory listing tables (common in Apache/Nginx auto-index)
            if soup.find('table') and re.search(r'Name\s+Last modified\s+Size\s+Description', text, re.IGNORECASE):
                return True

            # Check if the page is mostly just links (navigation)
            links = soup.find_all('a')
            text_length = len(soup.get_text(strip=True))
            link_text_length = sum(len(a.get_text(strip=True)) for a in links)

            if text_length > 0 and (link_text_length / text_length) > 0.8:
                return True

        # Plain text index files often have "Parent Directory" or long lists of .txt links
        elif format_type in ("plaintext_flow", "plaintext_wrapped"):
            if re.search(r'Parent Directory|Index of|\.txt\s+\d{4}-\d{2}-\d{2}', text, re.IGNORECASE):
                # Ensure it's not just a story mentioning a date
                if len(re.findall(r'\.txt', text)) > 5:
                    return True

        return False
