from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

MAX_GUESSES = 6
WORD_LENGTH = 5

WORDS_SET = set(word.lower() for word in Path('dictionary.txt').read_text().split('\n')
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


def get_hint_for_guess(guess: str, solution: str) -> [Hint]:
    """
    >>> get_hint_for_guess('aaper', 'apple')
    [<Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Incorrect: 2>]
    """
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


@dataclass
class GameState:
    solution: str
    guesses: [str] = field(default_factory=list)
    hints: [[Hint]] = field(default_factory=list)
