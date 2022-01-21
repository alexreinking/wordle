from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List

import click

MAX_GUESSES = 6
WORD_LENGTH = 5

SCRIPT_PATH = Path(__file__).parent
DICT_PATH = SCRIPT_PATH.parent.parent / 'dictionary.txt'

WORDS_SET = set(word.lower() for word in DICT_PATH.read_text().split('\n')
                if len(word) == WORD_LENGTH)
WORDS = list(sorted(WORDS_SET))


class Hint(Enum):
    Correct = 0
    CorrectLetter = 1
    Incorrect = 2

    def __str__(self):
        match self:
            case Hint.Correct:
                return '*'
            case Hint.CorrectLetter:
                return '?'
            case Hint.Incorrect:
                return 'x'

    @property
    def emoji(self):
        match self:
            case Hint.Correct:
                return u'🟩'
            case Hint.CorrectLetter:
                return u'🟨'
            case Hint.Incorrect:
                return u'🟥'

    @property
    def color(self):
        match self:
            case Hint.Correct:
                return 'green'
            case Hint.CorrectLetter:
                return 'yellow'
            case Hint.Incorrect:
                return 'red'

    @staticmethod
    def parse(letter):
        return {
            '*': Hint.Correct,
            '?': Hint.CorrectLetter,
            'x': Hint.Incorrect,
        }[letter]

    @staticmethod
    def for_guess(guess: str, solution: str) -> List[Hint]:
        hints = []
        for guess_ch, sol_ch in zip(guess, solution):
            if guess_ch == sol_ch:
                hints.append(Hint.Correct)
            elif guess_ch in solution:
                hints.append(Hint.CorrectLetter)
            else:
                hints.append(Hint.Incorrect)
        return hints


class Player(Enum):
    Guesser = 0
    WordCzar = 1


@dataclass(slots=True)
class GameState:
    guesses: List[str] = field(default_factory=list)
    hints: List[List[Hint]] = field(default_factory=list)

    def render(self):
        for guess, hint in zip(self.guesses, self.hints):
            colored_guess = ''.join(click.style(letter, fg=h.color)
                                    for letter, h in zip(guess, hint))
            output = f'{colored_guess}  {"".join(h.emoji for h in hint)}'
            click.echo(output)
