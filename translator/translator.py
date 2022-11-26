"""Multi-lingual translation model for subtitle translation."""

import os
import time
from typing import Callable, Sequence
from easynmt import EasyNMT
from pprint import pprint as pp



ENCODING = 'utf8'  # For tamil chars in windows OS
CHUNK_SIZE = 1024

def load_translator(target_lang:str, source_lang:str) -> Callable:
    """Load translation model function."""

    model = EasyNMT('mbart50_m2m')
    #model = EasyNMT('m2m_100_418M')

    # Check if language pair in model
    lang_pair = f"{source_lang}-{target_lang}"
    just_ta = [lp for lp in list(model.lang_pairs)
               if target_lang in lp]
    assert lang_pair in model.lang_pairs, \
        (f"{source_lang} to {target_lang} translation not in model."
         f"Available language paris are: {'; '.join(just_ta)}")
    # Make translate function with model and language curried.
    def translate_fn(text:Sequence[str]) -> Sequence[str]:
        """Curried language function."""
        return model.translate(
            text,
            target_lang=target_lang,
            source_lang=source_lang,
            show_progress_bar=False,
            batch_size=CHUNK_SIZE,
            document_language_detection=False,
            max_new_tokens=50
            )

    # print(model.translate.__doc__)

    return translate_fn

def printraw(*text):
    rawout = open(1, 'w', encoding=ENCODING, closefd=False)
    print(*text, file=rawout)
    rawout.flush(); rawout.close()


if __name__ == '__main__':
    target_lang, source_lang = 'ta', 'en'
    translator = load_translator(target_lang, source_lang)
    tr_text = translator(["Testing translator, working!"])
    printraw(" ".join(tr_text))
