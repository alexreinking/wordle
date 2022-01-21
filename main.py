import click

from wordle import guessers, czars, play_game
from wordle.types import RulesError


@click.command()
@click.option('--guesser',
              default=guessers.human.__name__,
              type=click.Choice([x.__name__ for x in guessers.__all__]))
@click.option('--czar',
              default=czars.local.__name__,
              type=click.Choice([x.__name__ for x in czars.__all__]))
def main(guesser, czar):
    guesser_fn = getattr(guessers, guesser)
    czar_fn = getattr(czars, czar)

    try:
        play_game(guesser_fn(), czar_fn(), interactive=True)
    except RulesError as e:
        click.echo(f'Something went wrong during gameplay: {e}')


if __name__ == '__main__':
    main()
