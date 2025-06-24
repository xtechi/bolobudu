import pygame

PLAYER1, PLAYER2 = 1, 2

class Board:
    def __init__(self):
        self.rows, self.cols = 5, 6
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.selected_piece = None
        self.valid_moves = []
        self.cell_size = 80
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.phase = "placing"
        self.placing_count = 0
        self.current_player = PLAYER1
        self.move_history = []

    def reset(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.selected_piece = None
        self.valid_moves = []
        self.phase = "placing"
        self.placing_count = 0
        self.current_player = PLAYER1
        self.move_history = []

    def get_cell(self, pos):
        x, y = pos
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return None, None
        row = y // self.cell_size
        col = x // self.cell_size
        return row, col
        
    def try_place_piece(self, row, col, player):
        if 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] == 0:
            self.grid[row][col] = player
            if self._forms_triple(row, col, player):
                self.grid[row][col] = 0
                return False
            return True
        return False

    def _forms_triple(self, row, col, player):
        """Проверяет образование тройки в любом направлении (включая диагонали)"""
        directions = [
            (0, 1),   # горизонтально
            (1, 0),   # вертикально

        ]
        for dr, dc in directions:
            count = 1
            # Проверка в одном направлении
            r, c = row + dr, col + dc
            while 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # Проверка в противоположном направлении
            r, c = row - dr, col - dc
            while 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            if count >= 3:
                return True
        return False
        
    def is_placing_complete(self):
        count = 0
        for row in self.grid:
            for cell in row:
                if cell != 0:
                    count += 1
        return count == 24  # 12 фишек × 2 игрока
        
    def handle_placing(self, row, col):
        player = self.current_player
        if self.try_place_piece(row, col, player):
            self.placing_count += 1
            if self.placing_count == 2:
                self.placing_count = 0
                self.current_player = PLAYER2 if player == PLAYER1 else PLAYER1
                if self.is_placing_complete():
                    self.phase = "moving"
        return True
        return False
    
    def get_valid_moves(self, row, col):
        """Возвращает список возможных ходов для фишки по вертикали, горизонтали и диагонали"""
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),    
        ]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == 0:
                moves.append((r, c))
        return moves
    
    def handle_moving(self, pos):
        player = self.current_player
        row, col = self.get_cell(pos)
        if row is None or col is None:
            return False, None
    
        # Выбор фишки для перемещения
        if self.grid[row][col] == player:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_valid_moves(row, col)
            return True, None

        # Перемещение фишки
        if self.selected_piece and (row, col) in self.valid_moves:
            s_row, s_col = self.selected_piece
            self.grid[s_row][s_col] = 0
            self.grid[row][col] = player
            self.selected_piece = None
            self.valid_moves = []
            self.check_triples_and_capture(player)
            self.current_player = PLAYER2 if player == PLAYER1 else PLAYER1
            return True, None

        return False, None

    def check_game_over(self):
        p1_pieces = sum(row.count(PLAYER1) for row in self.grid)
        p2_pieces = sum(row.count(PLAYER2) for row in self.grid)
        if p1_pieces < 3 or p2_pieces < 3:
            return True
        return False

    def get_winner(self):
        p1_pieces = sum(row.count(PLAYER1) for row in self.grid)
        p2_pieces = sum(row.count(PLAYER2) for row in self.grid)
        if p1_pieces < 3:
            return "Игрок 2"
        if p2_pieces < 3:
            return "Игрок 1"
        return None
        
    def get_state(self):
        return str(self.grid)
        
    def draw(self, win):
        # Рисование сетки
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.cell_size
                y = row * self.cell_size
                color = (220, 220, 220) if (row + col) % 2 == 0 else (180, 180, 180)
                pygame.draw.rect(win, color, (x, y, self.cell_size, self.cell_size))
                
                # Выделение выбранной фишки
                if self.selected_piece == (row, col):
                    pygame.draw.rect(win, (255, 255, 0), (x, y, self.cell_size, self.cell_size), 3)
                
                # Показ возможных ходов
                if (row, col) in self.valid_moves:
                    pygame.draw.circle(win, (0, 255, 0), 
                                     (x + self.cell_size//2, y + self.cell_size//2),
                                     10)
                
                # Рисование фишек
                if self.grid[row][col] == PLAYER1:
                    pygame.draw.circle(win, (255, 0, 0), 
                                     (x + self.cell_size//2, y + self.cell_size//2),
                                     self.cell_size//3)
                elif self.grid[row][col] == PLAYER2:
                    pygame.draw.circle(win, (0, 0, 255),
                                     (x + self.cell_size//2, y + self.cell_size//2),
                                     self.cell_size//3)
                    
        # Рисование линий сетки
        for i in range(self.cols + 1):
            pygame.draw.line(win, (0, 0, 0), 
                           (i * self.cell_size, 0), 
                           (i * self.cell_size, self.height))
        for i in range(self.rows + 1):
            pygame.draw.line(win, (0, 0, 0), 
                           (0, i * self.cell_size), 
                           (self.width, i * self.cell_size))

    def check_triples_and_capture(self, player):
        """Проверяет горизонтальные и вертикальные тройки и снимает примыкающие сбоку фишки противника"""
        opponent = PLAYER2 if player == PLAYER1 else PLAYER1
        directions = [
            (0, 1),   # горизонтально
            (1, 0),   # вертикально
        ]
        for dr, dc in directions:
            for row in range(self.rows):
                for col in range(self.cols):
                    # Проверяем только если в этой клетке стоит фишка игрока
                    if self.grid[row][col] != player:
                        continue
                    # Проверяем тройку: текущая + 2 в выбранном направлении
                    triple = [(row, col)]
                    for i in range(1, 3):
                        r, c = row + dr * i, col + dc * i
                        if 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == player:
                            triple.append((r, c))
                        else:
                            break
                    if len(triple) == 3:
                        # Проверяем клетки по бокам тройки
                        before_r, before_c = row - dr, col - dc
                        after_r, after_c = row + dr * 3, col + dc * 3
                        # Снимаем фишку противника перед тройкой
                        if 0 <= before_r < self.rows and 0 <= before_c < self.cols:
                            if self.grid[before_r][before_c] == opponent:
                                self.grid[before_r][before_c] = 0
                        # Снимаем фишку противника после тройки
                        if 0 <= after_r < self.rows and 0 <= after_c < self.cols:
                            if self.grid[after_r][after_c] == opponent:
                                self.grid[after_r][after_c] = 0

#вроде работает