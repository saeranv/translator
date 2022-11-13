"""Multi-lingual translation model for subtitle translation."""

import os
import time
from typing import Callable, Sequence
from easynmt import EasyNMT
from pprint import pprint as pp

ENCODING = 'utf8'  # For tamil chars in windows OS

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
            batch_size=1024,
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
    tr_text = translator(["The door is there."])
    printraw(" ".join(tr_text))
    # fpath = os.path.join(os.getcwd(), "..", "snippet.txt")
    # mtime_ = os.path.getmtime(fpath)
    # tr_text_, text_ = "", ""

    # while True:
    #     #time.sleep(0.5)
    #     mtime = os.path.getmtime(fpath)
    #     if not mtime > mtime_:
    #         #print("...")
    #         continue
    #     with open(fpath, mode="r") as f:
    #         text_arr = f.readlines()
    #         if len(text_arr) > 1: print('len > 1', text_arr)
    #         if len(text_arr) == 0 or text_ == text_arr[0]:
    #             continue
    #         tr_text_arr = translator(text_arr)
    #         if len(tr_text_arr) > 1: print('len > 1', tr_text_arr)
    #         tr_text = tr_text_arr[0] if len(tr_text_arr) > 0 else "..."
    #         print("En:", text_arr[0])
    #         print("Ta:", tr_text)
    #         text_ = text_arr[0]
    #         tr_text_ = tr_text
