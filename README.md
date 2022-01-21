# The WordleBot
Created by Rachel Lawrence and Alex Reinking


## Setup

Depends on Python 3.10+. Create a virtual environment:

```shell
$ python3.10 -m venv venv
$ . venv/bin/activate
$ python -m pip install -U pip setuptools
$ python -m pip install -r requirements.txt
```

## Running

By default, running `main.py` will put you in an interactive mode where you play the game locally.

```shell
$ python main.py
>>>: apple
apple  🟥🟥🟥🟥🟨
>>>: tinge
apple  🟥🟥🟥🟥🟨
tinge  🟩🟥🟥🟥🟨
>>>: truck
apple  🟥🟥🟥🟥🟨
tinge  🟩🟥🟥🟥🟨
truck  🟩🟥🟥🟥🟥
>>>: tempo
apple  🟥🟥🟥🟥🟨
tinge  🟩🟥🟥🟥🟨
truck  🟩🟥🟥🟥🟥
tempo  🟩🟩🟥🟥🟥
>>>: teeth
apple  🟥🟥🟥🟥🟨
tinge  🟩🟥🟥🟥🟨
truck  🟩🟥🟥🟥🟥
tempo  🟩🟩🟥🟥🟥
teeth  🟩🟩🟨🟨🟥
>>>: teddy
apple  🟥🟥🟥🟥🟨
tinge  🟩🟥🟥🟥🟨
truck  🟩🟥🟥🟥🟥
tempo  🟩🟩🟥🟥🟥
teeth  🟩🟩🟨🟨🟥
teddy  🟩🟩🟩🟩🟩
Guesser won!
```

To solve the online wordle, override the Guesser to be the `cpu` and the Czar to be `remote`:

```shell
$ python main.py --guesser cpu --czar remote
hint for arose: x??xx
arose  🟥🟨🟨🟥🟥
hint for yourt: x*x?*
arose  🟥🟨🟨🟥🟥
yourt  🟥🟩🟥🟨🟩
hint for biros: ?x?*x
arose  🟥🟨🟨🟥🟥
yourt  🟥🟩🟥🟨🟩
biros  🟨🟥🟨🟩🟥
hint for robot: *****
arose  🟥🟨🟨🟥🟥
yourt  🟥🟩🟥🟨🟩
biros  🟨🟥🟨🟩🟥
robot  🟩🟩🟩🟩🟩
Guesser won!
```

Notice that when it asks for a hint for a guess, it expects one character per letter in the word, in the following
format:

* `x` - the letter is incorrect
* `?` - the letter appears in the word, but not in that spot
* `*` - the letter is in the correct spot 
