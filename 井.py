import tkinter as tk
from tkinter import ttk
import random
import pickle

# Q-learning parameters
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 1.0
EXPLORATION_DECAY = 0.995

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Q-learning AI")
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        self.buttons = []
        self.q_table = {}
        self.init_ui()

    def init_ui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for i in range(9):
            button = ttk.Button(frame, text=" ", command=lambda i= i: self.make_move(i))
            button.grid(row=i//3, column=i%3, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.buttons.append(button)

        for i in range(3):
            frame.rowconfigure(i, weight=1)
            frame.columnconfigure(i, weight=1)

        self.reset_button = ttk.Button(self.root, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
        for button in self.buttons:
            button.config(text=" ", state=tk.NORMAL)

    def make_move(self, index):
        if self.board[index] == ' ':
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            if self.check_winner(self.current_player):
                self.end_game(f"Player {self.current_player} wins!")
            elif ' ' not in self.board:
                self.end_game("It's a tie!")
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                if self.current_player == 'O':
                    self.ai_move()

    def end_game(self, message):
        for button in self.buttons:
            button.config(state=tk.DISABLED)
        print(message)

    def check_winner(self, player):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        return any(all(self.board[i] == player for i in condition) for condition in win_conditions)

    def ai_move(self):
        state = tuple(self.board)
        if random.uniform(0, 1) < EXPLORATION_RATE:
            action = random.choice([i for i, x in enumerate(self.board) if x == ' '])
        else:
            q_values = [self.q_table.get((state, a), 0) for a in range(9)]
            action = max(range(9), key=lambda x: q_values[x] if self.board[x] == ' ' else -float('inf'))

        self.board[action] = self.current_player
        self.buttons[action].config(text=self.current_player)
        if self.check_winner(self.current_player):
            self.end_game(f"Player {self.current_player} wins!")
            self.update_q_table(state, action, -1)
        elif ' ' not in self.board:
            self.end_game("It's a tie!")
            self.update_q_table(state, action, 0)
        else:
            self.update_q_table(state, action, 1)
            self.current_player = 'X'

    def update_q_table(self, state, action, reward):
        next_state = tuple(self.board)
        old_q_value = self.q_table.get((state, action), 0)
        future_q_values = [self.q_table.get((next_state, a), 0) for a in range(9)]
        best_future_q = max(future_q_values) if future_q_values else 0
        new_q_value = old_q_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * best_future_q - old_q_value)
        self.q_table[(state, action)] = new_q_value

        global EXPLORATION_RATE
        EXPLORATION_RATE *= EXPLORATION_DECAY

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
