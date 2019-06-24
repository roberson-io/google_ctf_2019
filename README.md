# Doomed to Repeat It
## Description
Play the classic game Memory. Feel free to download and study the source code.
[https://doomed.web.ctfcompetition.com/](https://doomed.web.ctfcompetition.com/)

## Summary
The task is to complete a game of [Memory (also known as Concentration)](https://en.wikipedia.org/wiki/Concentration_(card_game)) with a set of 56 cards in no more than 60 tries. There are 28 distinct pairs of cards marked 0 through 27. This means that you can flip no more than two pairs of mismatched cards. A weakness in the method for randomizing cards allows collection of game boards that have a high probability of being reused.

## Method for solving
### Approach
1. Collect a large set of boards using the Golang code provided in the challenge attachment. See results in `boards.txt`. See added `NewBoard` function in `modified/game/game.go` and command line argument added to `main` in `modified/main.go`. Command: `go run memory 100000 > boards.txt`
2. Reduce the set of boards to boards that are duplicated. See results in `dupes.txt`. Command: `sort boards.txt | uniq -d > dupes.txt`
3. Create a dictionary of duplicated boards where the key is the first four cards. Flip four cards. If the key for the first four cards is in the dictionary, attempt to solve. Quit if the key is not in the dictionary or if there are any mismatches after flipping the first four cards. See `doomed.py`.  I used Python 3.6.8 and the [websockets](https://pypi.org/project/websockets/) library (version 7.0). You probably want to use a virtualenv:
```
python3 -m venv venv
. venv/bin/activate
pip install websockets
python doomed.py
```
See results.txt for a successful attempt. Flag: `CTF{PastPerf0rmanceIsIndicativeOfFutureResults}`
### Observations
* Of the 100,000 boards I collected (`boards.txt`), 23,438 boards were duplicated (`dupes.txt`). This means that I should have found a duplicate about 1 out of every 4 or 5 attempts when running `doomed.py`. This seemed to be roughly the case.
* The comments in `random/random.go` heavily imply that the randomization is bad, but I went through the approaches below before making a pass through the provided code. 

## Obstacles and approaches that didn't work
### Exploiting JavaScript
The link in the challenge description provides a nice UI in your browser for the game. If you click a card, it flips it over and starts a 10 second countdown until you click another card. It keeps track of turns used and ends if you run out of time or exhaust the cap of 60 attempts.

At first, I thought that it might be possible to exploit the client side to extend the time limit or reveal the board. However, both are handled on the server side.

### Origin header
The source code shows that the application uses WebSockets. The JavaScript source code inspects the protocol to use `ws://` or `wss://` for the WebSocket URI. I started writing a client in Python using the [websockets](https://pypi.org/project/websockets/) library, but I got an HTTP 302 when using `ws://` and an HTTP 403 when using `wss://`. The [Gorilla WebSocket](https://github.com/gorilla/websocket) library used in the Golang server checks that the origin header matches. The Python [websockets](https://pypi.org/project/websockets/) library allows you to set the origin to whatever you want.

### Playing perfectly
The first iteration of `doomed.py` attempted to just keep track of flipped cards and play a perfect game. However, you have to be very lucky to match 28 pairs and only make two mistakes, even if you have a perfect memory.