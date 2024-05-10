from typer.testing import CliRunner
from willc.main import app

runner = CliRunner()


def test_bytes_option_single_file():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("Hello World")
        result = runner.invoke(app, ["testfile.txt", "-c"])
    assert "11\ttestfile.txt" in result.stdout


def test_lines_option_single_file():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("Hello\nWorld")
        result = runner.invoke(app, ["testfile.txt", "-l"])
    assert "1\ttestfile.txt" in result.stdout


def test_words_option_single_file():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("Hello World")
        result = runner.invoke(app, ["testfile.txt", "-w"])
    assert "2\ttestfile.txt" in result.stdout


def test_multibyte_option_single_file():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("こんにちは")  # Writing some multibyte characters
        result = runner.invoke(app, ["testfile.txt", "-m"])
    assert "5\ttestfile.txt" in result.stdout


def test_combined_options_single_file():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("Hello World\nGoodbye World")
        result = runner.invoke(app, ["testfile.txt", "-l", "-w", "-c"])
    assert "1\t4\t25\ttestfile.txt" in result.stdout


def test_no_options_uses_default():
    with runner.isolated_filesystem():
        with open("testfile.txt", "w") as f:
            f.write("Hello World")
        result = runner.invoke(app, ["testfile.txt"])
    assert "0\t2\t11\ttestfile.txt" in result.stdout


def test_stdin_input():
    result = runner.invoke(app, input="Hello World")
    assert "0\t2\t11\tstdin" in result.stdout


def test_multiple_files():
    with runner.isolated_filesystem():
        with open("file1.txt", "w") as f1:
            f1.write("Hello")
        with open("file2.txt", "w") as f2:
            f2.write("World")
        result = runner.invoke(app, ["file1.txt", "file2.txt", "-w"])
    assert "1\tfile1.txt" in result.stdout
    assert "1\tfile2.txt" in result.stdout
    assert "2\ttotal" in result.stdout
