# Iterated_PD

## Summary
This project is a simulation for strategy evolution/optimization using a genetic algorithm for the Iterated Prisoner's Dilemma game. The Iterated Prisoner's Dilemma is the repeated version of the standard Prisoner's Dilemma, a famous 2-player symmetric game where each player has the option to "Defect" (D) and "Cooperate" (C). The game has the following payoff matrix:

|                         | Player 2 Cooperates | Player 2 Defects |
|-------------------------|---------------------|------------------|
| Player 1 Cooperates     |   **3, 3**          |  **-1, 5**       |
| Player 1 Defects        |   **5, -1**         |  **0, 0**        |

There are 2 strict pure-strategy nash equilibria in this game: (Play C, Play C) and (Play D, Play D). The strategy profile (used in a less rigorous manner in this case) is encoded in a length L base-N string, where N is the number of base strategies available in the repeated game and L is the number of times the repeated game is played. Each character of the base-N string represents the base strategy that the agent will play at that time index. The history of moves and the payoffs from both players are available at every time step. The current simulation supports the following base strategies:
- Unconditional Cooperator (Cu)
- Unconditional Defector (Du)
- Random 
- Probability _p_ Cooperator (Cp)
- Tit-for-Tat (TFT)
- Tit-for-Two-Tats (TFTT)
- Prober 

The specifications of these strategies can be found at: https://plato.stanford.edu/entries/prisoner-dilemma/strategy-table.html.

