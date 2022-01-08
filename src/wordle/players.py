from collections import Counter

import click

from .types import WORDS, WORD_LENGTH, WORDS_SET, Hint, MAX_GUESSES


def human_player() -> str:
    def validate_word_input(word: str):
        word = word.lower()
        if word not in WORDS_SET:
            raise click.UsageError(f'{word} is not a valid word!')
        return word

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
