import click

import wordle
import wordle.czars
import wordle.guessers


@click.command()
@click.option('--guesser',
              default=wordle.guessers.human.__name__,
              type=click.Choice([x.__name__ for x in wordle.guessers.__all__]))
@click.option('--czar',
              default=wordle.czars.local.__name__,
              type=click.Choice([x.__name__ for x in wordle.czars.__all__]))
def main(guesser, czar):
    guesser_fn = getattr(wordle.guessers, guesser)
    czar_fn = getattr(wordle.czars, czar)

    wordle.play_game(guesser_fn(), czar_fn(), interactive=True)


if __name__ == '__main__':
    main()
