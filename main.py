import random
from collections import Counter
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
        yield click.prompt('>>>', value_proc=validate_word_input)


def cpu_player() -> str:
    position_mask = [1] * WORD_LENGTH
    position_guesses = [set() for _ in range(WORD_LENGTH)]
    all_letter_guesses = set()

    def get_dist(words):
        normalizing_factor = len(words) * WORD_LENGTH

        dict_histogram = Counter()
        for word in words:
            for i, letter in enumerate(word):
                dict_histogram[letter] += 1 * position_mask[i]

        for k in dict_histogram:
            dict_histogram[k] /= normalizing_factor

        return dict_histogram

    def get_best_word(words):
        def score_word(w):
            score = 0
            seen = set()
            for i, let in enumerate(w):
                if let in seen:
                    continue
                seen.add(let)
                if position_mask[i]:
                    if let not in position_guesses[i]:
                        score += dist[let]
                else:
                    if let not in all_letter_guesses:
                        score += dist[let]
            return score

        return max(words, key=score_word)

    possible_words = WORDS
    dist = get_dist(possible_words)
    current_guess = get_best_word(possible_words)

    while True:
        guesses, hints = yield current_guess
        assert guesses[-1] == current_guess

        # Record which letters we have guessed in which positions
        for let, guess_set in zip(current_guess, position_guesses):
            guess_set.add(let)
            all_letter_guesses.add(let)

        for i, hint in enumerate(hints[-1]):
            if hint == Hint.Correct:
                position_mask[i] = 0

        # Update set of possible words
        def word_is_compatible_with_hint(word: str):
            for pos, (word_let, guess_let, hint) in enumerate(zip(word, current_guess, hints[-1])):
                if hint == Hint.Correct:
                    if word_let != guess_let:
                        return False
                elif hint == Hint.CorrectLetter:
                    if guess_let == word_let:
                        # Would have been Hint.Correct otherwise.
                        return False
                    if guess_let not in word:
                        # The guessed letter must appear somewhere in the word.
                        return False
                    if guess_let not in (word[:pos] + word[pos + 1:]):
                        # Rule out the word when the correct letter cannot
                        # be placed elsewhere in this word. For instance:
                        #  abcde  (xx?xx)
                        # would eliminate "fgchi" because there's no "c"
                        # in a non-matching position.
                        return False
                elif hint == Hint.Incorrect:
                    if guess_let in word:
                        return False
            return True

        possible_words = [word for word in possible_words
                          if word_is_compatible_with_hint(word)]
        dist = get_dist(possible_words)

        if len(possible_words) == 1:
            yield possible_words[0]

        if len(guesses) < MAX_GUESSES - 1:
            current_guess = get_best_word(WORDS)
        else:
            current_guess = get_best_word(possible_words)


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


def main():
    # state = new_game()
    state = GameState('gecks')
    winner, state = play_game(cpu_player, state)
    click.echo(f'{winner} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
