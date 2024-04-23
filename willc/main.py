from typing import List, Optional
from pathlib import Path
import locale
import sys
import os
import io

import typer

app = typer.Typer()


def process_file(file_stream, filename: str, wbytes: bool = False,
                 lines: bool = False, multibytes: bool = False, words: bool = False):
    # Set default to -clw if no options are specified
    if not any([wbytes, lines, multibytes, words]):
        wbytes = lines = words = True

    results = []
    if lines:
        results.append(count_lines(file_stream))
    if words:
        results.append(count_words(file_stream))
    if wbytes:
        results.append(count_bytes(file_stream))
    if multibytes:
        results.append(count_multibytes(file_stream))
    results.append(str(filename))
    return results


def count_bytes(file_stream):
    file_stream.seek(0, os.SEEK_END)
    size = file_stream.tell()
    file_stream.seek(0)
    return str(size)


def count_lines(file_stream):
    file_stream.seek(0)
    return str(sum(buf.count(b'\n') for buf in iter(lambda: file_stream.read(1024 * 1024), b'')))


def count_multibytes(file_stream):
    current_locale_encoding = locale.getpreferredencoding()
    file_stream.seek(0)
    byte_content = file_stream.read()
    decoded_content = byte_content.decode(current_locale_encoding)
    return str(len(decoded_content))


def count_words(file_stream):
    file_stream.seek(0)
    content = file_stream.read().decode()
    return str(len(content.split()))


@app.command()
def willc(
        files: Optional[List[Path]] = typer.Argument(None, help="The file(s) to process", exists=True, readable=True),
        c: bool = typer.Option(False, "--bytes", "-c", help="The number of bytes in each input file is written to the "
                                                            "standard output. This will cancel out any prior usage "
                                                            "of the -m option."),
        l: bool = typer.Option(False, "--lines", "-l", help="The number of lines in each input file is written to the "
                                                            "standard output."),
        m: bool = typer.Option(False, "--multibytes", "-m", help="The number of characters in each input file is "
                                                                 "written to the standard output. If the current "
                                                                 "locale does not support multibyte characters, "
                                                                 "this is equivalent to the -c option. This will "
                                                                 "cancel out any prior usage of the -c option."),
        w: bool = typer.Option(False, "--words", "-w", help="The number of words in each input file is written to the "
                                                            "standard output.")
):
    # -m and -c overrules prior usage of the other
    flattened_opts = []
    for arg in sys.argv:
        if arg.startswith('-') and len(arg) > 1 and not arg.startswith('--'):
            flattened_opts.extend(f'-{char}' for char in arg[1:])
        else:
            flattened_opts.append(arg)

    # Find the last index of each option
    m_last_index = max((i for i, arg in enumerate(flattened_opts) if arg in ['-m', '--multibytes']), default=-1)
    c_last_index = max((i for i, arg in enumerate(flattened_opts) if arg in ['-c', '--bytes']), default=-1)

    # Determine which option takes precedence based on the last occurrence
    if m_last_index > c_last_index:
        c = False  # Ignore -c if -m is specified last
    elif c_last_index > m_last_index:
        m = False  # Ignore -m if -c is specified last

    if files is None:
        stdin_data = sys.stdin.buffer.read()
        stdin_buffer = io.BytesIO(stdin_data)
        std_out = process_file(stdin_buffer, "stdin", c, l, m, w)
        print("\t".join(std_out))
    else:
        totals = []
        for file in files:
            with file.open('rb') as file_stream:
                std_out = process_file(file_stream, str(file), c, l, m, w)
                if not totals:
                    totals = [0] * (len(std_out) - 1)
                totals = [total + int(num) for total, num in zip(totals, std_out[:-1])]
                print("\t".join(std_out))

        if len(files) > 1:
            print("\t".join(map(str, totals)) + "\ttotal")



