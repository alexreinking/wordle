import click

import wordle
import wordle.czars
import wordle.players


@click.command()
@click.option('--player',
              default=wordle.players.human.__name__,
              type=click.Choice([x.__name__ for x in wordle.players.__all__]))
@click.option('--czar',
              default=wordle.czars.local.__name__,
              type=click.Choice([x.__name__ for x in wordle.czars.__all__]))
def main(player, czar):
    player_fn = getattr(wordle.players, player)
    czar_fn = getattr(wordle.czars, czar)()
    wordle.play_game(player_fn, czar_fn)


if __name__ == '__main__':
    main()
