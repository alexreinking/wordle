from typing import Optional, Tuple

from .types import GameState, Player, MAX_GUESSES, Hint


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


def play_game(player, czar) -> Tuple[Player, GameState]:
    state = GameState()
    player = player()

    while get_winner(state) is None:
        guess = player.send(state if state.guesses else None)
        state = GameState(
            guesses=state.guesses + [guess],
            hints=state.hints + [czar(guess)],
        )

    return get_winner(state), state
