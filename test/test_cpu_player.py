import random
from collections import Counter

import click

from wordle import play_game, guessers, czars
from wordle.game import WORDS
from wordle.types import Player


def main():
    click.echo('Starting...')

    corpus = random.sample(WORDS, 1000)
    stats = Counter()
    bad_words = {}

    with click.progressbar(corpus) as bar:
        for word in bar:
            winner, end_state = play_game(guessers.cpu(), czars.local(word))

            stats[winner] += 1
            if winner == Player.WordCzar:
                bad_words[word] = end_state

    click.echo(stats)

    for word, state in bad_words.items():
        state.render()
        click.echo(f'Answer: {word}\n')


if __name__ == '__main__':
    main()
