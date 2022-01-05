import random
from collections import Counter

from main import play_game, cpu_player, GameState, WORDS, Player


def main():
    stats = Counter()
    for word in random.sample(WORDS, 100):
        winner, _ = play_game(cpu_player, GameState(word), quiet=True)
        stats[winner] += 1

        if winner == Player.WordCzar:
            print(word)

    print(stats)


if __name__ == '__main__':
    main()
