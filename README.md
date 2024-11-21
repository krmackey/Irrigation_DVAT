# Irrigation Data Visualization and Analysis Tool
### Kirin Mackey

## Quick Start Guide
To explore my current code, first create a `data` folder, containing both files held in the `data` folder[irrigation/data] in this repository

Project Penney is a project designed to simulate Penney's Game, a game played between two players where each player chooses a sequence of three card colors (e.g. Red, Black, Black). Points are awarded to players if their sequence appears when pulling cards sequentially from a well-shuffled deck. Penney's Game is of interest because the probability of winning is not equal; if the second player learns the sequence chosen by the first player, they can follow a rule to optimize their chances of winning. More information can be found in [the Wikipedia page](https://en.wikipedia.org/wiki/Penney%27s_game). 

Note that our simulation runs two variations of Penney's Game, which have different rules: 
1. For version 1, players are scored based on the number of "tricks" they earn. For example, if a player's sequence "Red, Black, Black" appears, the deck is cleared and the player earns 1 point. 
2. For version 2, players are scored based on the number of cards they earn. If a player's sequence "Red, Black, Black" appears, the deck is cleared and the player earns _all_ the cards in the deck. 
