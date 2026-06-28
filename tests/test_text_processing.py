from services.text_processing import clean_text, note_sentences


def test_clean_text_removes_pdf_headers() -> None:
    raw = """
    1/72 DSAI WEB ENABLED TECHNOLOGY March 20, 2024 JAVA SCRIPT
    JavaScript is a client side scripting language.
    2/72 DSAI WEB ENABLED TECHNOLOGY March 20, 2024 JAVA SCRIPT
    """

    cleaned = clean_text(raw)

    assert "DSAI WEB ENABLED TECHNOLOGY" not in cleaned
    assert "1/72" not in cleaned
    assert "JavaScript is a client side scripting language." in cleaned


def test_note_sentences_filters_code_heavy_lines() -> None:
    raw = """
    JavaScript functions are reusable blocks of code.
    var x = prompt("name"); document.write(x + "<br>"); if (x == "a") { alert(x); }
    """

    notes = note_sentences(raw)

    assert notes == ["JavaScript functions are reusable blocks of code."]
