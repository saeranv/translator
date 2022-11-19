"""Multi-lingual translation model for subtitle translation."""

import os
import sys
from functools import reduce
from pprint import pprint as pp
from string import whitespace
from typing import Callable, Sequence

import numpy as np

from .translator import load_translator

DATA_DIR = os.path.join(os.getcwd(), "srt_data")
TARGET_LANG = 'ta'
SOURCE_LANG = 'en'
ENCODING_WRITE = 'utf-16-le'  # for .srt file
ENCODING_PRINT = 'utf-8'


def get_srt_fname(srt_keyword:str) -> str:
        """Get .srt file."""
        find_srt = lambda f: (f.endswith(".srt") and srt_keyword in f)
        _srt_fnames = os.listdir(DATA_DIR)
        srt_fnames = [f for f in _srt_fnames if find_srt(f)]

        assert len(srt_fnames) == 1, \
            (f"Trouble finding .srt files with keyword "
             f" '{srt_keyword}' in {os.path.split(DATA_DIR)[1]} "
             f"directory. Available files are:\n\n"
             f"- " + reduce(lambda a, b: f"{a}\n- {b}", _srt_fnames) +
             f"\n\nCheck if your keyword is unique and correct!\n")

        return srt_fnames[0]


def is_line_alpha(line:str) -> bool:
    """True if any char in line is alphabetic, else False."""
    return any(c.isalpha() for c in line)


def is_line_numeric(line:str) -> bool:
    """True if any char in line is numeric, else False."""
    return any(c.isnumeric() for c in line)


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
        if not('-->' in _subs_ta[i]):
            continue # Not timestamp line
        # traverse backwards, add line break in case its missing
        for j in range(len(subs_ta))[::-1]:
            subs_ta[j] = subs_ta[j].replace('\n', '') + '\n'
            if is_line_alpha(subs_ta[j]):
                break

    return subs_ta


def translate_text(translator: Callable, text_arr: Sequence) -> Sequence:
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


# def printraw(*text):
#     rawout = open(1, 'w', encoding=ENCODING_PRINT, closefd=False)
#     print(*text, file=rawout)
#     rawout.flush(); rawout.close()


if __name__ == "__main__":

    assert len(sys.argv) == 2, \
        (f"Invalid argument(s). Usage: python translate_srt.app SRT_KEYWORD\n"
         f"Got {sys.argv[1:]} in args.")


    # Find the file with keyword
    srt_keyword = sys.argv[1]
    srt_fname = get_srt_fname(srt_keyword)
    print(f"Found {srt_fname} with keyword {srt_keyword}. Translating...")

    # Construct file paths
    srt_fname_ta = srt_fname.replace(".srt", "_tamil.srt")
    srt_fpath_en = os.path.join(DATA_DIR, srt_fname)
    srt_fpath_ta = os.path.join(
            DATA_DIR, srt_fname_ta)
    assert os.path.exists(srt_fpath_en)

    # Open file
    with open(srt_fpath_en, mode='r') as f:
        subs_en = f.readlines()

    N, subs_ta = len(subs_en), []

    # Load translator
    translator = load_translator(TARGET_LANG, SOURCE_LANG)

    # Translate
    chunk_size = 64
    for i in range(0, N, chunk_size):
        # Chunk indexes to 1024 len
        i0, i1 = i, i+chunk_size
        i1 = N if i1 >= N else i1
        # Extract strings
        _subs_en = np.array(subs_en[i0:i1], dtype=str)
        _subs_ta = translate_text(translator, _subs_en)
        subs_ta.extend(_subs_ta)

    subs_ta = fix_line_breaks(subs_ta)

    # # Check file
    # for i in range(10):
    #     print(f"en: {subs_en[i]}ta: {subs_ta[i]}")

    # Write file
    with open(srt_fpath_ta, mode='w', encoding=ENCODING_PRINT) as f:
        f.writelines(subs_ta)
        #if 3990 <= i <= 4000: print(i, ln)

    print(f"Translated {len(subs_ta)} lines.")
    print(f"sed -n 100,110p srt_data/{srt_fname_ta} >> cat 100-110 lines.")

