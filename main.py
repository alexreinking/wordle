import click

import wordle
import wordle.players


@click.command()
@click.option('--player',
              default=wordle.players.human.__name__,
              type=click.Choice([x.__name__ for x in wordle.players.__all__]))
def main(player):
    player_fn = getattr(wordle.players, player)
    winner, state = wordle.play_game(player_fn)
    click.echo(f'{winner.name} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
