from collections import Counter

import click

from wordle import play_game, cpu_player, new_game, WORDS, Player


def main():
    click.echo('Starting...')

    stats = Counter()
    with click.progressbar(WORDS) as bar:
        for word in bar:
            winner, _ = play_game(cpu_player, new_game(word))
            stats[winner] += 1

            if winner == Player.WordCzar:
                click.echo(word)

    click.echo(stats)


if __name__ == '__main__':
    main()
