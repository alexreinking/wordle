import pytest

from wordle import guessers, play_game, czars
from wordle.game import WORD_LENGTH
from wordle.types import RulesError, Hint, Player


def _lying_czar():
    while True:
        yield [Hint.Incorrect] * WORD_LENGTH


test_words = [
    'robot',
    'sugar',
    'doxed',
]


@pytest.mark.parametrize('word', test_words)
def test_can_solve_words(word):
    winner, state = play_game(guessers.cpu(), czars.local(word))
    state.render()
    assert winner == Player.Guesser


@pytest.mark.skip('slow')
@pytest.mark.parametrize('word', test_words)
def test_optimal_solves_words(word):
    winner, state = play_game(guessers.optimal(), czars.local(word))
    state.render()
    assert winner == Player.Guesser


def test_detects_lying():
    with pytest.raises(RulesError, match='No possible solution!'):
        play_game(guessers.cpu(), _lying_czar())
