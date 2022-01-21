import random

import click

from wordle.types import WORD_LENGTH, Hint, WORDS


def local(solution=''):
    assert not solution or len(solution) == WORD_LENGTH
    solution = solution or random.choice(WORDS)

    def _get_hint(guess):
        return Hint.for_guess(guess, solution)

    return _get_hint


def _validate_hint_input(hint: str):
    if len(hint) != WORD_LENGTH:
        raise click.UsageError(f'{hint} is not the right length ({WORD_LENGTH})!')

    try:
        return list(map(Hint.parse, hint))
    except KeyError as e:
        raise click.UsageError('Use * = correct, ? = correct letter, and x = incorrect') from e


def remote():
    def _ask_human(guess):
        return click.prompt(f'hint for {guess}', value_proc=_validate_hint_input)

    return _ask_human


__all__ = [local, remote]
