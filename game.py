import pygame
import math
import copy
from board import Board
from ui import Button

MENU, PLACING, PLAYING, GAME_OVER = "MENU", "PLACING", "PLAYING", "GAME_OVER"
PLAYER1, PLAYER2 = 1, 2

class Game:
    def __init__(self, win):
        self.win = win
        self.state = MENU
        self.board = Board()
        self.current_player = PLAYER1
        self.buttons = [
            Button(150, 250, 300, 60, "Против друга", lambda: self.start_game(vs_ai=False)),
            Button(150, 350, 300, 60, "Против ИИ", lambda: self.start_game(vs_ai=True)),
        ]
        self.vs_ai = False
        self.ai_difficulty = 2
        self.placing_counter = 0  # <--- добавляем счетчик

    def start_game(self, vs_ai):
        self.vs_ai = vs_ai
        self.state = PLACING
        self.board.reset()
        self.current_player = PLAYER1
        self.placing_counter = 0  # <--- сбрасываем счетчик

    def handle_click(self, pos):
        if self.state == MENU:
            for btn in self.buttons:
                if btn.check_click(pos):
                    break
        elif self.state == PLACING:
            row, col = self.board.get_cell(pos)
            if row is not None and col is not None:
                if self.board.handle_placing(row, col):
                    self.placing_counter += 1
                    if self.placing_counter == 2:
                        self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
                        self.placing_counter = 0
                    if self.board.is_placing_complete():
                        self.state = PLAYING
        elif self.state == PLAYING:
            if self.vs_ai and self.current_player == PLAYER2:
                self.ai_move()
            else:
                success, result = self.board.handle_moving(pos)
                if success:
                    self.board.check_triples_and_capture(self.current_player)
                    if self.board.check_game_over():
                        self.state = GAME_OVER
                    else:
                        self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1

    def ai_move(self):
        best_score = -math.inf
        best_move = None
        
        possible_moves = self.board.get_all_possible_moves(PLAYER2)
        if not possible_moves:
            return
            
        for move in possible_moves:
            board_copy = copy.deepcopy(self.board)
            from_pos, to_pos = move
            
            if board_copy.apply_move(from_pos, to_pos, PLAYER2):
                score = self.minimax(board_copy, self.ai_difficulty - 1, -math.inf, math.inf, False)
                if score > best_score:
                    best_score = score
                    best_move = move
        
        if best_move:
            from_pos, to_pos = best_move
            self.board.apply_move(from_pos, to_pos, PLAYER2)
            self.board.check_triples_and_capture(PLAYER2)
            if self.board.check_game_over():
                self.state = GAME_OVER
            else:
                self.current_player = PLAYER1

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.check_game_over():
            return self.evaluate_board(board, PLAYER2)
        
        if maximizing_player:
            max_eval = -math.inf
            possible_moves = board.get_all_possible_moves(PLAYER2)
            for move in possible_moves:
                board_copy = copy.deepcopy(board)
                from_pos, to_pos = move
                if board_copy.apply_move(from_pos, to_pos, PLAYER2):
                    evaluation = self.minimax(board_copy, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, evaluation)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = math.inf
            possible_moves = board.get_all_possible_moves(PLAYER1)
            for move in possible_moves:
                board_copy = copy.deepcopy(board)
                from_pos, to_pos = move
                if board_copy.apply_move(from_pos, to_pos, PLAYER1):
                    evaluation = self.minimax(board_copy, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, evaluation)
                    beta = min(beta, evaluation)
                    if beta <= alpha:
                        break
            return min_eval

    def evaluate_board(self, board, player):
        score = 0
        player_pieces = board.count_pieces(player)
        opponent_pieces = board.count_pieces(PLAYER1 if player == PLAYER2 else PLAYER2)
        score += (player_pieces - opponent_pieces) * 10
        
        center_bonus = 0
        center_positions = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for pos in center_positions:
            if board.get_piece(pos[0], pos[1]) == player:
                center_bonus += 1
        score += center_bonus * 3
        
        isolated_penalty = 0
        for row in range(8):
            for col in range(8):
                if board.get_piece(row, col) == player:
                    if not self.has_adjacent_allies(board, row, col, player):
                        isolated_penalty += 1
        score -= isolated_penalty * 2
        
        return score

    def has_adjacent_allies(self, board, row, col, player):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board.get_piece(r, c) == player:
                    return True
        return False

    def update(self):
        self.win.fill((0, 0, 0))
        if self.state == MENU:
            for btn in self.buttons:
                btn.draw(self.win)
        else:
            self.board.draw(self.win)
            font = pygame.font.SysFont(None, 36)
            player_text = f"Ход игрока: {self.current_player}"
            text_color = (255, 0, 0) if self.current_player == PLAYER1 else (0, 0, 255)
            text_surface = font.render(player_text, True, text_color)
            self.win.blit(text_surface, (10, 10))
            
            if self.state == PLACING:
                state_text = "Размещение фишек"
            elif self.state == PLAYING:
                state_text = "Игра"
            elif self.state == GAME_OVER:
                winner = self.board.get_winner()
                state_text = f"Игра окончена! Победил: {winner}"
            else:
                state_text = ""
            
            state_surface = font.render(state_text, True, (255, 255, 255))
            self.win.blit(state_surface, (10, 50))