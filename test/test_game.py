from wordle import czars, play_game
from wordle.game import MAX_GUESSES
from wordle.types import Player


def _constant_player(word):
    while True:
        yield word


def _list_player(words):
    while True:
        for word in words:
            yield word


def test_wrong_answer():
    winner, state = play_game(_constant_player('apple'), czars.local('peels'))
    assert winner == Player.WordCzar
    assert len(state.guesses) == MAX_GUESSES


def test_correct_answer_first():
    winner, state = play_game(_constant_player('fruit'), czars.local('fruit'))
    assert winner == Player.Guesser
    assert len(state.guesses) == 1


def test_correct_answer_last():
    bad = 'apple'
    good = 'fruit'

    guesses = [bad] * (MAX_GUESSES - 1) + [good]
    winner, state = play_game(_list_player(guesses), czars.local(good))

    assert winner == Player.Guesser
    assert len(state.guesses) == MAX_GUESSES


def test_correct_answer_middle():
    bad = 'apple'
    good = 'fruit'

    assert MAX_GUESSES > 1

    guesses = [bad] * (MAX_GUESSES - 2) + [good]
    winner, state = play_game(_list_player(guesses), czars.local(good))

    assert winner == Player.Guesser
    assert len(state.guesses) == MAX_GUESSES - 1
