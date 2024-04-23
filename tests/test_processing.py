import io
from willc.main import process_file


def test_process_file_count_lines():
    file_stream = io.BytesIO(b"line1\nline2\nline3\n")
    result = process_file(file_stream, filename="testfile", lines=True)
    assert result[0] == '3', "Should count 3 lines"


def test_process_file_count_words():
    file_stream = io.BytesIO(b"hello world\nwelcome to testing")
    result = process_file(file_stream, filename="testfile", words=True)
    assert result[0] == '5', "Should count 5 words"


def test_process_file_no_options_defaults():
    file_stream = io.BytesIO(b"Hello world\nSecond line\nThird line")
    # No options implies -clw by default
    result = process_file(file_stream, filename="testfile")
    assert result[0] == '2', "Should count 2 lines"
    assert result[1] == '6', "Should count 6 words"
    assert result[2] == '34', "Should count 32 bytes including newlines"


def test_process_file_bytes_and_lines():
    file_stream = io.BytesIO(b"Hello\nworld\n")
    result = process_file(file_stream, filename="testfile", wbytes=True, lines=True)
    assert result[0] == '2', "Should count 2 lines"
    assert result[1] == '12', "Should count 12 bytes including newlines"


def test_process_file_multibytes():
    file_stream = io.BytesIO("こんにちは世界".encode('utf-8'))
    result = process_file(file_stream, filename="testfile", multibytes=True)
    assert result[0] == '7', "Should count 7 characters in UTF-8 encoded Japanese text"

def test_process_file_empty_file():
    file_stream = io.BytesIO(b"")
    result = process_file(file_stream, filename="emptyfile", wbytes=True, lines=True, words=True)
    assert result == ['0', '0', '0', 'emptyfile'], "Should handle empty file with zero counts"
