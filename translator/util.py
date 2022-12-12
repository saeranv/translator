"""Utility functions for translation."""

import numpy as np
from string import punctuation


NUM_WORDS = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
    }


def is_line_alpha(line: str) -> bool:
    """True if any char in line is alphabetic, else False."""
    return any(c.isalpha() for c in line)


def is_line_numeric(line: str) -> bool:
    """True if any char in line is numeric, else False."""
    return any(c.isnumeric() for c in line)


def is_punct(char: str) -> bool:
    """True if char is punctuation, else False."""
    return char in punctuation


def is_line_punct(line: str) -> bool:
    """True if any char in line is punctuation, else False."""
    return any(is_punct(c) for c in line)


def word2num(words: str) -> int:
    """Convert English numbers as words to numbers, keeping punctuation.

    Surprisingly, there's no existing library to do this,
    that's simple to install. Using code from here:
        https://stackoverflow.com/a/67259088/2185097
    """

    numbers = []
    for token in words.replace('-', ' ').split(' '):
        if token in NUM_WORDS:
            numbers.append(NUM_WORDS[token])
        elif token == 'hundred':
            numbers[-1] *= 100
        elif token == 'thousand':
            numbers = [x * 1000 for x in numbers]
        elif token == 'million':
            numbers = [x * 1000000 for x in numbers]
    return sum(numbers)