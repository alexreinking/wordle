import pytest

from wordle import guessers, play_game, czars
from wordle.game import WORD_LENGTH
from wordle.types import RulesError, Hint, Player


def _lying_czar():
    while True:
        yield [Hint.Incorrect] * WORD_LENGTH


def test_can_solve_robot():
    winner, _ = play_game(guessers.cpu(), czars.local('robot'))
    assert winner == Player.Guesser


def test_detects_lying():
    with pytest.raises(RulesError, match='No possible solution!'):
        play_game(guessers.cpu(), _lying_czar())
