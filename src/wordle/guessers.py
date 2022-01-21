import random
from collections import Counter

import click

from .game import WORDS, WORD_LENGTH, WORDS_SET, MAX_GUESSES
from .types import Hint, Guesser, RulesError


def _validate_word_input(word: str):
    word = word.lower()
    if word not in WORDS_SET:
        raise click.UsageError(f'{word} is not a valid word!')
    return word


def human() -> Guesser:
    while True:
        yield click.prompt('>>>', value_proc=_validate_word_input)


def _word_is_compatible_with_hints(word: str, guesses: [str], hints: [[Hint]]):
    for guess, hint in zip(reversed(guesses), reversed(hints)):
        for pos, (word_let, guess_let, hint_let) in enumerate(zip(word, guess, hint)):
            if hint_let == Hint.Correct:
                if word_let != guess_let:
                    return False
            elif hint_let == Hint.CorrectLetter:
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
            elif hint_let == Hint.Incorrect:
                if guess_let in word:
                    return False
    return True


def cpu() -> Guesser:
    position_mask = [1] * WORD_LENGTH
    position_guesses = [[1] * 26 for _ in range(WORD_LENGTH)]
    all_letter_guesses = [1] * 26

    def get_dist(words):
        normalizing_factor = len(words) * WORD_LENGTH

        dict_histogram = Counter()
        for word in words:
            for i, let in enumerate(word):
                dict_histogram[let] += 1 * position_mask[i]

        for k in dict_histogram:
            dict_histogram[k] /= normalizing_factor

        return dict_histogram

    if (dist := getattr(cpu, 'dist', None)) is None:
        dist = cpu.dist = get_dist(WORDS)

    def score_word(w):
        score = 0
        seen = [1] * 26
        a_off = ord('a')
        for let, pos_m, pos_g in zip(w, position_mask, position_guesses):
            let_i = ord(let) - a_off
            score += seen[let_i] * dist[let] * (
                    pos_m * pos_g[let_i]
                    + (1 - pos_m) * all_letter_guesses[let_i]
            )
            seen[let_i] = 0

        return score

    def get_best_word(words):
        return max(words, key=score_word)

    if (current_guess := getattr(cpu, 'initial_guess', None)) is None:
        current_guess = cpu.initial_guess = get_best_word(WORDS)

    possible_words = WORDS

    while True:
        state = yield current_guess
        assert state.guesses[-1] == current_guess

        # Record which letters we have guessed in which positions
        for let, guess_set in zip(current_guess, position_guesses):
            guess_set[ord(let) - ord('a')] = 0
            all_letter_guesses[ord(let) - ord('a')] = 0

        for i, hint in enumerate(state.hints[-1]):
            if hint == Hint.Correct:
                position_mask[i] = 0

        possible_words = [word for word in possible_words
                          if _word_is_compatible_with_hints(word, state.guesses, state.hints)]
        dist = get_dist(possible_words)

        if not possible_words:
            raise RulesError('No possible solution!')

        if len(possible_words) == 1:
            yield possible_words[0]

        if len(state.guesses) < MAX_GUESSES - 1:
            current_guess = get_best_word(WORDS)
        else:
            current_guess = get_best_word(possible_words)


def optimal() -> Guesser:
    possible_words = WORDS
    guesses, hints = [], []

    def get_guess() -> str:
        if len(possible_words) == 1:
            return possible_words[0]

        sample_size = 128
        inner_sample_size = min(len(possible_words), sample_size)

        best = float('inf'), ''
        for guess in random.sample(WORDS, sample_size):
            score = 0
            for solution in random.sample(possible_words, inner_sample_size):
                for alternate in random.sample(possible_words, inner_sample_size):
                    score += _word_is_compatible_with_hints(
                        alternate,
                        guesses + [guess],
                        hints + [Hint.for_guess(guess, solution)]
                    )
            score = score / inner_sample_size
            best = min(best, (score, guess))
        return best[1]

    click.echo(f'We start with {len(possible_words)} possible words.')
    while True:
        current_guess = get_guess()
        click.echo(f'Guessing "{current_guess}"...')
        guesses, hints = yield current_guess
        possible_words = [word for word in possible_words
                          if _word_is_compatible_with_hints(word, guesses, hints)]
        click.echo(f'There are now {len(possible_words)} possible words.')


__all__ = [human, cpu, optimal]
