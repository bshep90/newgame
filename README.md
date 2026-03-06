# NewGame Tactical Demo

This repository now contains two Python command-line projects:

1. A simple two-player tactical board game in `tactical_game.py`.
2. An educational toy operating system simulator in `os_sim.py`.

## Running the Tactical Game

```bash
python tactical_game.py
```

Players take turns entering coordinates for the piece they wish to move and the destination square. The board is an 8×8 grid. Each unit is represented by an emoji.

Win by eliminating the opponent's command unit or moving your own command unit to the far side of the board.

## Running NanoOS (toy OS simulator)

```bash
python os_sim.py
```

`os_sim.py` simulates a tiny shell-based OS with:
- users (`adduser`, `login`, `whoami`)
- virtual files (`ls`, `cat`, `write`)
- processes (`spawn`, `ps`, `tick`, `kill`)
- memory accounting (`meminfo`)

Use `help` inside the simulator to see all commands, and `shutdown` to exit.
