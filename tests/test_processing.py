import io
from willc.main import process_file


def test_process_file_count_lines():
    file_stream = io.BytesIO(b"line1\nline2\nline3\n")
    result = process_file(file_stream, lines=True)
    assert result[0] == "3", "Should count 3 lines"


def test_process_file_count_words():
    file_stream = io.BytesIO(b"hello world\nwelcome to testing")
    result = process_file(file_stream, words=True)
    assert result[0] == "5", "Should count 5 words"


def test_process_file_bytes_and_lines():
    file_stream = io.BytesIO(b"Hello\nworld\n")
    result = process_file(file_stream, wbytes=True, lines=True)
    assert result[0] == "2", "Should count 2 lines"
    assert result[1] == "12", "Should count 12 bytes including newlines"


def test_process_file_multibytes():
    file_stream = io.BytesIO("こんにちは世界".encode("utf-8"))
    result = process_file(file_stream, multibytes=True)
    assert result[0] == "7", "Should count 7 characters in UTF-8 encoded Japanese text"


def test_process_file_empty_file():
    file_stream = io.BytesIO(b"")
    result = process_file(file_stream, wbytes=True, lines=True, words=True)
    assert result == [
        "0",
        "0",
        "0",
    ], "Should handle empty file with zero counts"
