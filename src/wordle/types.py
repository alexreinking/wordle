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


class Player(Enum):
    Guesser = 0
    WordCzar = 1


@dataclass
class GameState:
    solution: str
    guesses: [str] = field(default_factory=list)
    hints: [[Hint]] = field(default_factory=list)
