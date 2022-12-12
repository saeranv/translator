"""Multi-lingual translation model for subtitle translation."""

import os
import sys
from functools import reduce
from pprint import pprint as pp
from typing import Callable, Sequence
import numpy as np
from numpy import typing as npt

from . import translator as tr
from . import util
is_line_alpha, is_line_numeric = \
    util.is_line_alpha, util.is_line_numeric


DATA_DIR = os.path.join(os.getcwd(), "srt_data")
TARGET_LANG = 'ta'
SOURCE_LANG = 'en'
ENCODING_WRITE = 'utf-16-le'  # for .srt file
ENCODING_PRINT = 'utf-8'
DEFAULT_CHUNK_SIZE = 64
DEFAULT_INCL_EN = False


def get_srt_fname(srt_keyword: str) -> str:
    """Get .srt file."""
    def find_srt(f): return (f.endswith(".srt") and srt_keyword in f)
    _srt_fnames = os.listdir(DATA_DIR)
    srt_fnames = [f for f in _srt_fnames
                  if find_srt(f) and '_tamil' not in f]

    assert len(srt_fnames) == 1, \
        (f"Trouble finding .srt files with keyword "
            f" '{srt_keyword}' in {os.path.split(DATA_DIR)[1]} "
            f"directory. Available files are:\n\n"
            f"- " + reduce(lambda a, b: f"{a}\n- {b}", _srt_fnames) +
            f"\n\nCheck if your keyword is unique and correct!\n")

    return srt_fnames[0]


def is_line_timestamp(line: str) -> bool:
    """True if line is a timestamp line, else False."""
    return '-->' in line


def fix_line_breaks(_subs_ta):
    """Hacky fix to line break bug.

    If linebreaks after final line of dialogue is missing,
    the subtitles group together incorrectly. The text snippet
    below illustrates a correct example. Dialogue at line 2 doesn't
    need a linebreak, but line 3 does.

    ```text
    0. 879\n
    1. 00:40:35,107 --> 00:40:38,304\n
    2. விடாமல்
    3. மற்றும் விலா எலும்புகளை.\n
    4. \n
    5. 880\n
    6. 00:40:38,343 --> 00:40:40,971\n
    7. விடாமல்
    8. ஒரு காயம் அளவுக்கு.\n
    9. \n
    ```

    This function checks that lines after the timestamp until
    the last dialogue line (i.e line 6 to 2) has a linebreak,
    and adds it if not.
    """

    subs_ta = []  # w/ fixed linebreaks
    for i in range(len(_subs_ta)):
        subs_ta += [_subs_ta[i]]
        # if not timestamp line, continue
        if not is_line_timestamp(_subs_ta[i]):
            continue  # Not timestamp line
        # traverse backwards, add line break in case its missing
        for j in range(len(subs_ta))[::-1]:
            subs_ta[j] = subs_ta[j].replace('\n', '') + '\n'
            if is_line_alpha(subs_ta[j]):
                break

    return subs_ta


def translate_text(
        translator: Callable,
        text_arr: npt.NDArray) -> npt.NDArray:
    """Translate text.

    Args:
        text_arr: 1D array of tuples, with each tuple representing
        one line of text via multiple characters:
        ```
        np.array(
            ['00:00:27,945 --> 00:00:32,783\n',
                '[Naru, in Comanche] <i>Soobesükütsa tüa</i>\n',
                '<i>pia mupitsl ikÜ kimai</i>.\n',
                '\n',
                '00:00:34,326 --> 00:00:39,748\n',
                '[in English] <i>A long time ago, it is said,</i>\n',
                '<i>a monster came here.</i>\n',
                '\n'])
        ```
    """
    # Map True if alpha else False
    alpha_bool = np.array(
        [is_line_alpha(line)
         for i, line in enumerate(text_arr)],
        dtype=bool)
    text_arr[alpha_bool] = translator(list(text_arr[alpha_bool]))
    return text_arr


def chunk_subs(subs_en: Sequence, chunk_size: int) -> Sequence:
    """Chunk sub array to ensure fit language model requirements."""

    N, subs_en_chunks = len(subs_en), []
    for i in range(0, N, chunk_size):
        # Chunk indexes to 1024 len
        i0, i1 = i, i+chunk_size
        i1 = N if i1 >= N else i1
        # Extract strings
        subs_en_chunks += [np.array(subs_en[i0:i1], dtype=str)]
    return subs_en_chunks


def concat_en(subs_ta: Sequence, subs_en: Sequence) -> npt.NDArray:
    """Concat english subtitles after timestamp."""
    # Traverse translated subs backwards
    _subs_ta = np.array(subs_ta, dtype=str)
    _subs_en = np.array(subs_en, dtype=str)
    _idx, concat_subs = [], []
    for i in range(len(_subs_en))[::-1]:
        line = _subs_en[i]
        if is_line_alpha(line):
            _idx += [i]
        elif is_line_timestamp(line):
            # Once we hit timestamp concat prior lines
            concat_subs += list(_subs_ta[_idx])
            concat_subs += list(_subs_en[_idx])
            concat_subs += [line]
            _idx = []
        else:
            concat_subs += [line]

    return np.array(concat_subs[::-1], dtype=str)


def main(
        subs_en: Sequence,
        translator: Callable,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        incl_en: bool = DEFAULT_INCL_EN
        ) -> str:
    """Main function."""

    # Translate
    subs_en_chunks = chunk_subs(subs_en, chunk_size)
    subs_ta_chunks = [translate_text(translator, _subs_en.copy())
                      for _subs_en in subs_en_chunks]


    subs_ta = list(reduce(lambda x, y: list(x) + list(y),
                          subs_ta_chunks))  # unchunk
    if incl_en:
        subs_ta = concat_en(subs_ta, subs_en)
    subs_ta = fix_line_breaks(subs_ta)

    return subs_ta


if __name__ == "__main__":

    # Parse args
    def parser_quit():
        parser.print_help(); sys.exit()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword_srt', type=str,
                        help='Keyword to search for .srt file.')
    parser.add_argument('-c', '--chunk_size', type=int,
                        default=DEFAULT_CHUNK_SIZE,
                        help='Number of words per translation.')
    parser.add_argument('-o', '--original_included', type=int,
                        default=int(DEFAULT_INCL_EN),
                        help=('Include original subtitles above '
                             'translated subtitles.'))
    parser.add_argument('--file', action='store_true',
                        help=('Optional, write translation to auto-named file. '
                              'By default translation streams to stdout.'))
    parser.add_argument('-p', '--pickle', type=int,
                        default=0, help=f'Use pickle. Default {0}.')

    args = parser.parse_args()
    srt_keyword = args.keyword_srt
    chunk_size = args.chunk_size
    incl_en = bool(args.original_included)
    write_file = args.file
    use_pickle = bool(args.pickle)

    # Check inputs and quit if not correct
    if len(sys.argv) == 1 or srt_keyword is None:
        parser_quit()

    # Find the file with keyword
    srt_fname_en = get_srt_fname(srt_keyword)
    if write_file:
        print(f"Found {srt_fname_en} with keyword {srt_keyword}. "
            f"Translating with {chunk_size} chunk size...")
    srt_fpath_en = os.path.join(DATA_DIR, srt_fname_en)
    assert os.path.exists(srt_fpath_en)
    with open(srt_fpath_en, mode='r') as f:
        subs_en = f.readlines()

    # Translate
    # Load translator
    translator = tr.load_translator(
        SOURCE_LANG, TARGET_LANG, batch_size=chunk_size, use_pickle=use_pickle)
    subs_ta = main(
        subs_en, translator, chunk_size, incl_en)

    if not write_file:
        print("".join(subs_ta))
    else:
        srt_fname_ta = srt_fname_en.replace(".srt", "_tamil.srt")
        srt_fpath_ta = os.path.join(DATA_DIR, srt_fname_ta)

        # Write file
        with open(srt_fpath_ta, mode='w', encoding=ENCODING_PRINT) as f:
            f.writelines(subs_ta)
            #if 3990 <= i <= 4000: print(i, ln)

        print(f"Translated {len(subs_ta)} lines, saved as {srt_fname_ta}.")
        print("".join(subs_ta[:min(15, len(subs_ta))]))
