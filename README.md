# NewGame Tactical Demo

This repository contains a simple two-player tactical board game implemented in `tactical_game.py`.

## Running the Game

The game now uses a simple Tkinter GUI. Run it with:

```bash
python tactical_game.py
```

A window will appear showing the 8×8 board using emoji for each unit. Click a
piece to highlight its valid moves, then click a highlighted square to move. The
game ends when a command unit is eliminated or reaches the opposite back row.

Win by eliminating the opponent's command unit or moving your own command unit
to the far side of the board.
