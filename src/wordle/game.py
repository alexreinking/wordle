import random
from typing import Optional

from .types import GameState, WORDS, Player, MAX_GUESSES, Hint, WORDS_SET, WORD_LENGTH


def new_game(word='') -> GameState:
    assert not word or len(word) == WORD_LENGTH
    return GameState(word or random.choice(WORDS))


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


def submit_guess(state: GameState, guess: str) -> GameState:
    assert len(state.guesses) < MAX_GUESSES
    assert guess in WORDS_SET

    return GameState(
        state.solution,
        state.guesses + [guess],
        state.hints + [get_hint_for_guess(guess, state)]
    )


def play_game(player, state: Optional[GameState] = None):
    player = player()

    if state is None:
        state = new_game()

    while get_winner(state) is None:
        hints = None if not state.guesses else (state.guesses, state.hints)

        new_guess = player.send(hints)
        state = submit_guess(state, new_guess)

    return get_winner(state), state