import random
from collections import defaultdict

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
    for guess, hint in zip(guesses, hints):
        for pos in range(WORD_LENGTH):
            hint_let = guess[pos]
            match hint[pos]:
                case Hint.Correct:
                    if hint_let != word[pos]:
                        return False
                case Hint.CorrectLetter:
                    if (
                            # Would have been Hint.Correct otherwise.
                            hint_let == word[pos] or
                            # The guessed letter must appear somewhere in the word.
                            hint_let not in word or
                            # Rule out the word when the correct letter cannot
                            # be placed elsewhere in this word. For instance:
                            #  abcde  (xx?xx)
                            # would eliminate "fgchi" because there's no "c"
                            # in a non-matching position.
                            hint_let not in (word[:pos] + word[pos + 1:])
                    ):
                        return False
                case Hint.Incorrect:
                    if hint_let in word:
                        return False
    return True


def cpu() -> Guesser:
    position_mask = [1] * WORD_LENGTH
    position_guesses = [[1] * 26 for _ in range(WORD_LENGTH)]
    all_letter_guesses = [1] * 26

    def get_dist(words):
        assert words

        normalizing_factor = len(words) * WORD_LENGTH
        a_off = ord('a')
        dict_histogram = [0] * 26
        for word in words:
            for let, p in zip(word, position_mask):
                dict_histogram[ord(let) - a_off] += p

        for k in range(26):
            dict_histogram[k] /= normalizing_factor

        return dict_histogram

    if (dist := getattr(cpu, 'dist', None)) is None:
        dist = cpu.dist = get_dist(WORDS)

    def score_word(w):
        let_score = [0] * 26
        let_count = [0] * 26

        a_off = ord('a')
        for let, pos_m, pos_g in zip(w, position_mask, position_guesses):
            let_i = ord(let) - a_off
            let_score[let_i] += dist[let_i] * (  # Weight by frequency in distribution of possibilities
                    pos_m * pos_g[let_i]  # Position solution unknown and letter+pos not yet guessed OR
                    + (1 - pos_m) * all_letter_guesses[let_i]  # Position soln known but letter never guessed.
            )
            let_count[let_i] += 1

        return sum(let_score[i] / max(let_count[i], 1) for i in range(26))

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

        if not possible_words:
            raise RulesError('No possible solution!')

        dist = get_dist(possible_words)

        if len(possible_words) == 1:
            yield possible_words[0]

        if len(state.guesses) < MAX_GUESSES - 1:
            current_guess = get_best_word(WORDS)
        else:
            current_guess = get_best_word(possible_words)


def optimal() -> Guesser:
    guessable_words = WORDS
    possible_words = WORDS
    guesses, hints = [], []

    absent_letters = set()

    def get_guess() -> str:
        if len(possible_words) == 1:
            return possible_words[0]

        scores = defaultdict(int)

        for guess in random.sample(guessable_words, min(len(guessable_words), 1000)):
            for solution in possible_words:
                scores[guess] = max(
                    scores[guess],
                    sum(_word_is_compatible_with_hints(
                        word,
                        guesses + [guess],
                        hints + [Hint.for_guess(guess, solution)]
                    ) for word in possible_words)
                )

        return min(scores.keys(), key=lambda w: scores[w])

    if (current_guess := getattr(optimal, 'current_guess', None)) is None:
        current_guess = optimal.current_guess = random.choice(guessable_words)

    while True:
        print(f'Guessing {current_guess}')
        state = yield current_guess
        guesses, hints = state.guesses, state.hints

        absent_letters.update(w for w, h in zip(guesses[-1], hints[-1]) if h == Hint.Incorrect)

        # TODO: if a word has only known letters and known non-letters, then exclude it, too
        guessable_words = [word for word in guessable_words
                           if any(letter not in absent_letters for letter in word)]

        possible_words = [word for word in possible_words
                          if _word_is_compatible_with_hints(word, guesses, hints)]

        print(len(guessable_words))
        print(len(possible_words))

        current_guess = get_guess()


__all__ = [human, cpu, optimal]
