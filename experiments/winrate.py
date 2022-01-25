import random
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import click

from wordle import play_game, guessers, czars
from wordle.game import WORDS
from wordle.types import Player


def print_bad_words(bad_words):
    for word, state in bad_words.items():
        state.render()
        click.echo(f'Answer: {word}\n')


def run_cpu_game(word):
    return word, play_game(guessers.optimal(), czars.local(word))


def main():
    click.echo('Starting...')

    stats = Counter()
    bad_words = {}

    start = time.time()

    with ProcessPoolExecutor() as pool:
        for word, (winner, end_state) in pool.map(run_cpu_game, random.sample(WORDS, 10)):
            stats[winner] += 1
            if winner == Player.WordCzar:
                bad_words[word] = end_state

    end = time.time()
    click.echo(end - start)

    click.echo(stats)

    print_bad_words(bad_words)


if __name__ == '__main__':
    main()
