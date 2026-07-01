# Iterated Prisoner's Dilemma

## Summary

This project simulates strategy evolution using a genetic algorithm applied to the Iterated Prisoner's Dilemma (IPD). In the IPD, two players repeatedly choose to cooperate (C) or defect (D), with payoffs determined by the standard matrix:

|                     | Player 2 Cooperates | Player 2 Defects |
|---------------------|---------------------|------------------|
| Player 1 Cooperates | 3, 3                | -1, 5            |
| Player 1 Defects    | 5, -1               | 0, 0             |

Each agent's behaviour is encoded as a fixed-length gene string. Every character maps to one of the supported base strategies and determines the agent's move at that time step. Agents compete in round-robin tournaments, and top performers reproduce via genetic crossover — mixing gene strings to produce offspring with new strategy combinations. A small random mutation rate is applied during crossover.

## Strategies

| Name   | Gene | Description |
|--------|------|-------------|
| Cu     | `a`  | Always cooperate |
| Du     | `b`  | Always defect |
| Random | `c`  | Cooperate or defect with equal probability |
| Cp     | `d`  | Cooperate with probability 0.7 |
| TFT    | `e`  | Tit-for-Tat: cooperate first, then copy opponent's last move |
| TFTT   | `f`  | Tit-for-Two-Tats: only defect after two consecutive opponent defections |
| Prober | `g`  | Open D, C, C — exploit if opponent didn't retaliate, else TFT |

Strategy specs: https://plato.stanford.edu/entries/prisoner-dilemma/strategy-table.html

## Project Structure

```
.
├── simulation.py           # Entry point
├── requirements.txt
├── tests/
│   └── player_test.py      # Unit tests
└── lib/
    ├── config.py           # Shared strategy constants
    ├── player.py           # Player agent and crossover logic
    ├── prisoner_dilemma.py # Simulation engine
    └── tree.py             # Lineage tree data structure
```

## Installation

```bash
brew install pytest
pip install matplotlib
```

Or with pip in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 simulation.py
```

Runs a preconfigured simulation with 4 agents per strategy, gene length 20, over 7 epochs with a 33% reproduction rate. A `players.db` SQLite database is written with all players.

By default no plot is shown. Pass `--plot` to generate a two-panel chart of population count and gene percentage over time — it will be saved as `simulation_plot.png` and opened automatically in Preview:

```bash
python3 simulation.py --plot
```

To adjust parameters, edit `run_sim()` in `simulation.py`:

```python
sim = prisoner_dilemma.Simulation(
    pool_size=4,      # agents per strategy
    gene_length=20,   # moves per game
    totalrounds=7,    # epochs
    predetermined=True
)
sim.sim_configuration_1(0.33)  # top 33% reproduce each round
```

## Running Tests

```bash
pytest tests/ -v
```

## How It Works

1. An initial population is created with `pool_size` agents per strategy.
2. Each epoch, every agent plays every other (round-robin) over `gene_length` moves.
3. The top `rp` fraction by score form a mate pool.
4. Random pairs reproduce via two-point crossover, producing two offspring each (with optional point mutation).
5. Offspring are appended to the population — no agents are eliminated (strictly growing).
6. Gene frequency statistics are tracked each epoch and plotted at the end.
7. All players are persisted to `players.db` for post-run analysis.
