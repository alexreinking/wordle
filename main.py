import click

from wordle import human_player, play_game


def main():
    winner, state = play_game(human_player)
    click.echo(f'{winner.name} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
