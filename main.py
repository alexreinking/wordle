import click

from wordle import human_player, play_game, cpu_player
from wordle.players import optimal_player


def main():
    winner, state = play_game(optimal_player)
    click.echo(f'{winner.name} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
