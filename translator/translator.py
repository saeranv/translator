"""Multi-lingual translation model for subtitle translation."""

import os
import sys
import time
from typing import Callable, Sequence
from easynmt import EasyNMT
from pprint import pprint as pp
import pickle

from . import util
from tamil import numeral
num_ta = numeral.num2tamilstr


ENCODING = 'utf8'  # For tamil chars in windows OS
DEFAULT_BATCH_SIZE = 254
PICKLE_FPATH = os.path.join(os.getcwd(), "model.pkl")


def _load_model_pickle():
    """Use cache to speed up about 2x."""
    if not os.path.exists(PICKLE_FPATH):
        print('pickel not found, creating new model')
        with open(PICKLE_FPATH, 'wb') as fout:
            model = EasyNMT('mbart50_m2m')  # EasyNMT('m2m_100_418M')
            pickle.dump(model, fout)

    # Open as pickle file
    with open(PICKLE_FPATH, "rb") as fin:
        model = pickle.load(fin)

    return model


def load_translator(
    source_lang:str,
    target_lang:str,
    batch_size:int,
    use_pickle:bool) -> Callable:
    """Load translation model function."""

    def _find_pairs(
        target_lang:str, lang_pairs:Sequence)->Sequence:
        _lang_pairs = set(lang_pairs)
        return "; ".join([lp for lp in _lang_pairs
                          if target_lang in lp])

    if use_pickle:
        model = _load_model_pickle()
    else:
        model = EasyNMT('mbart50_m2m')  # EasyNMT('m2m_100_418M')

    # Check if language pair in model
    lang_pair = f"{source_lang}-{target_lang}"
    assert lang_pair in model.lang_pairs, \
        (f"{source_lang} to {target_lang} translation not in model. "
         f"Available language pairs are: "
         f"{_find_pairs(target_lang, model.lang_pairs)}")


    # Make translate function with model and language curried.
    def translate_fn(text:Sequence[str]) -> Sequence[str]:
        """Curried language function."""
        return model.translate(
            text,
            target_lang=target_lang,
            source_lang=source_lang,
            show_progress_bar=False,
            batch_size=batch_size,
            document_language_detection=False,
            max_new_tokens=50
            )

    return translate_fn

def printraw(*text):
    rawout = open(1, 'w', encoding=ENCODING, closefd=False)
    print(*text, file=rawout)
    rawout.flush(); rawout.close()


if __name__ == '__main__':

    def parser_quit():
        parser.print_help(); sys.exit()

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text', type=str, default="",
                        help="Text to translate.")
    parser.add_argument('--source_lang', type=str, default='en',
                        help='Source language. Default "en".')
    parser.add_argument('--target_lang', type=str, default='ta',
                        help='Target language. Default "ta".')
    parser.add_argument('-n', '--translate_num', default=0,
                        help='Just translate numbers to Tamil using '
                             'Open-Tamil. Default 0.')
    parser.add_argument('-c', '--chunk_size', type=int,
                        default=DEFAULT_BATCH_SIZE,
                        help='Number of words per translation. '
                             f'Default {DEFAULT_BATCH_SIZE}.')
    parser.add_argument('-p', '--pickle', type=int,
                        default=1, help=f'Use pickle. Default {1}.')
    args = parser.parse_args()


    target_lang = args.target_lang
    source_lang = args.source_lang
    translate_num = bool(args.translate_num)
    batch_size = args.chunk_size
    use_pickle = bool(args.pickle)
    text = input() if not sys.stdin.isatty() else args.text

    if text == "":
        parser_quit()

    if translate_num:
        # Quicker numeric translation to Tamil text
        text_ = [num_ta(util.word2num(c))
                 for c in text.split(" ")]
    else:
        translator_fn = \
            load_translator(
                source_lang, target_lang, batch_size, use_pickle)
        text_ = translator_fn([text])

    text_ = " ".join(text_)
    print(text_, flush=True)
