import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import click

MAX_GUESSES = 6
WORD_LENGTH = 5

WORDS_SET = set(word.lower() for word in Path('./dictionary.csv').read_text().split('\n')
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


def new_game() -> GameState:
    return GameState(random.choice(WORDS))


def get_winner(state: GameState) -> Optional[Player]:
    """
    >>> get_winner(GameState('w', ['a', 'b', 'c', 'd', 'e', 'f']))
    <Player.WordCzar: 1>
    >>> get_winner(GameState('w', ['a', 'b', 'c', 'd', 'e', 'w']))
    <Player.Guesser: 0>
    >>> get_winner(GameState('w', ['a', 'b', 'c', 'd', 'e', 'f', 'w']))
    <Player.WordCzar: 1>
    >>> get_winner(GameState('w', ['a', 'b', 'c', 'd', 'e']))
    >>> get_winner(GameState('w', ['w']))
    <Player.Guesser: 0>
    >>> get_winner(GameState('w', []))
    """
    if len(state.guesses) == 0:
        return None
    if len(state.guesses) > MAX_GUESSES:
        return Player.WordCzar
    if state.guesses[-1] == state.solution:
        return Player.Guesser
    if len(state.guesses) == MAX_GUESSES:
        return Player.WordCzar
    return None


def get_hint(state: GameState) -> [Hint]:
    """
    >>> get_hint(GameState('apple', ['aaper']))
    [<Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Incorrect: 2>]
    """
    assert len(state.guesses)

    guess = state.guesses[-1]
    assert len(guess) == len(state.solution)

    return get_hint_for_guess(guess, state)


def get_hint_for_guess(guess: str, state: GameState) -> [Hint]:
    """
    >>> get_hint_for_guess('aaper', GameState('apple'))
    [<Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Correct: 0>, <Hint.CorrectLetter: 1>, <Hint.Incorrect: 2>]
    """
    hints = []
    for guess_ch, sol_ch in zip(guess, state.solution):
        if guess_ch == sol_ch:
            hints.append(Hint.Correct)
        elif guess_ch in state.solution:
            hints.append(Hint.CorrectLetter)
        else:
            hints.append(Hint.Incorrect)
    return hints


def display_game(state: GameState):
    """
    >>> display_game(GameState('apple', ['perot', 'aaper']))
    perot
    ??xxx
    -----
    aaper
    *?*?x
    """
    separator = '-' * WORD_LENGTH
    first = True
    for guess, hint in zip(state.guesses, state.hints):
        if not first:
            print(separator)
        print(f'{guess}\n{"".join(map(str, hint))}')
        first = False


class WordleError(Exception):
    pass


def submit_guess(state: GameState, guess: str) -> GameState:
    assert len(state.guesses) < MAX_GUESSES
    assert guess in WORDS_SET

    return GameState(
        state.solution,
        state.guesses + [guess],
        state.hints + [get_hint_for_guess(guess, state)]
    )


def validate_word_input(word: str):
    word = word.lower()
    if word not in WORDS_SET:
        raise click.UsageError(f'{word} is not a valid word!')
    return word


def human_player() -> str:
    while True:
        guesses, hints = yield click.prompt('>>>', value_proc=validate_word_input)


def play_game(player):
    game = new_game()
    player = player()

    print(f'DEBUG: word is "{game.solution}"')

    while get_winner(game) is None:
        display_game(game)

        hints = None if not game.guesses else (game.guesses, game.hints)

        new_guess = player.send(hints)
        game = submit_guess(game, new_guess)

    display_game(game)
    winner = get_winner(game)
    print(f'{winner} won! Word was "{game.solution}"')


if __name__ == '__main__':
    play_game(human_player)
