import click

import wordle
import wordle.players


@click.command()
@click.option('--player', default='human', type=click.Choice(['human', 'cpu', 'optimal']))
def main(player):
    player_fn = getattr(wordle.players, f'{player}_player')
    winner, state = wordle.play_game(player_fn)
    click.echo(f'{winner.name} won in {len(state.guesses)} moves! Word was "{state.solution}"')


if __name__ == '__main__':
    main()
