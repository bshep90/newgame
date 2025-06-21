# coding: utf-8
"""Simple two-player tactical game on an 8x8 board.
This follows the MVP described in the repository task.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

BOARD_SIZE = 8

# Mapping of unit codes to display emoji and movement type
UNIT_DATA = {
    "CMD": {"symbol": "\U0001F9E0", "move": "one"},      # brain emoji
    "INF": {"symbol": "\U0001FA96", "move": "one_straight"}, # helmet
    "SNP": {"symbol": "\U0001F3AF", "move": "one_or_snipe"}, # direct hit
    "DRN": {"symbol": "\U0001F681", "move": "two"},          # helicopter
    "ENG": {"symbol": "\U0001F9F0", "move": "one"},          # toolbox
    "TNK": {"symbol": "\U0001F6E1", "move": "one_straight"}, # shield
    "AT":  {"symbol": "\U0001F4A5", "move": "one_diag"},     # boom
    "MIN": {"symbol": "\u26A0\uFE0F", "move": "none"},       # warning
}

@dataclass
class Piece:
    code: str      # e.g. "INF"
    owner: int     # 1 or 2
    revealed: bool = True

    @property
    def symbol(self) -> str:
        return UNIT_DATA[self.code]["symbol"]

class GameBoard:
    def __init__(self) -> None:
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.place_initial_units()

    def place_initial_units(self) -> None:
        """Place a mirrored setup for both players."""
        # Player 2 (top)
        self.grid[0][3] = Piece("TNK", 2)
        self.grid[0][4] = Piece("CMD", 2)
        self.grid[0][5] = Piece("AT", 2)
        self.grid[1][2] = Piece("INF", 2)
        self.grid[1][3] = Piece("SNP", 2)
        self.grid[1][4] = Piece("ENG", 2)
        self.grid[1][5] = Piece("DRN", 2)
        self.grid[1][6] = Piece("INF", 2)
        self.grid[2][2] = Piece("MIN", 2)
        self.grid[2][6] = Piece("MIN", 2)

        # Player 1 (bottom)
        self.grid[7][3] = Piece("TNK", 1)
        self.grid[7][4] = Piece("CMD", 1)
        self.grid[7][5] = Piece("AT", 1)
        self.grid[6][2] = Piece("INF", 1)
        self.grid[6][3] = Piece("SNP", 1)
        self.grid[6][4] = Piece("ENG", 1)
        self.grid[6][5] = Piece("DRN", 1)
        self.grid[6][6] = Piece("INF", 1)
        self.grid[5][2] = Piece("MIN", 1)
        self.grid[5][6] = Piece("MIN", 1)

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE

    def display_board(self, highlights: Optional[List[Tuple[int, int]]] = None) -> None:
        highlights = highlights or []
        print("   " + " ".join(str(i) for i in range(BOARD_SIZE)))
        for y in range(BOARD_SIZE):
            row = f"{y} "
            for x in range(BOARD_SIZE):
                if (y, x) in highlights:
                    row += " * "
                else:
                    piece = self.grid[y][x]
                    row += piece.symbol if piece else " . "
                row += " "
            print(row)
        print()

    def get_piece(self, pos: Tuple[int, int]) -> Optional[Piece]:
        y, x = pos
        if not self.in_bounds(y, x):
            return None
        return self.grid[y][x]

    def movement_dirs(self, piece: Piece) -> List[Tuple[int, int]]:
        """Return basic delta positions for a piece move."""
        t = UNIT_DATA[piece.code]["move"]
        if t == "one":
            return [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if not (dy == dx == 0)]
        if t == "one_straight":
            return [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if t == "one_diag":
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if t == "two":
            dirs = []
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    if abs(dy) == 2 or abs(dx) == 2:
                        if not (dy == 0 and dx == 0) and max(abs(dy), abs(dx)) == 2:
                            dirs.append((dy, dx))
            return dirs
        if t == "one_or_snipe":
            dirs = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if not (dy == dx == 0)]
            dirs += [(-2, 0), (2, 0), (0, -2), (0, 2)]
            return dirs
        return []

    def valid_moves(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        piece = self.get_piece(pos)
        if not piece:
            return []
        moves = []
        for dy, dx in self.movement_dirs(piece):
            ny, nx = pos[0] + dy, pos[1] + dx
            if not self.in_bounds(ny, nx):
                continue
            target = self.grid[ny][nx]
            if target and target.owner == piece.owner:
                continue
            # drones cannot capture
            if piece.code == "DRN" and target:
                continue
            # anti-tank only fights tanks
            if piece.code == "AT" and target and target.code != "TNK":
                continue
            moves.append((ny, nx))
        return moves

    def resolve_combat(self, attacker: Piece, defender: Piece) -> str:
        """Return 'attacker', 'defender', or 'both' for tie."""
        if defender.code == attacker.code:
            return "both"
        if defender.code == "MIN":
            return "attacker" if attacker.code == "ENG" else "defender"
        if attacker.code == "MIN":
            return "defender" if defender.code == "ENG" else "attacker"
        if attacker.code == "TNK":
            if defender.code in ("AT", "MIN"):
                return "defender"
            return "attacker"
        if attacker.code == "AT":
            return "attacker" if defender.code == "TNK" else "defender"
        if attacker.code == "DRN":
            return "defender"
        if attacker.code == "ENG" and defender.code in ("MIN", "DRN"):
            return "attacker"
        if attacker.code == "INF" and defender.code == "CMD":
            return "attacker"
        return "attacker"

    def move_piece(self, src: Tuple[int, int], dst: Tuple[int, int]) -> Optional[int]:
        piece = self.get_piece(src)
        if not piece:
            return None
        target = self.get_piece(dst)
        if target:
            outcome = self.resolve_combat(piece, target)
            if outcome == "attacker":
                self.grid[dst[0]][dst[1]] = piece
            elif outcome == "defender":
                if target.code != "MIN":
                    self.grid[dst[0]][dst[1]] = target
                self.grid[src[0]][src[1]] = None
                return None
            else:  # tie
                self.grid[dst[0]][dst[1]] = None
        else:
            self.grid[dst[0]][dst[1]] = piece
        self.grid[src[0]][src[1]] = None

        # victory checks
        if target and target.code == "CMD":
            return piece.owner
        if piece.code == "CMD":
            if piece.owner == 1 and dst[0] == 0:
                return 1
            if piece.owner == 2 and dst[0] == BOARD_SIZE - 1:
                return 2
        return None

    def has_units(self, player: int) -> bool:
        for row in self.grid:
            for cell in row:
                if cell and cell.owner == player and cell.code != "CMD":
                    return True
        return False

class Game:
    def __init__(self) -> None:
        self.board = GameBoard()
        self.turn = 1

    def ask_pos(self, prompt: str) -> Optional[Tuple[int, int]]:
        try:
            coords = input(prompt).split()
            if len(coords) != 2:
                return None
            y, x = int(coords[0]), int(coords[1])
            if not self.board.in_bounds(y, x):
                return None
            return (y, x)
        except ValueError:
            return None

    def run(self) -> None:
        while True:
            self.board.display_board()
            print(f"Player {self.turn}'s move")
            src = self.ask_pos("Select piece (y x): ")
            if not src:
                print("Invalid input")
                continue
            piece = self.board.get_piece(src)
            if not piece or piece.owner != self.turn:
                print("No piece of yours there")
                continue
            moves = self.board.valid_moves(src)
            if not moves:
                print("No valid moves for that piece")
                continue
            self.board.display_board(highlights=moves)
            dst = self.ask_pos("Move to (y x): ")
            if not dst or dst not in moves:
                print("Invalid destination")
                continue
            winner = self.board.move_piece(src, dst)
            if winner:
                self.board.display_board()
                print(f"Player {winner} wins!")
                break
            opponent = 2 if self.turn == 1 else 1
            if not self.board.has_units(opponent):
                self.board.display_board()
                print(f"Player {self.turn} wins by surrender!")
                break
            self.turn = opponent

if __name__ == "__main__":
    Game().run()
