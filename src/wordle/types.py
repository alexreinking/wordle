from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Generator

import click


class RulesError(Exception):
    pass


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

    def __bool__(self):
        return bool(self.guesses and self.hints)


class Player(Enum):
    Guesser = 0
    WordCzar = 1


Guesser = Generator[str, GameState, None]
Czar = Generator[List[Hint], str, None]
