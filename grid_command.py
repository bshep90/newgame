diff --git a//dev/null b/grid_command.py
index 0000000000000000000000000000000000000000..749e0652285756674cdfaa2b74e8297db8a09e57 100644
--- a//dev/null
+++ b/grid_command.py
@@ -0,0 +1,207 @@
+import copy
+from dataclasses import dataclass
+from typing import List, Optional, Tuple
+
+BOARD_SIZE = 8
+
+@dataclass
+class Piece:
+    player: int
+    kind: str  # CMD, INF, SNP, DRN, ENG, TNK, AT, MIN
+
+ABBREV = {
+    'CMD': 'C',
+    'INF': 'I',
+    'SNP': 'S',
+    'DRN': 'D',
+    'ENG': 'E',
+    'TNK': 'T',
+    'AT': 'A',
+    'MIN': 'M',
+}
+
+# Initial board setup for two players
+# Player 1 starts at bottom, Player 2 at top
+
+def create_board() -> List[List[Optional[Piece]]]:
+    board: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
+
+    # Player 2 setup (top)
+    board[0][3] = Piece(2, 'TNK')
+    board[0][4] = Piece(2, 'CMD')
+    board[0][5] = Piece(2, 'AT')
+    board[1][2] = Piece(2, 'INF')
+    board[1][3] = Piece(2, 'SNP')
+    board[1][4] = Piece(2, 'ENG')
+    board[1][5] = Piece(2, 'DRN')
+    board[1][6] = Piece(2, 'INF')
+    board[2][2] = Piece(2, 'MIN')
+    board[2][6] = Piece(2, 'MIN')
+
+    # Player 1 setup (bottom)
+    board[7][3] = Piece(1, 'TNK')
+    board[7][4] = Piece(1, 'CMD')
+    board[7][5] = Piece(1, 'AT')
+    board[6][2] = Piece(1, 'INF')
+    board[6][3] = Piece(1, 'SNP')
+    board[6][4] = Piece(1, 'ENG')
+    board[6][5] = Piece(1, 'DRN')
+    board[6][6] = Piece(1, 'INF')
+    board[5][2] = Piece(1, 'MIN')
+    board[5][6] = Piece(1, 'MIN')
+    return board
+
+def in_bounds(y: int, x: int) -> bool:
+    return 0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE
+
+class Game:
+    def __init__(self):
+        self.board = create_board()
+        self.turn = 1
+
+    def display(self, highlights: Optional[List[Tuple[int,int]]] = None):
+        highlights = highlights or []
+        print('   ' + ' '.join(str(i) for i in range(BOARD_SIZE)))
+        for y in range(BOARD_SIZE):
+            row_str = f"{y} "
+            for x in range(BOARD_SIZE):
+                cell = self.board[y][x]
+                if (y, x) in highlights:
+                    row_str += ' * '
+                elif cell is None:
+                    row_str += ' . '
+                else:
+                    row_str += f"{cell.player}{ABBREV[cell.kind]}"
+                row_str += ' '
+            print(row_str)
+        print()
+
+    def get_piece(self, pos: Tuple[int,int]) -> Optional[Piece]:
+        y,x = pos
+        if not in_bounds(y,x):
+            return None
+        return self.board[y][x]
+
+    def valid_moves(self, pos: Tuple[int,int]) -> List[Tuple[int,int]]:
+        y,x = pos
+        piece = self.get_piece(pos)
+        if not piece:
+            return []
+        moves = []
+        dirs = []
+        forward = -1 if piece.player == 1 else 1
+        if piece.kind == 'CMD' or piece.kind == 'SNP' or piece.kind == 'ENG':
+            dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
+        elif piece.kind == 'INF':
+            dirs = [(forward,0),(0,-1),(0,1)]
+        elif piece.kind == 'DRN':
+            dirs = [(2,0),(-2,0),(0,2),(0,-2),(2,2),(2,-2),(-2,2),(-2,-2)]
+        elif piece.kind == 'TNK':
+            dirs = [(forward,0),(0,-1),(0,1)]
+        elif piece.kind == 'AT':
+            dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]
+        elif piece.kind == 'MIN':
+            return []
+        for dy,dx in dirs:
+            ny,nx = y+dy,x+dx
+            if not in_bounds(ny,nx):
+                continue
+            target = self.board[ny][nx]
+            if target and target.player == piece.player:
+                continue
+            # drone cannot move onto enemy unit
+            if piece.kind == 'DRN' and target:
+                continue
+            # anti-tank only attacks tanks
+            if piece.kind == 'AT' and target and target.kind != 'TNK':
+                continue
+            moves.append((ny,nx))
+        return moves
+
+    def combat_result(self, attacker: Piece, defender: Piece) -> str:
+        # returns 'attacker', 'defender'
+        if defender.kind == 'MIN':
+            return 'attacker' if attacker.kind == 'ENG' else 'defender'
+        if attacker.kind == 'TNK':
+            if defender.kind in ['AT','MIN']:
+                return 'defender'
+            return 'attacker'
+        if attacker.kind == 'AT':
+            return 'attacker' if defender.kind == 'TNK' else 'defender'
+        if attacker.kind == 'DRN':
+            return 'defender'
+        if attacker.kind == 'INF' and defender.kind == 'CMD':
+            return 'attacker'
+        return 'attacker'
+
+    def move_piece(self, from_pos: Tuple[int,int], to_pos: Tuple[int,int]) -> Optional[int]:
+        piece = self.get_piece(from_pos)
+        if not piece:
+            return None
+        target = self.get_piece(to_pos)
+        if target:
+            winner = self.combat_result(piece, target)
+            if winner == 'attacker':
+                self.board[to_pos[0]][to_pos[1]] = piece
+            else:
+                # attacker lost; mine remains etc.
+                if target.kind != 'MIN':
+                    self.board[to_pos[0]][to_pos[1]] = target
+                return None
+        else:
+            self.board[to_pos[0]][to_pos[1]] = piece
+        self.board[from_pos[0]][from_pos[1]] = None
+        if target and target.kind == 'CMD':
+            return piece.player
+        if piece.kind == 'CMD' and ((piece.player == 1 and to_pos[0] == 0) or (piece.player == 2 and to_pos[0] == BOARD_SIZE-1)):
+            return piece.player
+        return None
+
+    def check_surrender(self, opponent: int) -> bool:
+        for row in self.board:
+            for cell in row:
+                if cell and cell.player == opponent and cell.kind != 'CMD':
+                    return False
+        return True
+
+    def run(self):
+        while True:
+            self.display()
+            print(f"Player {self.turn}'s turn")
+            try:
+                from_input = input('Select piece (y x): ')
+                fy,fx = map(int, from_input.split())
+                if not in_bounds(fy,fx):
+                    print('Invalid coordinates')
+                    continue
+                piece = self.get_piece((fy,fx))
+                if not piece or piece.player != self.turn:
+                    print('No piece belonging to you there')
+                    continue
+                moves = self.valid_moves((fy,fx))
+                if not moves:
+                    print('No valid moves')
+                    continue
+                self.display(highlights=moves)
+                to_input = input('Move to (y x): ')
+                ty,tx = map(int, to_input.split())
+                if (ty,tx) not in moves:
+                    print('Invalid move')
+                    continue
+                winner = self.move_piece((fy,fx),(ty,tx))
+                if winner:
+                    self.display()
+                    print(f'Player {winner} wins!')
+                    break
+                opponent = 2 if self.turn == 1 else 1
+                if self.check_surrender(opponent):
+                    self.display()
+                    print(f'Player {self.turn} wins by surrender!')
+                    break
+                self.turn = opponent
+            except (ValueError, KeyboardInterrupt, EOFError):
+                print('\nGame interrupted.')
+                break
+
+if __name__ == '__main__':
+    Game().run()
