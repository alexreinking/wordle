import random

import click

from .game import WORDS, WORD_LENGTH
from .types import Hint, Czar


def local(solution='') -> Czar:
    assert not solution or len(solution) == WORD_LENGTH
    solution = solution or random.choice(WORDS)

    hint = None
    while True:
        guess: str = yield hint
        hint = Hint.for_guess(guess, solution)


def _validate_hint_input(hint: str):
    if len(hint) != WORD_LENGTH:
        raise click.UsageError(f'{hint} is not the right length ({WORD_LENGTH})!')

    try:
        return list(map(Hint.parse, hint))
    except KeyError as e:
        raise click.UsageError('Use * = correct, ? = correct letter, and x = incorrect') from e


def remote() -> Czar:
    hint = None
    while True:
        guess = yield hint
        hint = click.prompt(f'hint for {guess}', value_proc=_validate_hint_input)


__all__ = [local, remote]
