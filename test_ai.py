from collections import Counter

import click

from main import play_game, cpu_player, GameState, WORDS, Player


def main():
    click.echo('Starting...')

    stats = Counter()
    with click.progressbar(WORDS) as bar:
        for word in bar:
            winner, _ = play_game(cpu_player, GameState(word), quiet=True)
            stats[winner] += 1

            if winner == Player.WordCzar:
                click.echo(word)

    click.echo(stats)


if __name__ == '__main__':
    main()
