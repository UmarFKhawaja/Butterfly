import pytest
from butterfly.encoding_repairer import EncodingRepairer
from butterfly.format_classifier import FormatClassifier
from butterfly.content_filter import ContentFilter
from butterfly.html_cleaner import HtmlCleaner
from butterfly.rtf_handler import RtfHandler


def test_encoding_repairer_mojibake():
    repairer = EncodingRepairer()

    # 1. Start with the correct text
    correct_text = "café"

    # 2. Encode to UTF-8 (b'caf\xc3\xa9')
    utf8_bytes = correct_text.encode('utf-8')

    # 3. Simulate a legacy system misinterpreting it as latin-1
    # This creates the classic mojibake string: "cafÃ©"
    mangled_text = utf8_bytes.decode('latin-1')

    # 4. Simulate saving that mangled text to a file as UTF-8
    # These are the actual "bad bytes" our repairer will receive
    bad_bytes = mangled_text.encode('utf-8')

    # Now test our repairer on these corrupted bytes
    result = repairer.repair(bad_bytes)

    # ftfy is specifically designed to untangle "cafÃ©" back to "café"
    assert "café" in result
    assert "Ã©" not in result


def test_format_classifier_html():
    classifier = FormatClassifier()
    assert classifier.classify("<html><body><p>Hello</p></body></html>") == "html"
    assert classifier.classify("<font color='red'>Test</font>") == "html"


def test_format_classifier_wrapped():
    classifier = FormatClassifier()
    wrapped_text = "\n".join([
        "This is a line of text that is hard wrapped",
        "at a specific length without proper paragraph",
        "breaks. It continues on the next line because",
        "the author used an old text editor that forced",
        "line breaks at column 72. This is very common",
        "in Usenet archives and old plain text files.",
        "The classifier needs to see enough lines to",
        "confidently determine that this is wrapped text",
        "and not just a series of short, intentional",
        "lines like poetry or a list of items. So we",
        "add more lines to exceed the minimum threshold",
        "of ten lines required by the heuristic logic.",
        "This ensures the mid-sentence break ratio is",
        "calculated correctly and returns the expected",
        "plaintext_wrapped classification result."
    ])
    assert classifier.classify(wrapped_text) == "plaintext_wrapped"


def test_content_filter_index_page():
    content_filter = ContentFilter()
    index_html = "<html><head><title>Index of /stories</title></head><body><table><tr><td>Name</td><td>Last modified</td></tr></table></body></html>"
    assert content_filter.is_non_story(index_html, "html") is True


def test_html_cleaner_strips_chrome():
    cleaner = HtmlCleaner()
    messy_html = """
    <html>
    <head><script>alert('x');</script><style>body{red}</style></head>
    <body>
    <nav>Home | About</nav>
    <font size="4"><center><b>The Story Title</b></center></font>
    <p>Once upon a time.</p>
    <br><br>
    <p>It was dark.</p>
    <footer>Return to Index</footer>
    </body>
    </html>
    """
    result = cleaner.clean_and_convert(messy_html)

    assert "alert" not in result
    assert "Home | About" not in result
    assert "Return to Index" not in result
    assert "The Story Title" in result
    assert "Once upon a time." in result
    assert "It was dark." in result


def test_rtf_handler_conversion():
    handler = RtfHandler()
    # A minimal, valid RTF string
    rtf_text = "{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\n\\f0\\fs24 This is a test story.\\par\n}"

    assert handler.is_rtf(rtf_text) is True

    result = handler.convert_to_text(rtf_text)

    # The output should be clean plain text without RTF control words
    assert "This is a test story." in result
    assert "\\rtf1" not in result
    assert "\\fonttbl" not in result
