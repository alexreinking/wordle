import click

import wordle


def main():
    state = wordle.new_game()
    winner, state = wordle.play_game(wordle.cpu_player, state)
    click.echo(f'{winner} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
