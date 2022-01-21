from pathlib import Path
from typing import Optional, Tuple

from .types import GameState, Player, Hint

MAX_GUESSES = 6
WORD_LENGTH = 5

SCRIPT_PATH = Path(__file__).parent
DICT_PATH = SCRIPT_PATH.parent.parent / 'dictionary.txt'

WORDS_SET = set(word.lower() for word in DICT_PATH.read_text().split('\n')
                if len(word) == WORD_LENGTH)
WORDS = list(sorted(WORDS_SET))


def get_winner(state: GameState) -> Optional[Player]:
    if len(state.guesses) == 0:
        return None
    if len(state.guesses) > MAX_GUESSES:
        return Player.WordCzar
    if all(h == Hint.Correct for h in state.hints[-1]):
        return Player.Guesser
    if len(state.guesses) == MAX_GUESSES:
        return Player.WordCzar
    return None


def play_game(player, czar, interactive=False) -> Tuple[Player, GameState]:
    state = GameState()

    czar.send(None)
    guess = player.send(None)

    while True:
        hint = czar.send(guess)

        state = GameState(
            guesses=state.guesses + [guess],
            hints=state.hints + [hint],
        )

        if get_winner(state) is not None:
            break

        if interactive:
            state.render()

        guess = player.send(state)

    winner = get_winner(state)

    if interactive:
        state.render()
        print(f'{winner.name} won!')

    return winner, state
