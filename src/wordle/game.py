import random
from typing import Optional

import click

from .types import GameState, WORDS, Player, MAX_GUESSES, Hint, WORDS_SET


def new_game() -> GameState:
    return GameState(random.choice(WORDS))


def fill_hints(state: GameState) -> GameState:
    return GameState(
        state.solution,
        state.guesses,
        [get_hint_for_guess(guess, state)
         for guess in state.guesses]
    )


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
    >>> state = GameState('apple', ['perot', 'aaper'])
    >>> state = fill_hints(state)
    >>> display_game(state)
    perot  ??xxx
    aaper  *?*?x
    """

    color_map = {
        Hint.Correct: 'green',
        Hint.CorrectLetter: 'yellow',
        Hint.Incorrect: 'red',
    }

    for guess, hint in zip(state.guesses, state.hints):
        colored_guess = ''.join(click.style(letter, fg=color_map[h])
                                for letter, h in zip(guess, hint))
        output = f'{colored_guess}  {"".join(map(str, hint))}'
        click.echo(output)


def submit_guess(state: GameState, guess: str) -> GameState:
    assert len(state.guesses) < MAX_GUESSES
    assert guess in WORDS_SET

    return GameState(
        state.solution,
        state.guesses + [guess],
        state.hints + [get_hint_for_guess(guess, state)]
    )


def play_game(player, state: GameState, *, quiet=False):
    player = player()

    while get_winner(state) is None:
        if not quiet:
            display_game(state)

        hints = None if not state.guesses else (state.guesses, state.hints)

        new_guess = player.send(hints)
        state = submit_guess(state, new_guess)

    if not quiet:
        display_game(state)
    return get_winner(state), state
