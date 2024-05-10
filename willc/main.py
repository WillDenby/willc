"""A Command Line Tool that replicates the built-in Unix `wc` tool."""

# Standard library imports

import os
import sys
import locale
from pathlib import Path
from typing import Union, Optional
from io import BytesIO, BufferedReader

# Third party imports
import typer

app = typer.Typer()


def process_file(
    file_stream: Union[BytesIO, BufferedReader],
    wbytes: bool = False,
    lines: bool = False,
    multibytes: bool = False,
    words: bool = False,
) -> list[str]:
    """Perform specified count options on a given file.

    This function also contains the relevant helper functions.

    Args:
        file_stream: Streamed in from caller in main.
        wbytes: Whether to count bytes.
        lines: Whether to count lines.
        multibytes: Whether to count multibytes.
        words: Whether to count words.

    Returns:
        A list containing values for any of the four options, for unpacking and displaying back in main. These are as strings, to aid manipulation in main.
    """

    def count_bytes(file_stream: Union[BytesIO, BufferedReader]) -> str:
        """Count and return number of bytes"""
        file_stream.seek(0, os.SEEK_END)
        wbytes = file_stream.tell()
        file_stream.seek(0)
        return str(wbytes)

    def count_lines(file_stream: Union[BytesIO, BufferedReader]) -> str:
        """Count and return number of bytes"""
        file_stream.seek(0)
        lines = sum(
            buf.count(b"\n") for buf in iter(lambda: file_stream.read(1024 * 1024), b"")
        )
        return str(lines)

    def count_multibytes(file_stream: Union[BytesIO, BufferedReader]) -> str:
        """Count and return number of multibytes"""
        current_locale_encoding = locale.getpreferredencoding()
        file_stream.seek(0)
        multibytes = file_stream.read()
        multibytes = multibytes.decode(current_locale_encoding)
        return str(len(multibytes))

    def count_words(file_stream: Union[BytesIO, BufferedReader]) -> str:
        """Count and return number of words"""
        file_stream.seek(0)
        words = file_stream.read().decode()
        return str(len(words.split()))

    results = []
    if lines:
        results.append(count_lines(file_stream))
    if words:
        results.append(count_words(file_stream))
    if wbytes:
        results.append(count_bytes(file_stream))
    if multibytes:
        results.append(count_multibytes(file_stream))
    return results


def c_m_overruler(cli_args: list, c: bool, m: bool) -> tuple:
    """If c and m are both true, return only the last one used in `cli_args` as true"

    As in the original `wc` utility, -c and -m cancel out any prior usage of the other.

    Args:
        cli_args: Streamed in from caller in main.
        c: The option to count bytes.
        m: The option to count multibytes.

    Returns:
        Updated boolean values for c and m, for unpacking in main"""

    flattened_opts = []
    for arg in cli_args:
        if arg.startswith("-") and len(arg) > 1 and not arg.startswith("--"):
            flattened_opts.extend(f"-{char}" for char in arg[1:])
        else:
            flattened_opts.append(arg)
    m_last_index = max(
        (i for i, arg in enumerate(flattened_opts) if arg in ["-m", "--multibytes"]),
        default=-1,
    )
    c_last_index = max(
        (i for i, arg in enumerate(flattened_opts) if arg in ["-c", "--bytes"]),
        default=-1,
    )
    c = c_last_index > m_last_index
    m = m_last_index > c_last_index
    return c, m


@app.command()
def willc(
    files: Optional[list[Path]] = typer.Argument(
        None, help="The file(s) to process", exists=True, readable=True
    ),
    c: bool = typer.Option(
        False,
        "--bytes",
        "-c",
        help="The number of bytes in each input file is written to the "
        "standard output. This will cancel out any prior usage "
        "of the -m option.",
    ),
    l: bool = typer.Option(
        False,
        "--lines",
        "-l",
        help="The number of lines in each input file is written to the "
        "standard output.",
    ),
    m: bool = typer.Option(
        False,
        "--multibytes",
        "-m",
        help="The number of characters in each input file is "
        "written to the standard output. If the current "
        "locale does not support multibyte characters, "
        "this is equivalent to the -c option. This will "
        "cancel out any prior usage of the -c option.",
    ),
    w: bool = typer.Option(
        False,
        "--words",
        "-w",
        help="The number of words in each input file is written to the "
        "standard output.",
    ),
):
    """willc can be used to display the number of lines, words, and bytes contained in each input file, or standard input (if no file is specified) to the standard output."""

    # Setting the default to -clw if no options are specified
    if not any([c, l, m, w]):
        c = l = w = True

    # Ensuring that `-m`` and `-c`` overrule any prior usage of the other.
    if c and m:
        c, m = c_m_overruler(sys.argv, c, m)

    # Read from passed in files and print to standard output
    if files:
        totals = []
        for file in files:
            with file.open("rb") as file_stream:
                std_out = process_file(file_stream, c, l, m, w)
                std_out.append(str(file))
                if not totals:
                    totals = [0] * (len(std_out) - 1)
                totals = [total + int(num) for total, num in zip(totals, std_out[:-1])]
                print("\t".join(std_out))

        if len(files) > 1:
            print("\t".join(map(str, totals)) + "\ttotal")
    # Read from standard input if no files specified
    else:
        stdin_data = sys.stdin.buffer.read()
        stdin_buffer = BytesIO(stdin_data)
        std_out = process_file(stdin_buffer, c, l, m, w)
        std_out.append("stdin")
        print("\t".join(std_out))
